# -*- coding: utf-8 -*-
"""
AI回合管线
负责协调AI生成的对话、行动和叙事
"""
from __future__ import annotations
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio

from src.api.deepseek_client import DeepSeekClient
from src.api.schemas import (
    TurnPlan, PlannedAction, DialogueTurn, 
    NPCState, SceneContext, RuleEvalResult
)
from typing import TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from src.models.event import Event, EventType
    from src.models.npc import NPC
    from src.models.rule import Rule

# 临时事件类型定义（如果主模块不可用）
class EventType(enum.Enum):
    """事件类型枚举"""
    NPC_DIALOGUE = "npc_dialogue"
    NPC_ACTION = "npc_action"
    RULE_TRIGGERED = "rule_triggered"
    NPC_DEATH = "npc_death"
    ITEM_FOUND = "item_found"
    ITEM_USED = "item_used"
    TURN_SUMMARY = "turn_summary"
    ACTION_FAILED = "action_failed"
    CLUE_FOUND = "clue_found"
    NARRATIVE = "narrative"

# 临时事件类（如果主模块不可用）
class Event:
    """事件数据类"""
    def __init__(self, type: EventType, description: str, turn: int, 
                 timestamp: Optional[datetime] = None, metadata: Optional[Dict] = None):
        self.type = type
        self.description = description
        self.turn = turn
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value if hasattr(self.type, 'value') else str(self.type),
            "description": self.description,
            "turn": self.turn,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata
        }

logger = logging.getLogger(__name__)


class AITurnPipeline:
    """AI驱动的回合管线"""
    
    def __init__(self, game_mgr: Any, ds_client: DeepSeekClient):
        """
        初始化AI回合管线
        
        Args:
            game_mgr: 游戏状态管理器
            ds_client: DeepSeek客户端
        """
        self.game_mgr = game_mgr
        self.ds_client = ds_client
        self._action_handlers = self._init_action_handlers()
        
    def _init_action_handlers(self) -> Dict[str, Any]:
        """初始化行动处理器映射"""
        return {
            "move": self._handle_move,
            "search": self._handle_search,
            "talk": self._handle_talk,
            "use_item": self._handle_use_item,
            "wait": self._handle_wait,
            "defend": self._handle_defend,
            "investigate": self._handle_investigate,
            "hide": self._handle_hide,
            "run": self._handle_run,
            "custom": self._handle_custom
        }
    
    async def run_turn_ai(self, force_dialogue: bool = True) -> TurnPlan:
        """
        执行AI驱动的回合
        
        Args:
            force_dialogue: 是否强制生成对话
            
        Returns:
            TurnPlan: 包含对话和行动的回合计划
        """
        try:
            logger.info("开始执行AI回合")
            state = self.game_mgr.state
            
            # 准备数据
            npc_states = self._prepare_npc_states()
            scene_context = self._prepare_scene_context()
            available_places = self._get_available_places()
            
            # 生成回合计划
            plan = await self.ds_client.generate_turn_plan(
                npc_states=npc_states,
                scene_context=scene_context,
                available_places=available_places,
                time_of_day=state.time_of_day,
                min_dialogue=1 if force_dialogue else 0
            )
            
            # 记录生成的计划
            logger.info(f"AI生成了{len(plan.dialogue)}条对话，{len(plan.actions)}个行动")
            
            # 处理对话
            await self._process_dialogues(plan.dialogue)
            
            # 验证并执行行动
            executed_actions = await self._process_actions(plan.actions)
            
            # 更新回合总结
            if plan.turn_summary:
                self._log_event(
                    plan.turn_summary,
                    EventType.TURN_SUMMARY,
                    metadata={"atmosphere": plan.atmosphere}
                )
            
            # 触发回合后处理
            await self._post_turn_processing(executed_actions)
            
            return plan
            
        except Exception as e:
            logger.error(f"AI回合执行失败: {str(e)}", exc_info=True)
            # 返回空计划
            return TurnPlan(dialogue=[], actions=[])
    
    def _prepare_npc_states(self) -> List[Dict[str, Any]]:
        """准备NPC状态数据"""
        # 使用游戏管理器提供的方法获取NPC状态
        return self.game_mgr.get_npc_states_for_ai()
    
    def _prepare_scene_context(self) -> Dict[str, Any]:
        """准备场景上下文"""
        # 使用游戏管理器提供的方法获取场景上下文
        context = self.game_mgr.get_scene_context_for_ai()
        
        # 添加额外的上下文信息
        context["weather"] = self._get_weather_condition()
        
        return context
    
    def _get_available_places(self) -> List[str]:
        """获取可访问的地点列表"""
        # 简化版本：返回一些默认地点
        # TODO: 从游戏状态中获取实际地点
        default_locations = ["客厅", "卧室", "厨房", "浴室", "走廊", "地下室"]
        
        # 如果游戏管理器有地点信息，使用它
        if hasattr(self.game_mgr.state, 'locations') and self.game_mgr.state.locations:
            return list(self.game_mgr.state.locations.keys())
        
        return default_locations
    
    async def _process_dialogues(self, dialogues: List[DialogueTurn]):
        """处理对话列表"""
        for dialogue in dialogues:
            # 验证说话者存在
            npc = self._find_npc(dialogue.speaker)
            if not npc:
                logger.warning(f"找不到说话者: {dialogue.speaker}")
                continue
            
            # 获取NPC位置（适配字典和对象格式）
            location = npc.get("location", "未知") if isinstance(npc, dict) else getattr(npc, "location", "未知")
            
            # 记录对话事件
            event = Event(
                type=EventType.NPC_DIALOGUE,
                description=f"{dialogue.speaker}: {dialogue.text}",
                turn=self.game_mgr.state.turn_count if self.game_mgr.state else 0,
                timestamp=datetime.now(),
                metadata={
                    "speaker": dialogue.speaker,
                    "text": dialogue.text,
                    "emotion": dialogue.emotion,
                    "location": location
                }
            )
            self.game_mgr.state.events_history.append(event)
            
            # 对话可能触发规则
            await self._check_dialogue_triggers(npc, dialogue.text)
    
    async def _process_actions(self, actions: List[PlannedAction]) -> List[PlannedAction]:
        """处理行动列表"""
        executed_actions = []
        
        # 按优先级排序
        sorted_actions = sorted(actions, key=lambda a: a.priority or 1, reverse=True)
        
        for action in sorted_actions:
            # 验证行动合法性
            validation_result = self._validate_action(action)
            if not validation_result["valid"]:
                logger.warning(f"行动验证失败: {action.npc} - {action.action} - {validation_result['reason']}")
                self._log_event(
                    f"{action.npc}试图{self._format_action_description(action)}，但{validation_result['reason']}",
                    EventType.ACTION_FAILED,
                    metadata={"action": action.dict(), "reason": validation_result['reason']}
                )
                continue
            
            # 执行行动
            try:
                handler = self._action_handlers.get(action.action, self._handle_custom)
                success = await handler(action)
                
                if success:
                    executed_actions.append(action)
                    logger.info(f"成功执行行动: {action.npc} - {action.action}")
                else:
                    logger.warning(f"行动执行失败: {action.npc} - {action.action}")
                    
            except Exception as e:
                logger.error(f"执行行动时出错: {action.npc} - {action.action}: {str(e)}")
        
        return executed_actions
    
    def _validate_action(self, action: PlannedAction) -> Dict[str, Any]:
        """验证行动的合法性"""
        # 检查NPC是否存在且存活
        npc = self._find_npc(action.npc)
        if not npc:
            return {"valid": False, "reason": "找不到该NPC"}
        
        # 检查NPC是否存活（适配字典和对象格式）
        is_alive = True
        if isinstance(npc, dict):
            is_alive = npc.get("alive", True) and npc.get("hp", 0) > 0
        else:
            is_alive = getattr(npc, "is_alive", True)
        
        if not is_alive:
            return {"valid": False, "reason": "NPC已死亡"}
        
        # 检查NPC状态是否允许行动
        status = npc.get("status", "正常") if isinstance(npc, dict) else getattr(npc, "status", "正常")
        if status in ["昏迷", "瘫痪", "无法行动"]:
            return {"valid": False, "reason": f"NPC处于{status}状态"}
        
        # 检查目标地点是否存在（如果是移动行动）
        if action.action == "move" and action.target:
            available_places = self._get_available_places()
            if action.target not in available_places:
                return {"valid": False, "reason": f"目标地点不可访问: {action.target}"}
        
        # 检查物品是否存在（如果是使用物品）
        if action.action == "use_item" and action.target:
            if not self._npc_has_item(npc, action.target):
                return {"valid": False, "reason": f"NPC没有该物品: {action.target}"}
        
        # 检查行动是否违反规则
        rule_check = self._check_action_against_rules(npc, action)
        if not rule_check["allowed"]:
            return {"valid": False, "reason": f"违反规则: {rule_check['rule_name']}"}
        
        return {"valid": True, "reason": None}
    
    # ========== 行动处理器 ==========
    
    async def _handle_move(self, action: PlannedAction) -> bool:
        """处理移动行动"""
        npc = self._find_npc(action.npc)
        if not npc or not action.target:
            return False
        
        # 获取旧位置
        old_location = npc.get("location", "未知") if isinstance(npc, dict) else getattr(npc, "location", "未知")
        
        # 执行移动
        if isinstance(npc, dict):
            npc["location"] = action.target
        else:
            npc.location = action.target
        
        # 获取NPC名字
        npc_name = npc.get("name", "未知") if isinstance(npc, dict) else getattr(npc, "name", "未知")
        
        # 记录事件
        self._log_event(
            f"{npc_name}从{old_location}移动到{action.target}",
            EventType.NPC_ACTION,
            metadata={
                "actor": npc_name,
                "action": "move",
                "from": old_location,
                "to": action.target,
                "reason": action.reason
            }
        )
        
        # 检查进入新地点是否触发规则
        await self._check_location_triggers(npc, action.target)
        
        return True
    
    async def _handle_search(self, action: PlannedAction) -> bool:
        """处理搜索行动"""
        npc = self._find_npc(action.npc)
        if not npc:
            return False
        
        # 确定搜索目标
        target = action.target or "周围"
        
        # 获取NPC信息
        npc_name = npc.get("name", "未知") if isinstance(npc, dict) else getattr(npc, "name", "未知")
        location = npc.get("location", "未知") if isinstance(npc, dict) else getattr(npc, "location", "未知")
        
        # 记录搜索事件
        self._log_event(
            f"{npc_name}在{location}搜索{target}",
            EventType.NPC_ACTION,
            metadata={
                "actor": npc_name,
                "action": "search",
                "target": target,
                "location": location
            }
        )
        
        # 根据搜索结果生成发现
        discovery = await self._generate_search_discovery(npc, target)
        if discovery:
            self._log_event(
                f"{npc_name}发现了{discovery['item']}",
                EventType.ITEM_FOUND,
                metadata={
                    "finder": npc_name,
                    "item": discovery['item'],
                    "location": location
                }
            )
            
            # 可能增加恐惧
            if discovery.get("scary", False):
                fear_increase = discovery.get("fear_increase", 10)
                if isinstance(npc, dict):
                    npc["fear"] = min(100, npc.get("fear", 0) + fear_increase)
                else:
                    npc.fear = min(100, getattr(npc, "fear", 0) + fear_increase)
        
        return True
    
    async def _handle_talk(self, action: PlannedAction) -> bool:
        """处理交谈行动（通常在对话阶段已处理）"""
        # 交谈通常通过对话系统处理，这里可以记录额外的交互
        return True
    
    async def _handle_use_item(self, action: PlannedAction) -> bool:
        """处理使用物品行动"""
        npc = self._find_npc(action.npc)
        if not npc or not action.target:
            return False
        
        # 获取NPC信息
        npc_name = npc.get("name", "未知") if isinstance(npc, dict) else getattr(npc, "name", "未知")
        location = npc.get("location", "未知") if isinstance(npc, dict) else getattr(npc, "location", "未知")
        
        # 查找物品
        item_obj = None
        item_name = action.target
        
        if isinstance(npc, dict):
            inventory = npc.get("inventory", [])
            for idx, item in enumerate(inventory):
                if isinstance(item, str) and item == action.target:
                    item_obj = {"name": item, "index": idx}
                    break
                elif isinstance(item, dict) and item.get("name") == action.target:
                    item_obj = {"name": item.get("name"), "index": idx, "data": item}
                    break
        else:
            inventory = getattr(npc, "inventory", [])
            for item in inventory:
                if hasattr(item, "name") and item.name == action.target:
                    item_obj = item
                    break
        
        if not item_obj:
            return False
        
        # 使用物品
        effect = self._use_item(npc, item_obj)
        
        # 记录事件
        self._log_event(
            f"{npc_name}使用了{item_name}",
            EventType.ITEM_USED,
            metadata={
                "user": npc_name,
                "item": item_name,
                "effect": effect,
                "location": location
            }
        )
        
        # 移除消耗品
        if effect.get("consumed", False):
            if isinstance(npc, dict) and isinstance(item_obj, dict) and "index" in item_obj:
                npc["inventory"].pop(item_obj["index"])
            elif hasattr(npc, "inventory"):
                npc.inventory.remove(item_obj)
        
        return True
    
    async def _handle_wait(self, action: PlannedAction) -> bool:
        """处理等待行动"""
        npc = self._find_npc(action.npc)
        if not npc:
            return False
        
        # 获取NPC信息
        npc_name = npc.get("name", "未知") if isinstance(npc, dict) else getattr(npc, "name", "未知")
        location = npc.get("location", "未知") if isinstance(npc, dict) else getattr(npc, "location", "未知")
        
        self._log_event(
            f"{npc_name}选择等待观察",
            EventType.NPC_ACTION,
            metadata={
                "actor": npc_name,
                "action": "wait",
                "location": location
            }
        )
        
        # 等待可能略微降低恐惧
        if isinstance(npc, dict):
            npc["fear"] = max(0, npc.get("fear", 0) - 5)
        else:
            npc.fear = max(0, getattr(npc, "fear", 0) - 5)
        
        return True
    
    async def _handle_defend(self, action: PlannedAction) -> bool:
        """处理防御行动"""
        npc = self._find_npc(action.npc)
        if not npc:
            return False
        
        # 获取NPC信息
        npc_name = npc.get("name", "未知") if isinstance(npc, dict) else getattr(npc, "name", "未知")
        location = npc.get("location", "未知") if isinstance(npc, dict) else getattr(npc, "location", "未知")
        
        # 设置防御状态
        if isinstance(npc, dict):
            npc["status"] = "防御中"
        else:
            npc.status = "防御中"
        
        self._log_event(
            f"{npc_name}采取防御姿态",
            EventType.NPC_ACTION,
            metadata={
                "actor": npc_name,
                "action": "defend",
                "location": location
            }
        )
        
        return True
    
    async def _handle_investigate(self, action: PlannedAction) -> bool:
        """处理调查行动"""
        npc = self._find_npc(action.npc)
        if not npc:
            return False
        
        # 获取NPC信息
        npc_name = npc.get("name", "未知") if isinstance(npc, dict) else getattr(npc, "name", "未知")
        location = npc.get("location", "未知") if isinstance(npc, dict) else getattr(npc, "location", "未知")
        
        target = action.target or "异常现象"
        
        self._log_event(
            f"{npc_name}仔细调查{target}",
            EventType.NPC_ACTION,
            metadata={
                "actor": npc_name,
                "action": "investigate",
                "target": target,
                "location": location
            }
        )
        
        # 调查可能揭示线索或触发事件
        clue = await self._generate_investigation_result(npc, target)
        if clue:
            self._log_event(
                f"{npc_name}发现了重要线索：{clue}",
                EventType.CLUE_FOUND,
                metadata={
                    "investigator": npc_name,
                    "clue": clue,
                    "target": target
                }
            )
        
        return True
    
    async def _handle_hide(self, action: PlannedAction) -> bool:
        """处理躲藏行动"""
        npc = self._find_npc(action.npc)
        if not npc:
            return False
        
        # 获取NPC信息
        npc_name = npc.get("name", "未知") if isinstance(npc, dict) else getattr(npc, "name", "未知")
        location = npc.get("location", "未知") if isinstance(npc, dict) else getattr(npc, "location", "未知")
        
        # 设置躲藏状态
        if isinstance(npc, dict):
            npc["status"] = "躲藏中"
        else:
            npc.status = "躲藏中"
        
        hiding_spot = action.target or "阴影处"
        
        self._log_event(
            f"{npc_name}躲藏到{hiding_spot}",
            EventType.NPC_ACTION,
            metadata={
                "actor": npc_name,
                "action": "hide",
                "spot": hiding_spot,
                "location": location
            }
        )
        
        # 躲藏可能降低被某些规则影响的概率
        return True
    
    async def _handle_run(self, action: PlannedAction) -> bool:
        """处理逃跑行动"""
        npc = self._find_npc(action.npc)
        if not npc:
            return False
        
        # 获取NPC信息
        npc_name = npc.get("name", "未知") if isinstance(npc, dict) else getattr(npc, "name", "未知")
        
        # 逃跑会大幅增加恐惧但可能保命
        if isinstance(npc, dict):
            current_fear = npc.get("fear", 0)
            npc["fear"] = min(100, current_fear + 20)
            new_fear = npc["fear"]
        else:
            npc.fear = min(100, getattr(npc, "fear", 0) + 20)
            new_fear = npc.fear
        
        # 如果指定了目标地点，执行快速移动
        if action.target and action.target in self._get_available_places():
            old_location = npc.get("location", "未知") if isinstance(npc, dict) else getattr(npc, "location", "未知")
            
            if isinstance(npc, dict):
                npc["location"] = action.target
            else:
                npc.location = action.target
            
            self._log_event(
                f"{npc_name}惊慌失措地从{old_location}逃到{action.target}",
                EventType.NPC_ACTION,
                metadata={
                    "actor": npc_name,
                    "action": "run",
                    "from": old_location,
                    "to": action.target,
                    "fear_level": new_fear
                }
            )
        else:
            location = npc.get("location", "未知") if isinstance(npc, dict) else getattr(npc, "location", "未知")
            self._log_event(
                f"{npc_name}陷入恐慌，四处逃窜",
                EventType.NPC_ACTION,
                metadata={
                    "actor": npc_name,
                    "action": "run",
                    "location": location,
                    "fear_level": new_fear
                }
            )
        
        return True
    
    async def _handle_custom(self, action: PlannedAction) -> bool:
        """处理自定义行动"""
        npc = self._find_npc(action.npc)
        if not npc:
            return False
        
        # 获取NPC信息
        npc_name = npc.get("name", "未知") if isinstance(npc, dict) else getattr(npc, "name", "未知")
        location = npc.get("location", "未知") if isinstance(npc, dict) else getattr(npc, "location", "未知")
        
        self._log_event(
            f"{npc_name}{action.reason or '执行了特殊行动'}",
            EventType.NPC_ACTION,
            metadata={
                "actor": npc_name,
                "action": "custom",
                "description": action.reason,
                "target": action.target,
                "location": location
            }
        )
        
        return True
    
    # ========== 叙事生成 ==========
    
    async def generate_turn_narrative(self, include_hidden_events: bool = False) -> str:
        """
        生成回合叙事
        
        Args:
            include_hidden_events: 是否包含隐藏事件（如规则触发细节）
            
        Returns:
            str: 生成的叙事文本
        """
        try:
            # 获取本回合事件
            turn_events = self._get_turn_events()
            
            if not turn_events:
                return "这一刻，时间仿佛静止了，每个人都在等待着什么……"
            
            # 过滤事件
            if not include_hidden_events:
                turn_events = [e for e in turn_events if not e.get("hidden", False)]
            
            # 获取当前NPC状态（用于叙事参考）
            npc_states = self._prepare_npc_states()
            
            # 生成叙事
            narrative = await self.ds_client.generate_narrative_text(
                events=turn_events,
                time_of_day=self.game_mgr.state.time_of_day,
                location=self.game_mgr.state.current_location,
                npc_states=npc_states
            )
            
            # 保存叙事
            self._save_narrative(narrative)
            
            return narrative
            
        except Exception as e:
            logger.error(f"生成叙事失败: {str(e)}")
            return "恐惧在蔓延，但具体发生了什么，已经没人能说清楚了……"
    
    # ========== 规则评估 ==========
    
    async def evaluate_player_rule(self, rule_description: str) -> Dict[str, Any]:
        """
        评估玩家提出的自然语言规则
        
        Args:
            rule_description: 规则的自然语言描述
            
        Returns:
            Dict: 包含评估结果的字典
        """
        try:
            # 准备世界状态上下文
            world_ctx = {
                "rule_count": len(self.game_mgr.state.rules),
                "avg_fear": self._calculate_avg_fear(),
                "places": list(self.game_mgr.state.locations.keys()),
                "difficulty_level": self.game_mgr.difficulty,
                "common_items": self._get_common_items()
            }
            
            # 调用AI评估
            eval_result = await self.ds_client.evaluate_rule_nl(
                rule_nl=rule_description,
                world_ctx=world_ctx
            )
            
            # 构建返回结果
            return {
                "name": eval_result.name,
                "cost": eval_result.cost,
                "difficulty": eval_result.difficulty,
                "loopholes": eval_result.loopholes,
                "suggestion": eval_result.suggestion,
                "estimated_fear_gain": eval_result.estimated_fear_gain,
                "parsed_rule": {
                    "trigger": eval_result.trigger.dict(),
                    "effect": eval_result.effect.dict(),
                    "cooldown": eval_result.cooldown
                }
            }
            
        except Exception as e:
            logger.error(f"评估规则失败: {str(e)}")
            return {
                "error": str(e),
                "suggestion": "请尝试更清晰地描述规则"
            }
    
    # ========== 辅助方法 ==========
    
    def _find_npc(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名字查找NPC"""
        # 适配字典格式的NPC
        for npc in self.game_mgr.npcs:
            if isinstance(npc, dict) and npc.get("name") == name:
                return npc
            elif hasattr(npc, "name") and npc.name == name:
                return npc
        return None
    
    def _get_recent_events(self, limit: int = 5) -> List[Event]:
        """获取最近的事件"""
        return self.game_mgr.state.events_history[-limit:] if self.game_mgr.state.events_history else []
    
    def _get_turn_events(self) -> List[Dict[str, Any]]:
        """获取本回合的事件"""
        current_turn = self.game_mgr.state.turn_count
        turn_events = []
        
        for event in reversed(self.game_mgr.state.events_history):
            if event.turn == current_turn:
                turn_events.append({
                    "type": event.type.value,
                    "description": event.description,
                    "timestamp": event.timestamp.isoformat() if event.timestamp else None,
                    "metadata": event.metadata or {},
                    "hidden": event.metadata.get("hidden", False) if event.metadata else False
                })
            elif event.turn < current_turn:
                break
        
        return list(reversed(turn_events))
    
    def _log_event(self, description: str, event_type: EventType, metadata: Optional[Dict] = None):
        """记录事件到历史"""
        event = Event(
            type=event_type,
            description=description,
            turn=self.game_mgr.state.turn_count,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.game_mgr.state.events_history.append(event)
        logger.debug(f"记录事件: {description}")
    
    def _save_narrative(self, narrative: str):
        """保存叙事文本"""
        self._log_event(
            narrative,
            EventType.NARRATIVE,
            metadata={"is_narrative": True, "length": len(narrative)}
        )
    
    def _get_npc_status_description(self, npc: Dict[str, Any]) -> str:
        """获取NPC状态的描述性文本"""
        # 获取状态和恐惧值
        if isinstance(npc, dict):
            status = npc.get("status", "")
            fear = npc.get("fear", 0)
        else:
            status = getattr(npc, "status", "")
            fear = getattr(npc, "fear", 0)
        
        if status:
            return status
        
        # 根据数值生成状态描述
        if fear >= 80:
            return "极度恐慌"
        elif fear >= 60:
            return "非常害怕"
        elif fear >= 40:
            return "感到恐惧"
        elif fear >= 20:
            return "略微不安"
        else:
            return "相对冷静"
    
    def _calculate_relationship(self, npc1: Dict[str, Any], npc2: Dict[str, Any]) -> int:
        """计算两个NPC之间的关系值（0-100）"""
        # 获取性格特征
        if isinstance(npc1, dict):
            traits1 = set(npc1.get("traits", []))
        else:
            traits1 = set(getattr(npc1, "traits", []))
            
        if isinstance(npc2, dict):
            traits2 = set(npc2.get("traits", []))
        else:
            traits2 = set(getattr(npc2, "traits", []))
        
        # 简单实现：基于性格相似度
        shared_traits = traits1 & traits2
        base_relationship = 50 + len(shared_traits) * 10
        
        # 根据最近的互动调整
        # TODO: 实现基于事件历史的关系调整
        
        return min(100, max(0, base_relationship))
    
    def _format_event_description(self, event: Event) -> str:
        """格式化事件描述用于prompt"""
        return event.description
    
    def _is_rule_active(self, rule: Any) -> bool:
        """检查规则是否处于激活状态"""
        # 适配字典和对象格式
        if isinstance(rule, dict):
            cooldown_until = rule.get("cooldown_until")
            active = rule.get("active", True)
        else:
            cooldown_until = getattr(rule, "cooldown_until", None)
            active = getattr(rule, "active", True)
        
        if not active:
            return False
            
        if cooldown_until:
            return datetime.now() >= cooldown_until
        return True
    
    def _get_special_conditions(self) -> List[str]:
        """获取当前的特殊条件"""
        conditions = []
        
        # 检查时间相关条件
        hour = int(self.game_mgr.state.time_of_day.split(":")[0]) if ":" in self.game_mgr.state.time_of_day else 0
        if 22 <= hour or hour <= 6:
            conditions.append("深夜时分")
        
        # 检查环境条件
        if hasattr(self.game_mgr.state, "power_on") and not self.game_mgr.state.power_on:
            conditions.append("停电")
        
        # 检查NPC状态
        alive_count = sum(1 for npc in self.game_mgr.state.npcs if npc.is_alive)
        if alive_count <= 2:
            conditions.append("仅剩少数幸存者")
        
        return conditions
    
    def _calculate_ambient_fear(self) -> int:
        """计算环境恐惧等级"""
        base_fear = 30
        
        # 时间因素
        if "深夜" in self.game_mgr.state.time_of_day or "午夜" in self.game_mgr.state.time_of_day:
            base_fear += 20
        
        # 死亡事件影响
        death_count = sum(1 for npc in self.game_mgr.state.npcs if not npc.is_alive)
        base_fear += death_count * 10
        
        # 规则数量影响
        base_fear += len(self.game_mgr.state.rules) * 5
        
        return min(100, base_fear)
    
    def _get_weather_condition(self) -> str:
        """获取天气状况"""
        # 简单实现，可以扩展为更复杂的天气系统
        import random
        weather_options = ["阴沉", "雷雨", "浓雾", "寒冷", "闷热"]
        return random.choice(weather_options)
    
    def _is_location_accessible(self, location: str) -> bool:
        """检查地点是否可访问"""
        # TODO: 实现基于规则和条件的访问控制
        return location in self.game_mgr.state.locations
    
    def _calculate_avg_fear(self) -> float:
        """计算平均恐惧值"""
        alive_npcs = self.game_mgr.get_active_npcs()
        if not alive_npcs:
            return 0
        
        total_fear = 0
        for npc in alive_npcs:
            if isinstance(npc, dict):
                total_fear += npc.get("fear", 0)
            else:
                total_fear += getattr(npc, "fear", 0)
        
        return total_fear / len(alive_npcs)
    
    def _get_common_items(self) -> List[str]:
        """获取常见物品列表"""
        # 从所有NPC的物品中提取
        all_items = []
        for npc in self.game_mgr.state.npcs:
            all_items.extend([item.name for item in npc.inventory])
        
        # 返回去重后的列表
        return list(set(all_items)) or ["手电筒", "钥匙", "日记本", "绳子"]
    
    def _format_action_description(self, action: PlannedAction) -> str:
        """格式化行动描述"""
        action_verbs = {
            "move": f"移动到{action.target}",
            "search": f"搜索{action.target or '周围'}",
            "use_item": f"使用{action.target}",
            "investigate": f"调查{action.target or '异常'}",
            "hide": f"躲藏到{action.target or '某处'}",
            "run": "逃跑",
            "wait": "等待",
            "defend": "防御"
        }
        return action_verbs.get(action.action, action.action)
    
    def _check_action_against_rules(self, npc: NPC, action: PlannedAction) -> Dict[str, Any]:
        """检查行动是否违反规则"""
        # TODO: 实现规则检查逻辑
        return {"allowed": True, "rule_name": None}
    
    def _npc_has_item(self, npc: Dict[str, Any], item_name: str) -> bool:
        """检查NPC是否拥有指定物品"""
        if isinstance(npc, dict):
            inventory = npc.get("inventory", [])
            # 处理字符串列表或对象列表
            for item in inventory:
                if isinstance(item, str) and item == item_name:
                    return True
                elif isinstance(item, dict) and item.get("name") == item_name:
                    return True
                elif hasattr(item, "name") and item.name == item_name:
                    return True
        else:
            inventory = getattr(npc, "inventory", [])
            return any(getattr(item, "name", item) == item_name for item in inventory)
        return False
    
    async def _check_dialogue_triggers(self, npc: NPC, text: str):
        """检查对话是否触发规则"""
        # TODO: 实现对话触发检查
        pass
    
    async def _check_location_triggers(self, npc: NPC, location: str):
        """检查进入地点是否触发规则"""
        # TODO: 实现地点触发检查
        pass
    
    async def _generate_search_discovery(self, npc: NPC, target: str) -> Optional[Dict[str, Any]]:
        """生成搜索发现"""
        # TODO: 实现搜索结果生成
        import random
        if random.random() > 0.7:
            return {
                "item": "一本沾血的日记",
                "scary": True,
                "fear_increase": 15
            }
        return None
    
    def _use_item(self, npc: NPC, item: Any) -> Dict[str, Any]:
        """使用物品的效果"""
        # TODO: 实现物品使用逻辑
        return {"consumed": False, "effect": "使用了物品"}
    
    async def _generate_investigation_result(self, npc: NPC, target: str) -> Optional[str]:
        """生成调查结果"""
        # TODO: 实现调查结果生成
        import random
        if random.random() > 0.6:
            return "墙上的血迹组成了奇怪的符号"
        return None
    
    async def _post_turn_processing(self, executed_actions: List[PlannedAction]):
        """回合后处理"""
        # 检查是否有NPC死亡
        for npc in self.game_mgr.npcs:
            # 获取NPC信息
            if isinstance(npc, dict):
                fear = npc.get("fear", 0)
                is_alive = npc.get("alive", True) and npc.get("hp", 0) > 0
                npc_name = npc.get("name", "未知")
            else:
                fear = getattr(npc, "fear", 0)
                is_alive = getattr(npc, "is_alive", True)
                npc_name = getattr(npc, "name", "未知")
            
            if fear >= 100 and is_alive:
                # 标记NPC死亡
                if isinstance(npc, dict):
                    npc["alive"] = False
                    npc["hp"] = 0
                else:
                    npc.is_alive = False
                
                self._log_event(
                    f"{npc_name}因极度恐惧而精神崩溃",
                    EventType.NPC_DEATH,
                    metadata={"victim": npc_name, "cause": "恐惧过度"}
                )
        
        # 更新回合计数
        if self.game_mgr.state:
            self.game_mgr.state.turn_count += 1


# ========== 测试代码 ==========

if __name__ == "__main__":
    import asyncio
    
    async def test_pipeline():
        """测试AI管线"""
        from src.api.deepseek_client import DeepSeekClient, APIConfig
        
        # 创建mock客户端
        client = DeepSeekClient(APIConfig(mock_mode=True))
        
        # 创建mock游戏管理器
        class MockGameManager:
            class State:
                turn_count = 1
                time_of_day = "午夜"
                current_location = "废弃医院"
                locations = {"废弃医院": {}, "走廊": {}, "二楼": {}}
                events_history = []
                rules = []
                
                class MockNPC:
                    def __init__(self, name, fear=50, sanity=80):
                        self.name = name
                        self.fear = fear
                        self.sanity = sanity
                        self.traits = ["谨慎", "理性"]
                        self.status = "正常"
                        self.location = "废弃医院"
                        self.inventory = []
                        self.is_alive = True
                
                npcs = [
                    MockNPC("张三", 45, 75),
                    MockNPC("李四", 60, 60)
                ]
            
            state = State()
            difficulty = "普通"
        
        game_mgr = MockGameManager()
        pipeline = AITurnPipeline(game_mgr, client)
        
        print("=== 测试AI回合 ===")
        plan = await pipeline.run_turn_ai()
        print(f"生成了 {len(plan.dialogue)} 条对话，{len(plan.actions)} 个行动")
        
        print("\n=== 测试叙事生成 ===")
        narrative = await pipeline.generate_turn_narrative()
        print(f"叙事: {narrative[:100]}...")
        
        print("\n=== 测试规则评估 ===")
        eval_result = await pipeline.evaluate_player_rule("晚上不能开灯，否则会吸引怪物")
        print(f"规则名: {eval_result.get('name')}")
        print(f"成本: {eval_result.get('cost')}")
        
        await client.close()
    
    asyncio.run(test_pipeline())
