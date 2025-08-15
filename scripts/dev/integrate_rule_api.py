#!/usr/bin/env python3
"""
更新后端API以支持完整的规则系统
"""
import os
import re

def add_rule_api_endpoints():
    """添加规则相关的API端点"""
    
    # 要添加的API端点代码
    rule_endpoints = '''
# ==================== 规则管理API ====================

@app.get("/api/rules/templates")
async def get_rule_templates():
    """获取所有规则模板"""
    try:
        # 加载规则模板
        template_file = Path("data/rule_templates.json")
        if template_file.exists():
            import json
            with open(template_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            return {"success": True, "templates": templates}
        else:
            return {"success": True, "templates": []}
    except Exception as e:
        logger.error(f"Failed to load rule templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/games/{game_id}/rules/template")
async def create_rule_from_template(game_id: str, request: Dict):
    """从模板创建规则"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        template_id = request.get("template_id")
        
        # 从rule_service创建规则
        from .services.rule_service import RuleService
        rule_service = RuleService(game_service.game_state)
        rule = rule_service.create_rule_from_template(template_id)
        
        if not rule:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # 添加到游戏状态
        game_service.game_state.add_rule(rule)
        
        return {
            "success": True,
            "rule": {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "cost": rule.cost,
                "trigger": rule.trigger.dict(),
                "effects": [e.dict() for e in rule.effects]
            },
            "remaining_fear_points": game_service.game_state.fear_points
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create rule from template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/games/{game_id}/rules/custom")
async def create_custom_rule(game_id: str, request: Dict):
    """创建自定义规则"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        from .services.rule_service import RuleService
        rule_service = RuleService(game_service.game_state)
        
        # 创建自定义规则
        rule = rule_service.create_custom_rule(request)
        
        # 添加到游戏状态
        game_service.game_state.add_rule(rule)
        
        return {
            "success": True,
            "rule": {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "cost": rule.cost,
                "trigger": rule.trigger.dict(),
                "effects": [e.dict() for e in rule.effects]
            },
            "remaining_fear_points": game_service.game_state.fear_points
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create custom rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/games/{game_id}/rules")
async def get_game_rules(game_id: str):
    """获取游戏中的所有规则"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    rules = []
    for rule in game_service.game_state.rules:
        rules.append({
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "level": getattr(rule, 'level', 1),
            "is_active": getattr(rule, 'is_active', True),
            "cooldown": getattr(rule, 'cooldown', 0)
        })
    
    return {
        "success": True,
        "rules": rules,
        "total_count": len(rules)
    }

@app.put("/api/games/{game_id}/rules/{rule_id}/toggle")
async def toggle_rule(game_id: str, rule_id: str):
    """切换规则激活状态"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        from .services.rule_service import RuleService
        rule_service = RuleService(game_service.game_state)
        is_active = rule_service.toggle_rule(rule_id)
        
        return {
            "success": True,
            "rule_id": rule_id,
            "is_active": is_active
        }
    except Exception as e:
        logger.error(f"Failed to toggle rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/games/{game_id}/rules/{rule_id}/upgrade")
async def upgrade_rule(game_id: str, rule_id: str):
    """升级规则"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        from .services.rule_service import RuleService
        rule_service = RuleService(game_service.game_state)
        rule = rule_service.upgrade_rule(rule_id)
        
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        return {
            "success": True,
            "rule": {
                "id": rule.id,
                "name": rule.name,
                "level": rule.level,
                "effects": [e.dict() for e in rule.effects]
            },
            "remaining_fear_points": game_service.game_state.fear_points
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to upgrade rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/parse-rule")
async def parse_rule_with_ai(request: Dict):
    """使用AI解析自然语言规则描述"""
    description = request.get("description", "")
    game_id = request.get("game_id")
    
    if not description:
        raise HTTPException(status_code=400, detail="Description is required")
    
    try:
        # 这里集成AI服务
        # 暂时返回模拟数据
        parsed_rule = {
            "rule_name": "AI解析的规则",
            "description": description,
            "trigger": {
                "type": "condition",
                "conditions": {},
                "probability": 0.7
            },
            "effects": [
                {
                    "type": "fear_increase",
                    "value": 40,
                    "target": "trigger_npc"
                }
            ],
            "estimated_cost": 350,
            "suggestions": [
                "建议添加更具体的触发条件",
                "可以增加冷却时间以平衡游戏性",
                "考虑添加多重效果以增加趣味性"
            ]
        }
        
        return {
            "success": True,
            **parsed_rule
        }
    except Exception as e:
        logger.error(f"Failed to parse rule with AI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 规则计算API ====================

@app.post("/api/rules/calculate-cost")
async def calculate_rule_cost(request: Dict):
    """计算规则成本"""
    try:
        from .services.rule_service import RuleService
        
        # 创建临时的RuleService实例来计算成本
        rule_service = RuleService(None)
        cost = rule_service.calculate_rule_cost(request)
        
        return {
            "success": True,
            "cost": cost,
            "breakdown": {
                "base_cost": 100,
                "effect_cost": cost - 100,
                "probability_modifier": request.get("trigger", {}).get("probability", 1.0),
                "cooldown_modifier": request.get("cooldown", 0)
            }
        }
    except Exception as e:
        logger.error(f"Failed to calculate rule cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    # 读取现有的app.py文件
    app_path = "web/backend/app.py"
    
    if not os.path.exists(app_path):
        print(f"❌ 文件不存在: {app_path}")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有规则API
    if "/api/rules/templates" in content:
        print("ℹ️ 规则API端点已存在")
        return True
    
    # 找到合适的插入位置（在health check之后）
    insert_marker = "@app.get(\"/api/health\")"
    insert_pos = content.find(insert_marker)
    
    if insert_pos == -1:
        print("⚠️ 未找到插入位置，将在文件末尾添加")
        content += "\n" + rule_endpoints
    else:
        # 找到health端点的结束位置
        next_endpoint = content.find("@app.", insert_pos + len(insert_marker))
        if next_endpoint == -1:
            next_endpoint = len(content)
        
        # 在合适的位置插入规则API
        content = content[:next_endpoint] + rule_endpoints + "\n" + content[next_endpoint:]
    
    # 写回文件
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新 {app_path} 添加规则API端点")
    return True

def create_rule_models():
    """创建规则相关的Pydantic模型"""
    models_code = '''"""
规则相关的数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class TriggerType(str, Enum):
    """触发类型枚举"""
    ACTION = "action"
    TIME = "time"
    LOCATION = "location"
    ITEM = "item"
    CONDITION = "condition"
    RANDOM = "random"

class EffectType(str, Enum):
    """效果类型枚举"""
    INSTANT_DEATH = "instant_death"
    FEAR_INCREASE = "fear_increase"
    SANITY_DECREASE = "sanity_decrease"
    TELEPORT = "teleport"
    ITEM_GRANT = "item_grant"
    CONTINUOUS_DAMAGE = "continuous_damage"

class RuleTrigger(BaseModel):
    """规则触发条件"""
    type: TriggerType
    conditions: Dict[str, Any] = {}
    probability: float = Field(default=1.0, ge=0.0, le=1.0)

class RuleEffect(BaseModel):
    """规则效果"""
    type: EffectType
    value: Optional[int] = None
    target: Optional[str] = None
    duration: Optional[int] = None
    params: Dict[str, Any] = {}

class RuleModel(BaseModel):
    """规则模型"""
    id: str
    name: str
    description: str
    cost: int
    trigger: RuleTrigger
    effects: List[RuleEffect]
    cooldown: int = 0
    is_active: bool = True
    level: int = 1
    category: Optional[str] = None

class RuleTemplateRequest(BaseModel):
    """从模板创建规则请求"""
    template_id: str

class CustomRuleRequest(BaseModel):
    """创建自定义规则请求"""
    name: str
    description: str
    trigger: RuleTrigger
    effects: List[RuleEffect]
    cooldown: int = 0

class AIRuleParseRequest(BaseModel):
    """AI解析规则请求"""
    description: str
    game_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class RuleUpgradeRequest(BaseModel):
    """规则升级请求"""
    rule_id: str

class RuleCostCalculationRequest(BaseModel):
    """规则成本计算请求"""
    trigger: RuleTrigger
    effects: List[RuleEffect]
    cooldown: int = 0
'''
    
    output_path = "web/backend/models/rule_models.py"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(models_code)
    
    print(f"✅ 创建规则模型文件: {output_path}")
    return output_path

def create_frontend_rule_store():
    """创建前端规则Store"""
    store_code = '''import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import { useGameStore } from './game'
import type { Rule, RuleTemplate, RuleEffect } from '@/types/rule'

export const useRulesStore = defineStore('rules', () => {
  // 状态
  const rules = ref<Rule[]>([])
  const templates = ref<RuleTemplate[]>([])
  const selectedTemplate = ref<RuleTemplate | null>(null)
  const isCreating = ref(false)
  const isLoading = ref(false)
  
  // 计算属性
  const activeRules = computed(() => 
    rules.value.filter(r => r.is_active)
  )
  
  const totalRuleCost = computed(() =>
    rules.value.reduce((sum, rule) => sum + rule.cost, 0)
  )
  
  const canCreateRule = computed(() => {
    const gameStore = useGameStore()
    return (cost: number) => gameStore.gameState?.fear_points >= cost
  })
  
  // 方法
  async function loadTemplates() {
    isLoading.value = true
    try {
      const response = await api.get('/api/rules/templates')
      templates.value = response.data.templates
      return templates.value
    } catch (error) {
      console.error('Failed to load templates:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function loadGameRules(gameId: string) {
    isLoading.value = true
    try {
      const response = await api.get(`/api/games/${gameId}/rules`)
      rules.value = response.data.rules
      return rules.value
    } catch (error) {
      console.error('Failed to load game rules:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function createRuleFromTemplate(gameId: string, templateId: string) {
    isCreating.value = true
    try {
      const response = await api.post(`/api/games/${gameId}/rules/template`, {
        template_id: templateId
      })
      
      if (response.data.success) {
        rules.value.push(response.data.rule)
        
        // 更新游戏状态中的恐惧点数
        const gameStore = useGameStore()
        if (gameStore.gameState) {
          gameStore.gameState.fear_points = response.data.remaining_fear_points
        }
        
        return response.data.rule
      }
      throw new Error('Failed to create rule')
    } catch (error) {
      console.error('Failed to create rule from template:', error)
      throw error
    } finally {
      isCreating.value = false
    }
  }
  
  async function createCustomRule(gameId: string, ruleData: any) {
    isCreating.value = true
    try {
      const response = await api.post(`/api/games/${gameId}/rules/custom`, ruleData)
      
      if (response.data.success) {
        rules.value.push(response.data.rule)
        
        // 更新游戏状态中的恐惧点数
        const gameStore = useGameStore()
        if (gameStore.gameState) {
          gameStore.gameState.fear_points = response.data.remaining_fear_points
        }
        
        return response.data.rule
      }
      throw new Error('Failed to create custom rule')
    } catch (error) {
      console.error('Failed to create custom rule:', error)
      throw error
    } finally {
      isCreating.value = false
    }
  }
  
  async function parseRuleWithAI(description: string, gameId?: string) {
    isLoading.value = true
    try {
      const response = await api.post('/api/ai/parse-rule', {
        description,
        game_id: gameId
      })
      
      return response.data
    } catch (error) {
      console.error('Failed to parse rule with AI:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function toggleRule(gameId: string, ruleId: string) {
    try {
      const response = await api.put(`/api/games/${gameId}/rules/${ruleId}/toggle`)
      
      if (response.data.success) {
        const rule = rules.value.find(r => r.id === ruleId)
        if (rule) {
          rule.is_active = response.data.is_active
        }
        return response.data.is_active
      }
      throw new Error('Failed to toggle rule')
    } catch (error) {
      console.error('Failed to toggle rule:', error)
      throw error
    }
  }
  
  async function upgradeRule(gameId: string, ruleId: string) {
    isLoading.value = true
    try {
      const response = await api.post(`/api/games/${gameId}/rules/${ruleId}/upgrade`)
      
      if (response.data.success) {
        const index = rules.value.findIndex(r => r.id === ruleId)
        if (index !== -1) {
          rules.value[index] = { ...rules.value[index], ...response.data.rule }
        }
        
        // 更新恐惧点数
        const gameStore = useGameStore()
        if (gameStore.gameState) {
          gameStore.gameState.fear_points = response.data.remaining_fear_points
        }
        
        return response.data.rule
      }
      throw new Error('Failed to upgrade rule')
    } catch (error) {
      console.error('Failed to upgrade rule:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function calculateRuleCost(ruleData: any) {
    try {
      const response = await api.post('/api/rules/calculate-cost', ruleData)
      return response.data.cost
    } catch (error) {
      console.error('Failed to calculate rule cost:', error)
      return 100 // 默认成本
    }
  }
  
  function clearRules() {
    rules.value = []
    selectedTemplate.value = null
  }
  
  return {
    // 状态
    rules,
    templates,
    selectedTemplate,
    isCreating,
    isLoading,
    
    // 计算属性
    activeRules,
    totalRuleCost,
    canCreateRule,
    
    // 方法
    loadTemplates,
    loadGameRules,
    createRuleFromTemplate,
    createCustomRule,
    parseRuleWithAI,
    toggleRule,
    upgradeRule,
    calculateRuleCost,
    clearRules
  }
})
'''
    
    output_path = "web/frontend/src/stores/rules.ts"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(store_code)
    
    print(f"✅ 创建前端规则Store: {output_path}")
    return output_path

def create_rule_types():
    """创建TypeScript类型定义"""
    types_code = '''/**
 * 规则系统类型定义
 */

export type TriggerType = 'action' | 'time' | 'location' | 'item' | 'condition' | 'random'

export type EffectType = 
  | 'instant_death'
  | 'fear_increase'
  | 'sanity_decrease'
  | 'teleport'
  | 'item_grant'
  | 'continuous_damage'

export interface RuleTrigger {
  type: TriggerType
  conditions: Record<string, any>
  probability: number
}

export interface RuleEffect {
  type: EffectType
  value?: number
  target?: string
  duration?: number
  params?: Record<string, any>
}

export interface Rule {
  id: string
  name: string
  description: string
  cost: number
  trigger: RuleTrigger
  effects: RuleEffect[]
  cooldown: number
  is_active: boolean
  level: number
  category?: string
}

export interface RuleTemplate extends Rule {
  difficulty: 'easy' | 'normal' | 'hard'
}

export interface RuleCreationRequest {
  name: string
  description: string
  trigger: RuleTrigger
  effects: RuleEffect[]
  cooldown?: number
}

export interface AIRuleParseResult {
  rule_name: string
  description: string
  trigger: RuleTrigger
  effects: RuleEffect[]
  estimated_cost: number
  suggestions: string[]
}

export interface RuleCostBreakdown {
  base_cost: number
  effect_cost: number
  probability_modifier: number
  cooldown_modifier: number
}
'''
    
    output_path = "web/frontend/src/types/rule.ts"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(types_code)
    
    print(f"✅ 创建TypeScript类型定义: {output_path}")
    return output_path

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 RuleK 规则系统API集成")
    print("=" * 60)
    
    print("\n1️⃣ 更新后端API端点...")
    add_rule_api_endpoints()
    
    print("\n2️⃣ 创建规则数据模型...")
    create_rule_models()
    
    print("\n3️⃣ 创建前端Store...")
    create_frontend_rule_store()
    
    print("\n4️⃣ 创建TypeScript类型...")
    create_rule_types()
    
    print("\n" + "=" * 60)
    print("✅ API集成完成!")
    print("\n需要手动完成的步骤:")
    print("1. 在 web/backend/models/__init__.py 中导出新模型")
    print("2. 重启后端服务器")
    print("3. 在前端组件中使用新的Store")
    print("4. 运行测试验证功能")

if __name__ == "__main__":
    main()
