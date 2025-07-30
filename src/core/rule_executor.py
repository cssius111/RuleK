"""
规则执行引擎
负责检查和执行游戏规则
"""
import random
from typing import Dict, List, Optional, Tuple, Any, DefaultDict, cast
from datetime import datetime
from collections import defaultdict

from ..models.rule import Rule, EffectType
from ..core.game_state import GameStateManager
from ..utils.logger import get_logger, log_game_event
from .side_effects import SideEffectManager

logger = get_logger(__name__)


class RuleContext:
    """规则执行上下文"""
    
    def __init__(self, actor: Dict, action: str, game_state: Dict):
        self.actor = actor
        self.action = action
        self.game_state = game_state
        self.timestamp = datetime.now()
        
        # 提取常用属性
        self.actor_id = actor.get("id")
        self.actor_name = actor.get("name", "未知")
        self.actor_location = actor.get("location")
        self.actor_items = actor.get("inventory", [])
        self.current_time = game_state.get("current_time", "00:00")
        
    def to_dict(self) -> Dict:
        """转换为字典供规则判定使用"""
        return {
            "actor": self.actor,
            "action": self.action,
            "actor_location": self.actor_location,
            "actor_items": self.actor_items,
            "current_time": self.current_time,
            "game_state": self.game_state
        }


class RuleExecutor:
    """规则执行器"""
    
    def __init__(self, game_manager: GameStateManager):
        self.game_manager = game_manager
        self.execution_history: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)  # 规则执行历史
        self.cooldowns: Dict[str, int] = {}  # 规则冷却时间
        self.side_effect_manager = SideEffectManager()  # 副作用管理器
        
    def check_all_rules(self, context: RuleContext) -> List[Tuple[Rule, float]]:
        """检查所有可能触发的规则"""
        triggered_rules: List[Tuple[Rule, float]] = []

        state = self.game_manager.state
        if state is None:
            return triggered_rules

        for rule_id in state.active_rules:
            # 在规则列表中查找对应的规则
            rule = None
            for r in self.game_manager.rules:
                if r.id == rule_id:
                    rule = r
                    break
            
            if not rule:
                continue
                
            # 检查规则是否可以触发
            if self.can_rule_trigger(rule, context):
                # 计算触发概率
                probability = self.calculate_trigger_probability(rule, context)
                triggered_rules.append((rule, probability))
                
        # 按概率排序
        triggered_rules.sort(key=lambda x: x[1], reverse=True)
        
        logger.debug(f"检查规则完成，{len(triggered_rules)} 条规则可能触发")
        return triggered_rules
        
    def can_rule_trigger(self, rule: Rule, context: RuleContext) -> bool:
        """检查规则是否满足触发条件"""
        # 检查规则是否激活
        if not rule.active:
            return False
            
        # 检查冷却时间
        if rule.id in self.cooldowns:
            if self.cooldowns[rule.id] > 0:
                return False
                
        # 检查动作是否匹配
        if rule.trigger.action != context.action:
            return False
            
        # 检查地点限制
        if rule.trigger.location:
            if context.actor_location not in rule.trigger.location:
                return False
                
        # 检查时间限制
        if rule.trigger.time_range:
            if not self._check_time_range(context.current_time, rule.trigger.time_range):
                return False
                
        # 检查物品需求
        if rule.requirements.items:
            for item in rule.requirements.items:
                if item not in context.actor_items:
                    return False
                    
        # 检查NPC特质需求
        if rule.requirements.actor_traits:
            for trait, requirement in rule.requirements.actor_traits.items():
                actor_value = context.actor.get(trait, 0)
                
                # 支持最小/最大值检查
                if isinstance(requirement, dict):
                    if "min" in requirement and actor_value < requirement["min"]:
                        return False
                    if "max" in requirement and actor_value > requirement["max"]:
                        return False
                else:
                    # 直接比较
                    if actor_value != requirement:
                        return False
                        
        # 检查额外条件
        for condition in rule.trigger.extra_conditions:
            if not self._check_extra_condition(condition, context):
                return False
                
        return True
        
    def _check_time_range(self, current_time: str, time_range: Dict[str, str]) -> bool:
        """检查时间是否在范围内
        
        Args:
            current_time: 当前时间字符串，格式为 "HH:MM"
            time_range: 时间范围字典，包含 "from" 和 "to" 键
            
        Returns:
            bool: 时间是否在范围内
        """
        try:
            import re

            start_time = time_range.get("from", "")
            end_time = time_range.get("to", "")

            pattern = re.compile(r"^\d{2}:\d{2}$")
            for label, t in {"current_time": current_time, "start_time": start_time, "end_time": end_time}.items():
                if not pattern.match(t):
                    logger.error(f"时间格式错误: '{t}' 不符合 HH:MM 格式")
                    return False
            
            # 使用 datetime 解析时间以确保格式正确
            current = datetime.strptime(current_time, "%H:%M")
            start = datetime.strptime(start_time, "%H:%M")
            end = datetime.strptime(end_time, "%H:%M")
            
            # 将所有时间转换为当天的时间
            today = datetime.now().date()
            current = current.replace(year=today.year, month=today.month, day=today.day)
            start = start.replace(year=today.year, month=today.month, day=today.day)
            end = end.replace(year=today.year, month=today.month, day=today.day)
            
            # 处理跨午夜的情况
            if start > end:
                # 如果开始时间大于结束时间，说明跨越了午夜
                # 例如: 23:00 到 02:00
                if current >= start:  # 当前时间在今天的范围内
                    return True
                # 将结束时间调整到第二天
                from datetime import timedelta
                end = end + timedelta(days=1)
                # 也需要检查当前时间是否在第二天的范围内
                current_tomorrow = current + timedelta(days=1)
                return current_tomorrow <= end
            else:
                # 正常情况：开始时间小于等于结束时间
                return start <= current <= end
                
        except ValueError as e:
            logger.error(f"时间格式错误: {e}. 期望格式: HH:MM")
            return False
        except Exception as e:
            logger.error(f"时间范围检查失败: {e}")
            return False
            
    def _check_extra_condition(self, condition: str, context: RuleContext) -> bool:
        """检查额外条件"""
        # 这里可以实现各种特殊条件
        condition_checks = {
            "lights_off": lambda: not context.game_state.get("lights_on", True),
            "alone": lambda: len(
                self.game_manager.get_npcs_in_location(cast(str, context.actor_location))
            ) == 1,
            "multiple_people": lambda: len(
                self.game_manager.get_npcs_in_location(cast(str, context.actor_location))
            ) > 1,
            "low_sanity": lambda: context.actor.get("sanity", 100) < 50,
            "high_fear": lambda: context.actor.get("fear", 0) > 50,
        }
        
        if condition in condition_checks:
            return condition_checks[condition]()
            
        # 未知条件默认为真
        logger.warning(f"未知的额外条件: {condition}")
        return True
        
    def calculate_trigger_probability(self, rule: Rule, context: RuleContext) -> float:
        """计算规则触发概率"""
        base_prob = rule.trigger.probability
        
        # 根据NPC状态调整概率
        modifiers = []
        
        # 恐惧值影响
        fear_level = context.actor.get("fear", 0)
        if fear_level > 50:
            modifiers.append(0.2)  # 恐惧时更容易触发
            
        # 理智值影响  
        sanity = context.actor.get("sanity", 100)
        if sanity < 50:
            modifiers.append(0.15)  # 低理智更容易触发
            
        # 好奇心影响
        curiosity = context.actor.get("curiosity", 5)
        if curiosity > 7:
            modifiers.append(0.1)  # 好奇心强更容易触发
            
        # 计算最终概率
        final_prob = base_prob + sum(modifiers)
        final_prob = max(0.0, min(1.0, final_prob))  # 限制在0-1之间
        
        return final_prob
        
    def execute_rule(self, rule: Rule, context: RuleContext) -> Dict[str, Any]:
        """执行规则效果"""
        logger.info(f"执行规则: {rule.name} 对 {context.actor_name}")
        
        # 应用规则效果
        result = rule.apply_effect(context.actor)
        
        # 更新游戏状态
        self._apply_rule_effects(rule, context, result)
        
        # 记录执行历史
        self.execution_history[rule.id].append({
            "timestamp": datetime.now().isoformat(),
            "actor": context.actor_id,
            "location": context.actor_location,
            "result": result
        })
        
        # 设置冷却时间
        if hasattr(rule, "cooldown_after_trigger"):
            self.cooldowns[rule.id] = rule.cooldown_after_trigger
            
        # 记录游戏事件
        log_game_event(
            "rule_triggered",
            rule_id=rule.id,
            rule_name=rule.name,
            actor=context.actor_name,
            effect_type=rule.effect.type.value,
            fear_gained=result.get("fear_gained", 0)
        )
        
        return result
        
    def _apply_rule_effects(self, rule: Rule, context: RuleContext, result: Dict):
        """应用规则效果到游戏状态"""
        actor_id = cast(str, context.actor_id)

        # 获得恐惧积分
        if result.get("fear_gained", 0) > 0:
            self.game_manager.add_fear_points(
                result["fear_gained"], 
                f"规则触发: {rule.name}"
            )
            
        # 处理死亡
        if result.get("target_died"):
            self.game_manager.update_npc(actor_id, {
                "alive": False,
                "hp": 0,
                "death_cause": rule.name,
                "death_turn": self.game_manager.state.turn if self.game_manager.state else 0
            })
            
        # 处理理智损失
        if result.get("sanity_loss"):
            new_sanity = max(0, context.actor.get("sanity", 100) - result["sanity_loss"])
            self.game_manager.update_npc(actor_id, {"sanity": new_sanity})
            
            # 理智归零处理
            if new_sanity <= 0:
                self.game_manager.update_npc(actor_id, {
                    "alive": False,
                    "death_cause": "精神崩溃",
                    "death_turn": self.game_manager.state.turn if self.game_manager.state else 0
                })
                
        # 处理传送效果
        if rule.effect.type == EffectType.TELEPORT:
            target_location = rule.effect.params.get("target_location", "living_room")
            self.game_manager.update_npc(actor_id, {"location": target_location})
            
        # 处理副作用
        for side_effect in result.get("side_effects", []):
            self._apply_side_effect(side_effect, context)
            
    def _apply_side_effect(self, side_effect: str, context: RuleContext):
        """应用副作用"""
        # 构建副作用上下文
        effect_context = {
            "location": context.actor_location,
            "actor": context.actor,
            "trigger_action": context.action,
            "game_turn": context.game_state.get("turn", 0)
        }
        
        # 特殊副作用的额外参数
        if side_effect == "blood_on_mirror":
            effect_context.update({
                "surface": "mirror",
                "message": "你看到了什么？"
            })
            side_effect = "blood_message"
        elif side_effect == "lights_flicker":
            side_effect = "light_flicker"
        
        # 使用副作用管理器应用副作用
        result = self.side_effect_manager.apply_effect(
            side_effect,
            self.game_manager,
            effect_context
        )
        
        if result and result.get("success"):
            logger.info(f"副作用 {side_effect} 应用成功")
            # 如果副作用产生了额外恐惧值，添加到游戏中
            if result.get("fear_bonus"):
                self.game_manager.add_fear_points(
                    result["fear_bonus"],
                    f"副作用: {side_effect}"
                )
        else:
            logger.warning(f"副作用 {side_effect} 应用失败或未找到")
            
    def _add_scene_effect(self, location: str, effect: str) -> bool:
        """添加场景效果"""
        # TODO: 接入真实场景系统
        logger.info(f"场景效果: {location} - {effect}")
        return True
        
    def _alert_nearby_npcs(self, location: str):
        """警告附近的NPC"""
        nearby_npcs = self.game_manager.get_npcs_in_location(location)
        for npc in nearby_npcs:
            self.game_manager.update_npc(npc["id"], {
                "fear": min(100, npc.get("fear", 0) + 10),
                "suspicion": min(100, npc.get("suspicion", 0) + 5)
            })
            
    def _change_room_temp(self, location: str, change: int) -> bool:
        """改变房间温度"""
        # TODO: 接入真实环境系统
        logger.info(f"温度变化: {location} {change:+d}°C")
        return True
        
    def _trigger_light_event(self, location: str) -> bool:
        """触发灯光事件"""
        # TODO: 接入真实灯光系统
        logger.info(f"灯光闪烁: {location}")
        return True
        
    def update_cooldowns(self):
        """更新所有规则的冷却时间"""
        for rule_id in list(self.cooldowns.keys()):
            self.cooldowns[rule_id] -= 1
            if self.cooldowns[rule_id] <= 0:
                del self.cooldowns[rule_id]
                
    def detect_loopholes(self, npc: Dict, rule: Rule) -> Optional[str]:
        """检测NPC是否发现规则破绽"""
        # 基于NPC的观察力和理性
        detection_chance = 0.0
        
        observation = npc.get("observation", 5) / 10
        rationality = npc.get("rationality", 5) / 10
        loophole_sense = npc.get("loophole_sense", 3) / 10
        
        # 基础发现概率
        detection_chance = (observation + rationality + loophole_sense) / 3
        
        # 如果规则被触发多次，增加发现概率
        times_triggered = len(self.execution_history.get(rule.id, []))
        detection_chance += times_triggered * 0.05
        
        # 检查每个未修补的破绽
        for loophole in rule.loopholes:
            if loophole.patched:
                continue
                
            # 根据破绽难度调整概率
            adjusted_chance = detection_chance * (11 - loophole.discovery_difficulty) / 10
            
            if random.random() < adjusted_chance:
                logger.info(f"{npc['name']} 发现了规则 '{rule.name}' 的破绽: {loophole.description}")
                return loophole.id
                
        return None
        
    def get_execution_stats(self) -> Dict[str, Any]:
        """获取规则执行统计"""
        stats: Dict[str, Any] = {
            "total_executions": sum(len(history) for history in self.execution_history.values()),
            "rules_triggered": len(self.execution_history),
            "most_triggered": None,
            "cooldowns_active": len(self.cooldowns)
        }
        
        # 找出触发最多的规则
        if self.execution_history:
            most_triggered_id = max(
                self.execution_history.keys(),
                key=lambda k: len(self.execution_history[k])
            )
            rule = next(
                (r for r in self.game_manager.rules if r.id == most_triggered_id),
                None,
            )
            if rule is not None:
                stats["most_triggered"] = {
                    "name": rule.name,
                    "count": len(self.execution_history[most_triggered_id])
                }
                
        return stats


if __name__ == "__main__":
    # 测试代码
    from ..core.game_state import GameStateManager
    from ..models.rule import Rule, TriggerCondition, RuleEffect, EffectType
    
    # 创建游戏管理器
    game_manager = GameStateManager()
    game_manager.new_game()

    assert game_manager.state is not None
    
    # 创建测试规则
    test_rule = Rule(
        id="test_rule",
        name="测试规则",
        trigger=TriggerCondition(
            action="test_action",
            probability=0.8
        ),
        effect=RuleEffect(
            type=EffectType.FEAR_GAIN,
            fear_gain=100
        )
    )
    
    game_manager.add_rule(test_rule)
    
    # 创建规则执行器
    executor = RuleExecutor(game_manager)
    
    # 创建测试上下文
    test_npc = list(game_manager.state.npcs.values())[0]
    context = RuleContext(
        actor=test_npc,
        action="test_action",
        game_state=game_manager.state.to_dict()
    )
    
    # 检查规则
    triggered = executor.check_all_rules(context)
    print(f"可触发规则数: {len(triggered)}")
    
    # 执行规则
    if triggered:
        rule, prob = triggered[0]
        if random.random() < prob:
            result = executor.execute_rule(rule, context)
            print(f"规则执行结果: {result}")
