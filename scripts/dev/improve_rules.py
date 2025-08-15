"""
RuleK规则系统改进脚本
自动创建和更新规则相关文件
"""
import os
import json

def create_rule_templates():
    """创建规则模板数据文件"""
    templates = [
        {
            "id": "midnight_mirror",
            "name": "午夜镜像", 
            "description": "午夜12点照镜子会看到恐怖的景象，NPC恐惧值大幅增加",
            "cost": 300,
            "category": "时间触发",
            "difficulty": "normal",
            "trigger": {
                "type": "time",
                "conditions": {
                    "time": "00:00",
                    "action": "look_mirror"
                },
                "probability": 0.8
            },
            "effects": [
                {
                    "type": "fear_increase",
                    "value": 50,
                    "target": "trigger_npc"
                }
            ],
            "cooldown": 3
        },
        {
            "id": "corridor_whisper",
            "name": "走廊低语",
            "description": "晚上10点后在走廊会听到诡异的低语声，理智值下降",
            "cost": 200,
            "category": "地点触发",
            "difficulty": "easy",
            "trigger": {
                "type": "location",
                "conditions": {
                    "location": "corridor",
                    "time_range": "22:00-06:00"
                },
                "probability": 0.6
            },
            "effects": [
                {
                    "type": "sanity_decrease",
                    "value": 20,
                    "target": "trigger_npc"
                },
                {
                    "type": "fear_increase",
                    "value": 30,
                    "target": "trigger_npc"
                }
            ],
            "cooldown": 2
        },
        {
            "id": "shadow_follower",
            "name": "影子跟随者",
            "description": "独自一人时，影子会做出不同的动作，令人毛骨悚然",
            "cost": 400,
            "category": "条件触发",
            "difficulty": "hard",
            "trigger": {
                "type": "condition",
                "conditions": {
                    "alone": True,
                    "light_level": "dim"
                },
                "probability": 0.7
            },
            "effects": [
                {
                    "type": "sanity_decrease",
                    "value": 30,
                    "target": "trigger_npc"
                },
                {
                    "type": "fear_increase",
                    "value": 40,
                    "target": "all_witness"
                }
            ],
            "cooldown": 4
        },
        {
            "id": "door_knock",
            "name": "敲门声",
            "description": "深夜会听到房门被敲响，但门外没有人",
            "cost": 250,
            "category": "时间触发",
            "difficulty": "easy",
            "trigger": {
                "type": "time",
                "conditions": {
                    "time_range": "02:00-04:00",
                    "location_type": "room"
                },
                "probability": 0.3
            },
            "effects": [
                {
                    "type": "fear_increase",
                    "value": 40,
                    "target": "random_npc"
                }
            ],
            "cooldown": 1
        },
        {
            "id": "cursed_item",
            "name": "诅咒物品",
            "description": "拿起特定物品会触发诅咒，持续掉血",
            "cost": 500,
            "category": "物品触发",
            "difficulty": "hard",
            "trigger": {
                "type": "item",
                "conditions": {
                    "item_type": "cursed",
                    "action": "pick_up"
                },
                "probability": 1.0
            },
            "effects": [
                {
                    "type": "continuous_damage",
                    "value": 10,
                    "duration": 5,
                    "target": "trigger_npc"
                }
            ],
            "cooldown": 0
        },
        {
            "id": "blood_writing",
            "name": "血字警告",
            "description": "墙上出现血字，看到的NPC理智大幅下降",
            "cost": 350,
            "category": "随机触发",
            "difficulty": "normal",
            "trigger": {
                "type": "random",
                "conditions": {
                    "min_fear_total": 200
                },
                "probability": 0.2
            },
            "effects": [
                {
                    "type": "sanity_decrease",
                    "value": 50,
                    "target": "all_in_location"
                },
                {
                    "type": "fear_increase",
                    "value": 30,
                    "target": "all_in_location"
                }
            ],
            "cooldown": 5
        }
    ]
    
    # 保存为JSON文件
    output_path = "data/rule_templates.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 创建规则模板文件: {output_path}")
    print(f"   包含 {len(templates)} 个规则模板")
    
    return templates

def create_rule_service():
    """创建规则服务代码"""
    service_code = '''"""
规则服务模块
处理规则创建、验证和执行
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, time
import random
import json
from pathlib import Path

from src.models.game_state import GameState
from src.models.rule import Rule, RuleTrigger, RuleEffect
from src.core.npc import NPC

class RuleService:
    """规则服务类"""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.templates = self._load_templates()
        self.active_rules: List[Rule] = []
        self.cooldowns: Dict[str, int] = {}
    
    def _load_templates(self) -> List[Dict]:
        """加载规则模板"""
        template_file = Path("data/rule_templates.json")
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def create_rule_from_template(self, template_id: str) -> Optional[Rule]:
        """从模板创建规则"""
        template = next((t for t in self.templates if t['id'] == template_id), None)
        if not template:
            return None
        
        # 检查恐惧点数
        if self.game_state.fear_points < template['cost']:
            raise ValueError(f"恐惧点数不足: 需要 {template['cost']}, 当前 {self.game_state.fear_points}")
        
        # 扣除恐惧点数
        self.game_state.fear_points -= template['cost']
        
        # 创建规则对象
        rule = Rule(
            id=f"rule_{len(self.active_rules)}_{template_id}",
            name=template['name'],
            description=template['description'],
            cost=template['cost'],
            trigger=RuleTrigger(**template['trigger']),
            effects=[RuleEffect(**e) for e in template['effects']],
            cooldown=template.get('cooldown', 0),
            is_active=True,
            level=1
        )
        
        self.active_rules.append(rule)
        return rule
    
    def create_custom_rule(self, rule_data: Dict[str, Any]) -> Rule:
        """创建自定义规则"""
        # 计算成本
        cost = self.calculate_rule_cost(rule_data)
        
        # 检查恐惧点数
        if self.game_state.fear_points < cost:
            raise ValueError(f"恐惧点数不足: 需要 {cost}, 当前 {self.game_state.fear_points}")
        
        # 扣除恐惧点数
        self.game_state.fear_points -= cost
        
        # 创建规则
        rule = Rule(
            id=f"rule_custom_{len(self.active_rules)}",
            name=rule_data['name'],
            description=rule_data['description'],
            cost=cost,
            trigger=RuleTrigger(**rule_data['trigger']),
            effects=[RuleEffect(**e) for e in rule_data['effects']],
            cooldown=rule_data.get('cooldown', 0),
            is_active=True,
            level=1
        )
        
        self.active_rules.append(rule)
        return rule
    
    def calculate_rule_cost(self, rule_data: Dict[str, Any]) -> int:
        """计算规则成本"""
        base_cost = 100
        
        # 根据效果类型增加成本
        for effect in rule_data.get('effects', []):
            effect_type = effect.get('type')
            if effect_type == 'instant_death':
                base_cost += 500
            elif effect_type == 'fear_increase':
                base_cost += effect.get('value', 0) * 2
            elif effect_type == 'sanity_decrease':
                base_cost += abs(effect.get('value', 0)) * 3
            elif effect_type == 'teleport':
                base_cost += 200
            elif effect_type == 'continuous_damage':
                base_cost += effect.get('value', 0) * effect.get('duration', 1) * 2
        
        # 根据触发概率调整
        probability = rule_data.get('trigger', {}).get('probability', 1.0)
        if probability < 1.0:
            base_cost = int(base_cost * (1.5 - probability * 0.5))
        
        # 根据冷却时间调整
        cooldown = rule_data.get('cooldown', 0)
        if cooldown > 0:
            base_cost = int(base_cost * (1.0 - cooldown * 0.05))
        
        return max(base_cost, 50)  # 最低成本50
    
    def check_rule_triggers(self, event: Dict[str, Any]) -> List[Rule]:
        """检查哪些规则被触发"""
        triggered_rules = []
        
        for rule in self.active_rules:
            if not rule.is_active:
                continue
            
            # 检查冷却
            if rule.id in self.cooldowns and self.cooldowns[rule.id] > 0:
                continue
            
            # 检查触发条件
            if self._check_trigger_condition(rule.trigger, event):
                # 检查概率
                if random.random() <= rule.trigger.probability:
                    triggered_rules.append(rule)
                    # 设置冷却
                    if rule.cooldown > 0:
                        self.cooldowns[rule.id] = rule.cooldown
        
        return triggered_rules
    
    def _check_trigger_condition(self, trigger: RuleTrigger, event: Dict[str, Any]) -> bool:
        """检查触发条件是否满足"""
        if trigger.type != event.get('type'):
            return False
        
        conditions = trigger.conditions
        
        # 检查时间条件
        if 'time' in conditions:
            current_time = datetime.now().strftime("%H:%M")
            if conditions['time'] != current_time:
                return False
        
        if 'time_range' in conditions:
            start, end = conditions['time_range'].split('-')
            current = datetime.now().time()
            start_time = datetime.strptime(start, "%H:%M").time()
            end_time = datetime.strptime(end, "%H:%M").time()
            
            if start_time <= end_time:
                if not (start_time <= current <= end_time):
                    return False
            else:  # 跨午夜
                if not (current >= start_time or current <= end_time):
                    return False
        
        # 检查地点条件
        if 'location' in conditions:
            if event.get('location') != conditions['location']:
                return False
        
        # 检查动作条件
        if 'action' in conditions:
            if event.get('action') != conditions['action']:
                return False
        
        # 检查其他条件
        for key, value in conditions.items():
            if key not in ['time', 'time_range', 'location', 'action']:
                if event.get(key) != value:
                    return False
        
        return True
    
    def execute_rule_effects(self, rule: Rule, trigger_npc: Optional[NPC] = None) -> Dict[str, Any]:
        """执行规则效果"""
        results = {
            'rule_name': rule.name,
            'effects': [],
            'messages': []
        }
        
        for effect in rule.effects:
            result = self._apply_effect(effect, trigger_npc)
            results['effects'].append(result)
            if result.get('message'):
                results['messages'].append(result['message'])
        
        return results
    
    def _apply_effect(self, effect: RuleEffect, trigger_npc: Optional[NPC]) -> Dict[str, Any]:
        """应用单个效果"""
        result = {
            'type': effect.type,
            'target': effect.target,
            'success': False
        }
        
        # 确定目标NPC
        target_npcs = self._get_target_npcs(effect.target, trigger_npc)
        
        for npc in target_npcs:
            if effect.type == 'fear_increase':
                npc.fear = min(100, npc.fear + effect.value)
                result['success'] = True
                result['message'] = f"{npc.name}的恐惧值增加了{effect.value}"
            
            elif effect.type == 'sanity_decrease':
                npc.sanity = max(0, npc.sanity - abs(effect.value))
                result['success'] = True
                result['message'] = f"{npc.name}的理智值减少了{abs(effect.value)}"
            
            elif effect.type == 'instant_death':
                npc.is_alive = False
                npc.hp = 0
                result['success'] = True
                result['message'] = f"{npc.name}被规则杀死了！"
            
            elif effect.type == 'teleport':
                old_location = npc.location
                npc.location = effect.params.get('destination', 'unknown')
                result['success'] = True
                result['message'] = f"{npc.name}从{old_location}被传送到了{npc.location}"
        
        return result
    
    def _get_target_npcs(self, target: str, trigger_npc: Optional[NPC]) -> List[NPC]:
        """获取效果目标NPC列表"""
        npcs = []
        
        if target == 'trigger_npc' and trigger_npc:
            npcs = [trigger_npc]
        elif target == 'random_npc':
            alive_npcs = [npc for npc in self.game_state.npcs if npc.is_alive]
            if alive_npcs:
                npcs = [random.choice(alive_npcs)]
        elif target == 'all_npcs':
            npcs = [npc for npc in self.game_state.npcs if npc.is_alive]
        elif target == 'all_in_location' and trigger_npc:
            location = trigger_npc.location
            npcs = [npc for npc in self.game_state.npcs 
                   if npc.is_alive and npc.location == location]
        
        return npcs
    
    def update_cooldowns(self):
        """更新冷却时间"""
        for rule_id in list(self.cooldowns.keys()):
            self.cooldowns[rule_id] -= 1
            if self.cooldowns[rule_id] <= 0:
                del self.cooldowns[rule_id]
    
    def get_active_rules(self) -> List[Rule]:
        """获取所有激活的规则"""
        return [rule for rule in self.active_rules if rule.is_active]
    
    def toggle_rule(self, rule_id: str) -> bool:
        """切换规则激活状态"""
        rule = next((r for r in self.active_rules if r.id == rule_id), None)
        if rule:
            rule.is_active = not rule.is_active
            return rule.is_active
        return False
    
    def upgrade_rule(self, rule_id: str) -> Optional[Rule]:
        """升级规则"""
        rule = next((r for r in self.active_rules if r.id == rule_id), None)
        if not rule:
            return None
        
        # 计算升级成本
        upgrade_cost = rule.cost * rule.level
        
        if self.game_state.fear_points < upgrade_cost:
            raise ValueError(f"恐惧点数不足: 需要 {upgrade_cost}")
        
        # 扣除恐惧点数
        self.game_state.fear_points -= upgrade_cost
        
        # 升级规则
        rule.level += 1
        
        # 增强效果
        for effect in rule.effects:
            if hasattr(effect, 'value'):
                effect.value = int(effect.value * 1.5)
        
        return rule
'''
    
    output_path = "web/backend/services/rule_service.py"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(service_code)
    
    print(f"✅ 创建规则服务文件: {output_path}")
    
    return output_path

def create_frontend_rule_components():
    """创建前端规则组件"""
    
    # RuleTemplateSelector.vue
    template_selector = '''<template>
  <div class="rule-template-selector">
    <n-card title="选择规则模板" :bordered="false">
      <n-space vertical>
        <n-input
          v-model:value="searchText"
          placeholder="搜索规则模板..."
          clearable
        >
          <template #prefix>
            <n-icon :component="Search" />
          </template>
        </n-input>
        
        <n-tabs v-model:value="selectedCategory">
          <n-tab-pane name="all" tab="全部" />
          <n-tab-pane name="时间触发" tab="时间触发" />
          <n-tab-pane name="地点触发" tab="地点触发" />
          <n-tab-pane name="条件触发" tab="条件触发" />
          <n-tab-pane name="物品触发" tab="物品触发" />
        </n-tabs>
        
        <div class="template-grid">
          <n-card
            v-for="template in filteredTemplates"
            :key="template.id"
            :title="template.name"
            hoverable
            :class="{ selected: selectedTemplate?.id === template.id }"
            @click="selectTemplate(template)"
          >
            <template #header-extra>
              <n-tag :type="getDifficultyType(template.difficulty)">
                {{ template.difficulty }}
              </n-tag>
            </template>
            
            <n-space vertical>
              <n-text>{{ template.description }}</n-text>
              <n-space>
                <n-tag type="warning">
                  <n-icon :component="Coins" />
                  {{ template.cost }} 恐惧点
                </n-tag>
                <n-tag type="info">
                  冷却: {{ template.cooldown }}回合
                </n-tag>
              </n-space>
            </n-space>
          </n-card>
        </div>
        
        <div v-if="selectedTemplate" class="template-preview">
          <n-divider />
          <h4>预览: {{ selectedTemplate.name }}</h4>
          <n-descriptions :column="2">
            <n-descriptions-item label="类型">
              {{ selectedTemplate.trigger.type }}
            </n-descriptions-item>
            <n-descriptions-item label="触发概率">
              {{ (selectedTemplate.trigger.probability * 100).toFixed(0) }}%
            </n-descriptions-item>
            <n-descriptions-item label="效果数量">
              {{ selectedTemplate.effects.length }}
            </n-descriptions-item>
            <n-descriptions-item label="成本">
              {{ selectedTemplate.cost }} 恐惧点
            </n-descriptions-item>
          </n-descriptions>
        </div>
      </n-space>
      
      <template #footer>
        <n-space justify="end">
          <n-button @click="$emit('cancel')">取消</n-button>
          <n-button
            type="primary"
            :disabled="!selectedTemplate || !canAfford"
            @click="confirmSelection"
          >
            创建规则 ({{ selectedTemplate?.cost || 0 }} 恐惧点)
          </n-button>
        </n-space>
      </template>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NCard, NSpace, NInput, NIcon, NTabs, NTabPane, NTag, NDivider, NDescriptions, NDescriptionsItem, NButton } from 'naive-ui'
import { Search, Coins } from '@vicons/tabler'
import { useGameStore } from '@/stores/game'
import { useRulesStore } from '@/stores/rules'

const emit = defineEmits(['select', 'cancel'])

const gameStore = useGameStore()
const rulesStore = useRulesStore()

const searchText = ref('')
const selectedCategory = ref('all')
const selectedTemplate = ref(null)

const filteredTemplates = computed(() => {
  let templates = rulesStore.templates
  
  // 按类别筛选
  if (selectedCategory.value !== 'all') {
    templates = templates.filter(t => t.category === selectedCategory.value)
  }
  
  // 按搜索文本筛选
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    templates = templates.filter(t => 
      t.name.toLowerCase().includes(search) ||
      t.description.toLowerCase().includes(search)
    )
  }
  
  return templates
})

const canAfford = computed(() => {
  if (!selectedTemplate.value) return false
  return gameStore.fearPoints >= selectedTemplate.value.cost
})

function getDifficultyType(difficulty: string) {
  switch (difficulty) {
    case 'easy': return 'success'
    case 'normal': return 'warning'
    case 'hard': return 'error'
    default: return 'default'
  }
}

function selectTemplate(template: any) {
  selectedTemplate.value = template
}

function confirmSelection() {
  if (selectedTemplate.value && canAfford.value) {
    emit('select', selectedTemplate.value)
  }
}

onMounted(() => {
  rulesStore.loadTemplates()
})
</script>

<style scoped>
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin: 16px 0;
}

.template-grid .n-card {
  cursor: pointer;
  transition: all 0.3s;
}

.template-grid .n-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.template-grid .n-card.selected {
  border-color: var(--n-color-primary);
  background: var(--n-color-primary-lighter);
}

.template-preview {
  padding: 16px;
  background: var(--n-color-modal);
  border-radius: 8px;
}
</style>
'''
    
    output_path = "web/frontend/src/components/game/RuleTemplateSelector.vue"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template_selector)
    
    print(f"✅ 创建前端组件: {output_path}")
    
    return output_path

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 RuleK 规则系统改进工具")
    print("=" * 60)
    
    print("\n1️⃣ 创建规则模板数据...")
    create_rule_templates()
    
    print("\n2️⃣ 创建规则服务...")
    create_rule_service()
    
    print("\n3️⃣ 创建前端组件...")
    create_frontend_rule_components()
    
    print("\n" + "=" * 60)
    print("✅ 规则系统改进完成!")
    print("\n下一步:")
    print("1. 重启服务器查看效果")
    print("2. 运行测试验证功能")
    print("3. 在浏览器中测试规则创建")

if __name__ == "__main__":
    main()
