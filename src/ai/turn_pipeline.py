"""
AI 驱动的回合管线
处理对话生成、行动规划、规则评估等核心 AI 功能
"""
import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime
import random

from src.api.schemas import (
    TurnPlan, DialogueTurn, PlannedAction,
    NPCStateForAI, SceneContext, validate_turn_plan
)
from src.api.prompts import create_mock_turn_plan, create_mock_narrative, create_mock_rule_eval
from src.models.event import Event, EventType

if TYPE_CHECKING:
    from src.api.deepseek_client import DeepSeekClient
    from src.core.game_state import GameStateManager

logger = logging.getLogger(__name__)


class AITurnPipeline:
    """AI回合处理管线"""
    
    def __init__(self, game_mgr: 'GameStateManager', ds_client: 'DeepSeekClient'):
        """
        初始化AI管线
        
        Args:
            game_mgr: 游戏状态管理器
            ds_client: DeepSeek客户端
        """
        self.game_mgr = game_mgr
        self.ds_client = ds_client
        self.last_plan: Optional[TurnPlan] = None
        self.narrative_cache: Dict[int, str] = {}  # 回合->叙事的缓存
        
    async def run_turn_ai(self, force_dialogue: bool = True) -> TurnPlan:
        """
        执行AI驱动的回合
        
        Args:
            force_dialogue: 是否强制生成对话（即使NPC数量不足）
            
        Returns:
            TurnPlan: 回合计划（对话+行动）
        """
        try:
            # 1. 收集游戏状态
            state = self.game_mgr.state
            if not state:
                raise RuntimeError("游戏状态未初始化")
            
            # 2. 准备NPC状态数据
            npc_states = self._prepare_npc_states()
            if not npc_states and not force_dialogue:
                logger.warning("没有存活的NPC，跳过AI回合")
                return TurnPlan(dialogue=[], actions=[])
            
            # 3. 准备场景上下文
            scene_context = self._prepare_scene_context()
            
            # 4. 获取可用地点
            available_places = self._get_available_places()
            
            # 5. 调用AI生成计划
            logger.info("🤖 AI正在生成回合计划...")
            plan = await self.ds_client.generate_turn_plan(
                npc_states=npc_states,
                scene_context=scene_context,
                available_places=available_places,
                time_of_day=state.time_of_day,
                min_dialogue=2 if len(npc_states) >= 2 else 0
            )
            
            # 6. 验证计划合法性
            issues = validate_turn_plan(plan)
            if issues:
                logger.warning(f"AI生成的计划存在问题: {issues}")
            
            # 7. 处理对话
            await self._process_dialogue(plan.dialogue)
            
            # 8. 验证并执行行动
            await self._process_actions(plan.actions)
            
            # 9. 保存计划供后续使用
            self.last_plan = plan
            
            # 10. 触发回合后处理
            await self._post_turn_processing()
            
            return plan
            
        except Exception as e:
            logger.error(f"AI回合执行失败: {str(e)}")
            # 使用降级方案
            mock_plan_data = create_mock_turn_plan()
            return TurnPlan.model_validate(mock_plan_data)
    
    async def generate_turn_narrative(self, include_hidden_events: bool = False) -> str:
        """
        生成回合叙事
        
        Args:
            include_hidden_events: 是否包含隐藏事件
            
        Returns:
            str: 叙事文本
        """
        try:
            current_turn = self.game_mgr.state.current_turn
            
            # 检查缓存
            if current_turn in self.narrative_cache and not include_hidden_events:
                return self.narrative_cache[current_turn]
            
            # 收集本回合事件
            events = self._collect_turn_events(include_hidden_events)
            if not events:
                return "这一刻，时间仿佛静止了。所有人都在等待着什么……或者说，害怕着什么。"
            
            # 格式化事件描述
            event_descriptions = []
            for event in events:
                if isinstance(event, dict):
                    desc = event.get("description", "")
                elif hasattr(event, "description"):
                    desc = event.description
                else:
                    desc = str(event)
                
                if desc:
                    event_descriptions.append(desc)
            
            # 调用AI生成叙事
            logger.info("📖 AI正在生成叙事...")
            survivor_count = len(self.game_mgr.get_alive_npcs())
            
            narrative = await self.ds_client.generate_narrative_text(
                events=event_descriptions,
                time_of_day=self.game_mgr.state.time_of_day,
                survivor_count=survivor_count,
                ambient_fear=self._calculate_ambient_fear(),
                min_len=200
            )
            
            # 缓存结果
            self.narrative_cache[current_turn] = narrative
            
            # 保存到事件历史
            self._save_narrative(narrative)
            
            return narrative
            
        except Exception as e:
            logger.error(f"叙事生成失败: {str(e)}")
            # 使用降级方案
            return create_mock_narrative()
    
    async def evaluate_player_rule(self, rule_description: str) -> Dict[str, Any]:
        """
        评估玩家提出的规则
        
        Args:
            rule_description: 自然语言的规则描述
            
        Returns:
            Dict: 评估结果
        """
        try:
            # 准备评估上下文
            world_ctx = self._prepare_world_context()
            
            # 调用AI评估
            logger.info("🔍 AI正在评估规则...")
            eval_result = await self.ds_client.evaluate_rule_nl(
                rule_nl=rule_description,
                world_ctx=world_ctx
            )
            
            # 转换为标准格式
            result = {
                "name": eval_result.name,
                "cost": eval_result.cost,
                "difficulty": eval_result.difficulty,
                "loopholes": eval_result.loopholes,
                "suggestion": eval_result.suggestion,
                "parsed_rule": {
                    "trigger": eval_result.trigger.model_dump(),
                    "effect": eval_result.effect.model_dump(),
                    "cooldown": eval_result.cooldown
                }
            }
            
            logger.info(f"规则评估完成: {result['name']} (成本:{result['cost']})")
            return result
            
        except Exception as e:
            logger.error(f"规则评估失败: {str(e)}")
            # 使用降级方案
            return create_mock_rule_eval()
    
    # ========== 私有辅助方法 ==========
    
    def _prepare_npc_states(self) -> List[Dict[str, Any]]:
        """准备NPC状态数据"""
        npc_states = []
        
        for npc in self.game_mgr.get_alive_npcs():
            # 计算NPC之间的关系
            relationships = self._calculate_npc_relationships(npc)
            
            npc_state = NPCStateForAI(
                name=npc.get("name", "未知"),
                fear=npc.get("fear", 0),
                sanity=npc.get("sanity", 100),
                hp=npc.get("hp", 100),
                traits=npc.get("traits", []),
                status=npc.get("status", "正常"),
                location=npc.get("location", "未知位置"),
                inventory=npc.get("inventory", []),
                relationships=relationships
            )
            npc_states.append(npc_state.model_dump())
            
        return npc_states
    
    def _prepare_scene_context(self) -> Dict[str, Any]:
        """准备场景上下文"""
        state = self.game_mgr.state
        
        # 获取最近事件描述
        recent_events = []
        for event in state.events_history[-5:]:
            if hasattr(event, "to_dict"):
                event_dict = event.to_dict()
                desc = event_dict.get("description", "")
            elif isinstance(event, dict):
                desc = event.get("description", "")
            else:
                desc = str(event)
            
            if desc:
                recent_events.append(desc)
        
        # 获取激活的规则名称
        active_rule_names = []
        for rule_id in state.active_rules:
            rule = self._find_rule_by_id(rule_id)
            if rule:
                active_rule_names.append(getattr(rule, "name", f"规则{rule_id}"))
        
        context = SceneContext(
            current_location="恐怖空间",  # TODO: 实现具体位置系统
            time_of_day=state.time_of_day,
            recent_events=recent_events,
            active_rules=active_rule_names,
            ambient_fear_level=self._calculate_ambient_fear(),
            special_conditions=self._get_special_conditions()
        )
        
        return context.model_dump()
    
    def _get_available_places(self) -> List[str]:
        """获取可用地点列表"""
        # TODO: 从地图系统获取
        default_places = [
            "客厅", "厨房", "卧室", "浴室", 
            "走廊", "阁楼", "地下室", "花园"
        ]
        
        # 如果有地图系统，从中获取
        if hasattr(self.game_mgr, "map_system"):
            return list(self.game_mgr.map_system.locations.keys())
        
        return default_places
    
    async def _process_dialogue(self, dialogue_turns: List[DialogueTurn]):
        """处理对话回合"""
        for turn in dialogue_turns:
            # 创建对话事件
            event = Event(
                type=EventType.NPC_DIALOGUE,
                description=f"{turn.speaker}: {turn.text}",
                turn=self.game_mgr.state.current_turn,
                meta={
                    "speaker": turn.speaker,
                    "text": turn.text,
                    "emotion": turn.emotion
                }
            )
            
            # 添加到事件历史（转换为dict格式）
            self.game_mgr.state.events_history.append(event.to_dict())
            
            # 记录日志
            emotion_emoji = {
                "fear": "😨",
                "calm": "😐",
                "panic": "😱",
                "suspicious": "🤨",
                "angry": "😠"
            }
            emoji = emotion_emoji.get(turn.emotion, "💬")
            self.game_mgr.log(f"{emoji} {turn.speaker}: {turn.text}")
    
    async def _process_actions(self, actions: List[PlannedAction]):
        """处理并执行NPC行动"""
        for action in actions:
            # 验证行动合法性
            if not self._validate_action(action):
                logger.warning(f"非法行动被阻止: {action.model_dump()}")
                self._log_blocked_action(action)
                continue
            
            # 执行行动
            await self._execute_action(action)
            
            # 检查规则触发
            await self._check_rule_triggers(action)
    
    def _validate_action(self, action: PlannedAction) -> bool:
        """验证行动是否合法"""
        # 检查NPC是否存在且存活
        npc = self._find_npc_by_name(action.npc)
        if not npc or not npc.get("alive", True):
            return False
        
        # 检查目标地点是否有效
        if action.action == "move" and action.target:
            available_places = self._get_available_places()
            if action.target not in available_places:
                return False
        
        # 检查NPC状态是否允许行动
        if npc.get("status") == "昏迷" or npc.get("hp", 0) <= 0:
            return False
        
        return True
    
    async def _execute_action(self, action: PlannedAction):
        """执行单个行动"""
        npc = self._find_npc_by_name(action.npc)
        if not npc:
            return
        
        # 根据行动类型执行
        action_handlers = {
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
        
        handler = action_handlers.get(action.action, self._handle_custom)
        await handler(npc, action)
        
        # 记录行动事件
        self._log_action_event(npc, action)
    
    # ========== 行动处理器 ==========
    
    async def _handle_move(self, npc: Dict[str, Any], action: PlannedAction):
        """处理移动行动"""
        old_location = npc.get("location", "未知位置")
        npc["location"] = action.target
        
        # 更新游戏状态
        self.game_mgr.update_npc(npc["id"], {"location": action.target})
        
        # 可能触发位置相关事件
        if action.target == "地下室" and self.game_mgr.state.time_of_day == "night":
            npc["fear"] = min(100, npc.get("fear", 0) + 10)
            self.game_mgr.update_npc(npc["id"], {"fear": npc["fear"]})
    
    async def _handle_search(self, npc: Dict[str, Any], action: PlannedAction):
        """处理搜索行动"""
        # 随机决定是否找到物品
        if random.random() < 0.3:
            items = ["手电筒", "绳子", "钥匙", "笔记", "照片"]
            found_item = random.choice(items)
            
            # 添加到物品栏
            inventory = npc.get("inventory", [])
            inventory.append(found_item)
            self.game_mgr.update_npc(npc["id"], {"inventory": inventory})
            
            # 创建发现事件
            self._create_event(
                EventType.ITEM_FOUND,
                f"{npc['name']}找到了{found_item}",
                {"item": found_item, "finder": npc["name"]}
            )
    
    async def _handle_talk(self, npc: Dict[str, Any], action: PlannedAction):
        """处理交谈行动（已在对话阶段处理）"""
        pass
    
    async def _handle_use_item(self, npc: Dict[str, Any], action: PlannedAction):
        """处理使用物品行动"""
        inventory = npc.get("inventory", [])
        if action.target in inventory:
            # 移除使用的物品
            inventory.remove(action.target)
            self.game_mgr.update_npc(npc["id"], {"inventory": inventory})
            
            # 应用物品效果
            if action.target == "手电筒":
                # 降低恐惧
                npc["fear"] = max(0, npc.get("fear", 0) - 10)
                self.game_mgr.update_npc(npc["id"], {"fear": npc["fear"]})
    
    async def _handle_wait(self, npc: Dict[str, Any], action: PlannedAction):
        """处理等待行动"""
        # 恢复少量理智
        npc["sanity"] = min(100, npc.get("sanity", 100) + 5)
        self.game_mgr.update_npc(npc["id"], {"sanity": npc["sanity"]})
    
    async def _handle_defend(self, npc: Dict[str, Any], action: PlannedAction):
        """处理防御行动"""
        # 设置防御状态
        npc["status"] = "防御中"
        self.game_mgr.update_npc(npc["id"], {"status": npc["status"]})
    
    async def _handle_investigate(self, npc: Dict[str, Any], action: PlannedAction):
        """处理调查行动"""
        # 可能发现线索或触发事件
        if random.random() < 0.4:
            clues = ["血迹", "奇怪的符号", "日记残页", "划痕", "脚印"]
            found_clue = random.choice(clues)
            
            self._create_event(
                EventType.CLUE_FOUND,
                f"{npc['name']}发现了{found_clue}",
                {"clue": found_clue, "investigator": npc["name"]}
            )
            
            # 增加恐惧
            npc["fear"] = min(100, npc.get("fear", 0) + 15)
            self.game_mgr.update_npc(npc["id"], {"fear": npc["fear"]})
    
    async def _handle_hide(self, npc: Dict[str, Any], action: PlannedAction):
        """处理躲藏行动"""
        npc["status"] = "躲藏中"
        self.game_mgr.update_npc(npc["id"], {"status": npc["status"]})
        
        # 降低被某些规则影响的概率
        npc["hidden"] = True
        self.game_mgr.update_npc(npc["id"], {"hidden": True})
    
    async def _handle_run(self, npc: Dict[str, Any], action: PlannedAction):
        """处理逃跑行动"""
        # 快速移动但增加恐惧
        if action.target:
            npc["location"] = action.target
            npc["fear"] = min(100, npc.get("fear", 0) + 20)
            self.game_mgr.update_npc(npc["id"], {
                "location": npc["location"],
                "fear": npc["fear"]
            })
    
    async def _handle_custom(self, npc: Dict[str, Any], action: PlannedAction):
        """处理自定义行动"""
        # 记录自定义行动
        self._create_event(
            EventType.NPC_ACTION,
            f"{npc['name']}执行了特殊行动: {action.target or '未知'}",
            {"action": action.model_dump()}
        )
    
    async def _check_rule_triggers(self, action: PlannedAction):
        """检查行动是否触发规则"""
        # TODO: 与规则执行器集成
        pass
    
    async def _post_turn_processing(self):
        """回合后处理"""
        # 清理临时状态
        for npc in self.game_mgr.get_alive_npcs():
            if npc.get("status") == "防御中":
                npc["status"] = "正常"
                self.game_mgr.update_npc(npc["id"], {"status": npc["status"]})
            
            if npc.get("hidden"):
                npc["hidden"] = False
                self.game_mgr.update_npc(npc["id"], {"hidden": False})
    
    # ========== 辅助方法 ==========
    
    def _find_npc_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名字查找NPC"""
        for npc in self.game_mgr.npcs:
            if npc.get("name") == name:
                return npc
        return None
    
    def _find_rule_by_id(self, rule_id: str) -> Any:
        """根据ID查找规则"""
        for rule in self.game_mgr.rules:
            if getattr(rule, "id", None) == rule_id:
                return rule
        return None
    
    def _calculate_npc_relationships(self, npc: Dict[str, Any]) -> Dict[str, int]:
        """计算NPC之间的关系值"""
        relationships = {}
        # TODO: 实现基于历史互动的关系系统
        for other_npc in self.game_mgr.get_alive_npcs():
            if other_npc.get("id") != npc.get("id"):
                # 暂时使用随机值
                relationships[other_npc.get("name", "未知")] = random.randint(30, 80)
        return relationships
    
    def _calculate_ambient_fear(self) -> int:
        """计算环境恐惧等级"""
        return self.game_mgr._calculate_ambient_fear()
    
    def _get_special_conditions(self) -> List[str]:
        """获取特殊条件"""
        return self.game_mgr._get_special_conditions()
    
    def _collect_turn_events(self, include_hidden: bool) -> List[Any]:
        """收集本回合的事件"""
        current_turn = self.game_mgr.state.current_turn
        turn_events = []
        
        for event in reversed(self.game_mgr.state.events_history):
            # 判断事件的回合
            if hasattr(event, "turn"):
                event_turn = event.turn
            elif isinstance(event, dict):
                event_turn = event.get("turn", 0)
            else:
                continue
            
            if event_turn == current_turn:
                # 检查是否包含隐藏事件
                is_hidden = False
                if hasattr(event, "meta"):
                    is_hidden = event.meta.get("hidden", False)
                elif isinstance(event, dict):
                    is_hidden = event.get("meta", {}).get("hidden", False)
                
                if not is_hidden or include_hidden:
                    turn_events.append(event)
            elif event_turn < current_turn:
                break
        
        return list(reversed(turn_events))
    
    def _save_narrative(self, narrative: str):
        """保存叙事文本"""
        event = Event(
            type=EventType.NARRATIVE,
            description=narrative,
            turn=self.game_mgr.state.current_turn,
            meta={"is_narrative": True}
        )
        self.game_mgr.state.events_history.append(event.to_dict())
    
    def _create_event(self, event_type: EventType, description: str, meta: Dict[str, Any] = None):
        """创建并记录事件"""
        event = Event(
            type=event_type,
            description=description,
            turn=self.game_mgr.state.current_turn,
            meta=meta or {}
        )
        self.game_mgr.state.events_history.append(event.to_dict())
        self.game_mgr.log(description)
    
    def _log_action_event(self, npc: Dict[str, Any], action: PlannedAction):
        """记录行动事件"""
        action_desc = {
            "move": f"移动到{action.target}",
            "search": f"搜索{action.target or '周围'}",
            "talk": f"与{action.target or '其他人'}交谈",
            "use_item": f"使用{action.target}",
            "wait": "等待观察",
            "defend": "进入防御姿态",
            "investigate": f"调查{action.target or '异常'}",
            "hide": f"躲藏在{action.target or '暗处'}",
            "run": f"逃向{action.target or '安全地带'}",
            "custom": action.target or "执行特殊行动"
        }
        
        description = f"{npc['name']}{action_desc.get(action.action, '执行未知行动')}"
        if action.reason:
            description += f" ({action.reason})"
        
        self._create_event(EventType.NPC_ACTION, description, {
            "actor": npc["name"],
            "action": action.action,
            "target": action.target,
            "priority": action.priority
        })
    
    def _log_blocked_action(self, action: PlannedAction):
        """记录被阻止的行动"""
        self._create_event(
            EventType.SYSTEM,
            f"{action.npc}试图{action.action}但被神秘力量阻止",
            {"blocked_action": action.model_dump()}
        )
    
    def _prepare_world_context(self) -> Dict[str, Any]:
        """为规则评估准备世界上下文"""
        state = self.game_mgr.state
        
        # 计算平均恐惧值
        alive_npcs = self.game_mgr.get_alive_npcs()
        if alive_npcs:
            avg_fear = sum(npc.get("fear", 0) for npc in alive_npcs) / len(alive_npcs)
        else:
            avg_fear = 50
        
        return {
            "rule_count": len(self.game_mgr.rules),
            "avg_fear": avg_fear,
            "places": self._get_available_places(),
            "difficulty": state.difficulty,
            "current_turn": state.current_turn,
            "time_of_day": state.time_of_day
        }
