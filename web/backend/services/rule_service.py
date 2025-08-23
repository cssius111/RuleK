"""
规则服务模块
处理规则创建、验证和执行
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, time
import random
import json
from pathlib import Path

from src.core.game_state import GameState
from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType
from src.models.npc import NPC

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
            trigger=TriggerCondition(**template['trigger']),
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
            trigger=TriggerCondition(**rule_data['trigger']),
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
    
    def _check_trigger_condition(self, trigger: TriggerCondition, event: Dict[str, Any]) -> bool:
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
