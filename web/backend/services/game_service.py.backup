"""
游戏服务层
封装游戏逻辑，提供API接口
"""
import asyncio
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from fastapi import WebSocket
import json
import uuid
import logging
from pathlib import Path

from src.core.game_state import GameState, GameStateManager
from src.ai.turn_pipeline import AITurnPipeline
from src.models.rule import Rule
from src.models.rule_manager import RuleManager
from src.models import NPC, NPCManager
from src.core.narrator import Narrator
from src.core.dialogue_system import DialogueSystem
from src.core.event_system import EventSystem
from src.models.map import MapManager
from src.core.npc_behavior import NPCBehavior
from src.core.rule_executor import RuleExecutor
from src.api.deepseek_client import DeepSeekClient
from src.utils.config import load_config

from ..models import GameStateResponse, NPCStatus, RuleInfo, TurnResult, GameUpdate

logger = logging.getLogger(__name__)


class GameService:
    """游戏服务类"""
    
    def __init__(self, game_id: str = None, difficulty: str = "normal", npc_count: int = 4):
        """初始化游戏服务"""
        self.game_id = game_id or f"game_{uuid.uuid4().hex[:8]}"
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        
        # 游戏配置
        self.difficulty = difficulty
        self.npc_count = npc_count
        
        # WebSocket连接管理
        self.websockets: Dict[str, WebSocket] = {}
        self._ws_lock = asyncio.Lock()
        
        # 初始化标志
        self._initialized = False
        
        # AI相关
        self.ai_enabled = False
        self.ai_pipeline = None
        self.game_state_manager = None
    
    async def initialize(self):
        """异步初始化游戏组件"""
        if self._initialized:
            return
        
        # 加载配置
        self.config = load_config()
        
        # 初始化游戏状态管理器
        # 从 Config 对象中提取配置信息
        save_dir = self.config.get('save_dir', 'data/saves')
        
        # 获取游戏配置 - 处理嵌套结构
        game_cfg = self.config._config.get('game', {}) if hasattr(self.config, '_config') else {}
        game_config = {
            'initial_fear_points': game_cfg.get('initial_fear_points', 1000),
            'ai_enabled': game_cfg.get('ai_enabled', False),
            'difficulty': self.difficulty
        }
        self.game_state_manager = GameStateManager(save_dir=save_dir, config=game_config)
        self.game_state_manager.new_game(self.game_id)
        self.game_state = self.game_state_manager.state
        
        # 初始化地图
        self.map_manager = MapManager()
        self.map_manager.create_default_map()
        
        # 初始化管理器
        self.rule_manager = RuleManager()
        self.npc_manager = NPCManager()
        self.event_system = EventSystem()
        self.npc_behavior = NPCBehavior(self.game_state_manager)
        self.rule_executor = RuleExecutor(self.game_state_manager)
        
        # 初始化AI系统
        self.deepseek_client = DeepSeekClient()
        self.dialogue_system = DialogueSystem(self.deepseek_client)
        self.narrator = Narrator(self.deepseek_client)
        
        # 创建NPC
        self._create_npcs()
        
        self._initialized = True
        logger.info(f"Game service initialized: {self.game_id}")
    
    def _create_npcs(self):
        """创建NPC"""
        for i in range(self.npc_count):
            npc = self.npc_manager.create_npc(
                name=f"NPC_{i+1}",  # 实际游戏中会用AI生成名字
                rationality=5 + (i % 3),
                courage=3 + (i % 4),
                curiosity=4 + (i % 3)
            )
            # 随机放置在不同房间
            areas = list(self.map_manager.areas.keys())
            npc.location = areas[i % len(areas)]
            
            # 添加到游戏状态
            self.game_state.npcs[npc.id] = npc.to_dict()
    
    def update_last_accessed(self):
        """更新最后访问时间"""
        self.last_accessed = datetime.now()
    
    def is_active(self) -> bool:
        """检查游戏是否活跃（有WebSocket连接）"""
        return len(self.websockets) > 0
    
    def get_state_response(self) -> GameStateResponse:
        """获取游戏状态响应"""
        npcs_status = []
        for npc_id, npc_data in self.game_state.npcs.items():
            npcs_status.append(NPCStatus(
                id=npc_id,
                name=npc_data.get("name", "Unknown"),
                hp=npc_data.get("hp", 100),
                sanity=npc_data.get("sanity", 100),
                fear=npc_data.get("fear", 0),
                location=npc_data.get("location", "unknown"),
                status_effects=npc_data.get("status_effects", []),
                is_alive=npc_data.get("hp", 100) > 0
            ))
        
        return GameStateResponse(
            game_id=self.game_id,
            started_at=self.game_state.started_at,
            current_turn=self.game_state.current_turn,
            fear_points=self.game_state.fear_points,
            phase=self.game_state.phase.value,
            mode=self.game_state.mode.value,
            time_of_day=self.game_state.time_of_day,
            npcs=npcs_status,
            active_rules=len(self.rule_manager.active_rules),
            total_fear_gained=self.game_state.total_fear_gained,
            npcs_died=self.game_state.npcs_died
        )
    
    async def advance_turn(self) -> TurnResult:
        """推进游戏回合"""
        self.update_last_accessed()
        
        # 更新回合数
        self.game_state.current_turn += 1
        events = []
        fear_gained = 0
        npcs_affected = []
        rules_triggered = []
        
        # 1. 对话阶段（早晚各一次）
        if self.game_state.time_of_day in ["morning", "evening"]:
            dialogue_events = await self._run_dialogue_phase()
            events.extend(dialogue_events)
        
        # 2. NPC行动阶段
        for npc_id, npc_data in self.game_state.npcs.items():
            if npc_data.get("hp", 0) > 0:
                npc = self.npc_manager.get_npc(npc_id)
                if npc:
                    action = self.npc_behavior.decide_action(npc, self.game_state)
                    if action:
                        events.append({
                            "type": "npc_action",
                            "npc": npc.name,
                            "action": action
                        })
        
        # 3. 规则判定阶段
        for rule in self.rule_manager.active_rules:
            result = self.rule_executor.execute(rule, self.game_state)
            if result:
                rules_triggered.append(rule.id)
                fear_gained += result.get("fear_gain", 0)
                npcs_affected.extend(result.get("affected_npcs", []))
                events.append({
                    "type": "rule_triggered",
                    "rule": rule.name,
                    "result": result
                })
        
        # 4. 随机事件
        random_event = self.event_system.trigger_random_event(
            self.game_state.current_turn,
            self.game_state.fear_points
        )
        if random_event:
            events.append(random_event)
        
        # 5. 生成叙事
        narrative = None
        if events:
            narrative = await self.narrator.generate_narrative(events, self.game_state)
        
        # 更新游戏状态
        self.game_state.fear_points += fear_gained
        self.game_state.total_fear_gained += fear_gained
        
        # 推进时间
        self._advance_time()
        
        # 广播更新
        await self.broadcast_update({
            "update_type": "state",
            "data": self.get_state_response().dict()
        })
        
        return TurnResult(
            turn=self.game_state.current_turn,
            events=events,
            fear_gained=fear_gained,
            npcs_affected=list(set(npcs_affected)),
            rules_triggered=rules_triggered,
            narrative=narrative
        )
    
    async def _run_dialogue_phase(self) -> List[Dict]:
        """运行对话阶段"""
        events = []
        npcs = [self.npc_manager.get_npc(npc_id) 
                for npc_id in self.game_state.npcs 
                if self.game_state.npcs[npc_id].get("hp", 0) > 0]
        
        if len(npcs) >= 2:
            # 生成对话
            dialogue = await self.dialogue_system.generate_dialogue(
                npcs[:2],  # 选择前两个NPC对话
                {"time": self.game_state.time_of_day}
            )
            
            events.append({
                "type": "dialogue",
                "participants": [npc.name for npc in npcs[:2]],
                "content": dialogue
            })
            
            # 广播对话更新
            await self.broadcast_update({
                "update_type": "dialogue",
                "data": dialogue
            })
        
        return events
    
    def _advance_time(self):
        """推进游戏时间"""
        time_sequence = ["morning", "afternoon", "evening", "night"]
        current_index = time_sequence.index(self.game_state.time_of_day)
        next_index = (current_index + 1) % len(time_sequence)
        self.game_state.time_of_day = time_sequence[next_index]
    
    async def create_rule(self, rule_data: Dict) -> str:
        """创建新规则"""
        self.update_last_accessed()
        
        # 检查积分是否足够
        if self.game_state.fear_points < rule_data["cost"]:
            raise ValueError("Not enough fear points")
        
        # 创建规则
        rule = Rule(**rule_data)
        self.rule_manager.add_rule(rule)
        
        # 扣除积分
        self.game_state.fear_points -= rule_data["cost"]
        
        # 广播更新
        await self.broadcast_update({
            "update_type": "rule",
            "data": {
                "action": "created",
                "rule": rule.to_dict()
            }
        })
        
        return rule.id
    
    def get_rules(self) -> List[RuleInfo]:
        """获取规则列表"""
        rules = []
        for rule in self.rule_manager.active_rules:
            rules.append(RuleInfo(
                id=rule.id,
                name=rule.name,
                description=rule.description,
                level=rule.level,
                cost=rule.cost.get("base", 0),
                is_active=rule.status == "active",
                times_triggered=rule.times_triggered,
                loopholes=rule.loopholes
            ))
        return rules
    
    def get_npcs(self) -> List[NPCStatus]:
        """获取NPC列表"""
        npcs = []
        for npc_id, npc_data in self.game_state.npcs.items():
            npcs.append(NPCStatus(
                id=npc_id,
                name=npc_data.get("name", "Unknown"),
                hp=npc_data.get("hp", 100),
                sanity=npc_data.get("sanity", 100),
                fear=npc_data.get("fear", 0),
                location=npc_data.get("location", "unknown"),
                status_effects=npc_data.get("status_effects", []),
                is_alive=npc_data.get("hp", 100) > 0
            ))
        return npcs
    
    async def save_game(self) -> str:
        """保存游戏"""
        save_dir = Path("data/saves")
        save_dir.mkdir(exist_ok=True)
        
        filename = f"save_{self.game_id}_{datetime.now():%Y%m%d_%H%M%S}.json"
        save_path = save_dir / filename
        
        save_data = {
            "version": "1.0",
            "game_id": self.game_id,
            "created_at": self.created_at.isoformat(),
            "saved_at": datetime.now().isoformat(),
            "game_state": self.game_state.to_dict(),
            "managers": {
                "rules": [rule.to_dict() for rule in self.rule_manager.active_rules],
                "npcs": {npc_id: npc.to_dict() 
                        for npc_id, npc in self.npc_manager.npcs.items()},
                "map": self.map_manager.to_dict()
            }
        }
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Game saved: {filename}")
        return filename
    
    @classmethod
    def load_from_file(cls, filename: str) -> "GameService":
        """从文件加载游戏"""
        save_path = Path("data/saves") / filename
        if not save_path.exists():
            raise FileNotFoundError(f"Save file not found: {filename}")
        
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # 创建游戏服务实例
        game_service = cls(game_id=save_data["game_id"])
        
        # 恢复游戏状态
        game_service.game_state = GameState(**save_data["game_state"])
        game_service.created_at = datetime.fromisoformat(save_data["created_at"])
        
        # 恢复管理器状态会在 initialize() 中完成
        game_service._save_data = save_data["managers"]
        
        return game_service
    
    # ==================== WebSocket管理 ====================
    
    async def add_websocket(self, websocket: WebSocket) -> str:
        """添加WebSocket连接"""
        connection_id = str(uuid.uuid4())
        async with self._ws_lock:
            self.websockets[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")
        return connection_id
    
    async def remove_websocket(self, connection_id: str):
        """移除WebSocket连接"""
        async with self._ws_lock:
            if connection_id in self.websockets:
                del self.websockets[connection_id]
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def broadcast_update(self, update: Dict):
        """广播更新给所有连接的客户端"""
        if not self.websockets:
            return
        
        message = GameUpdate(
            update_type=update["update_type"],
            game_id=self.game_id,
            data=update.get("data", {})
        )
        
        disconnected = []
        async with self._ws_lock:
            for conn_id, ws in self.websockets.items():
                try:
                    await ws.send_json(message.dict())
                except Exception as e:
                    logger.error(f"Failed to send to {conn_id}: {e}")
                    disconnected.append(conn_id)
        
        # 清理断开的连接
        for conn_id in disconnected:
            await self.remove_websocket(conn_id)
    
    async def handle_action(self, action_data: Dict) -> Dict:
        """处理客户端动作"""
        self.update_last_accessed()
        
        action_type = action_data.get("action_type")
        
        if action_type == "advance_turn":
            result = await self.advance_turn()
            return result.dict()
        elif action_type == "create_rule":
            rule_id = await self.create_rule(action_data.get("rule_data", {}))
            return {"rule_id": rule_id}
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def cleanup(self):
        """清理资源"""
        # 关闭所有WebSocket连接
        async with self._ws_lock:
            for ws in self.websockets.values():
                try:
                    await ws.close()
                except:
                    pass
            self.websockets.clear()
        
        logger.info(f"Game service cleaned up: {self.game_id}")
    
    # ==================== AI功能集成 ====================
    
    async def init_ai_pipeline(self) -> bool:
        """初始化AI管线"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # 确保game_state_manager已经初始化
            if not hasattr(self, 'game_state_manager') or not self.game_state_manager:
                logger.error("GameStateManager not initialized")
                return False
            
            # 同步游戏状态
            self.game_state_manager.rules = self.rule_manager.active_rules
            self.game_state_manager.npcs = list(self.npc_manager.npcs.values())
            
            # 初始化AI管线
            self.ai_pipeline = AITurnPipeline(self.game_state_manager, self.deepseek_client)
            
            self.ai_enabled = True
            logger.info(f"AI pipeline initialized for game: {self.game_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI pipeline: {e}")
            self.ai_enabled = False
            return False
    
    def is_ai_enabled(self) -> bool:
        """检查AI是否启用"""
        return self.ai_enabled
    
    def is_ai_initialized(self) -> bool:
        """检查AI是否已初始化"""
        return self.ai_pipeline is not None
    
    async def run_ai_turn(self, force_dialogue: bool = True) -> Dict:
        """执行AI驱动的回合"""
        if not self.ai_enabled or not self.ai_pipeline:
            raise ValueError("AI not initialized")
        
        try:
            # 同步最新状态
            self._sync_state_to_manager()
            
            # 执行AI回合
            plan = await self.ai_pipeline.run_turn_ai()
            
            # 同步状态回游戏
            self._sync_state_from_manager()
            
            # 转换为响应格式
            from ..models import AITurnPlanResponse, AIDialogueResponse, AIActionResponse
            
            dialogue_responses = []
            for d in plan.dialogue:
                dialogue_responses.append(AIDialogueResponse(
                    speaker=d.speaker,
                    text=d.text,
                    emotion=getattr(d, 'emotion', None)
                ))
            
            action_responses = []
            for a in plan.actions:
                action_responses.append(AIActionResponse(
                    npc=a.npc,
                    action=a.action,
                    target=a.target,
                    reason=a.reason,
                    risk=a.risk,
                    priority=getattr(a, 'priority', 1)
                ))
            
            response = AITurnPlanResponse(
                dialogue=dialogue_responses,
                actions=action_responses,
                turn_summary=f"回合{self.game_state.current_turn}：生成了{len(dialogue_responses)}条对话和{len(action_responses)}个行动",
                atmosphere=self.game_state.time_of_day
            )
            
            # 广播AI生成的内容
            await self.broadcast_update({
                "update_type": "ai_turn",
                "data": response.dict()
            })
            
            return response.dict()
            
        except Exception as e:
            logger.error(f"AI turn execution failed: {e}")
            raise
    
    async def evaluate_rule_nl(self, rule_description: str) -> Dict:
        """评估自然语言规则"""
        if not self.ai_enabled or not self.ai_pipeline:
            raise ValueError("AI not initialized")
        
        try:
            result = await self.ai_pipeline.evaluate_player_rule(rule_description)
            
            from ..models import AIRuleEvaluationResponse
            response = AIRuleEvaluationResponse(
                name=result["name"],
                cost=result["cost"],
                difficulty=result["difficulty"],
                loopholes=result["loopholes"],
                suggestion=result["suggestion"],
                estimated_fear_gain=result.get("estimated_fear_gain"),
                parsed_rule=result["parsed_rule"]
            )
            
            return response.dict()
            
        except Exception as e:
            logger.error(f"Rule evaluation failed: {e}")
            raise
    
    async def generate_narrative(self, include_hidden: bool = False) -> str:
        """生成回合叙事"""
        if not self.ai_enabled or not self.ai_pipeline:
            raise ValueError("AI not initialized")
        
        try:
            narrative = await self.ai_pipeline.generate_turn_narrative()
            
            # 如果不包含隐藏事件，过滤掉某些内容
            if not include_hidden:
                # 这里可以添加过滤逻辑
                pass
            
            return narrative
            
        except Exception as e:
            logger.error(f"Narrative generation failed: {e}")
            raise
    
    def _sync_state_to_manager(self):
        """同步游戏状态到GameStateManager"""
        if not self.game_state_manager:
            return
        
        # 同步基本状态
        self.game_state_manager.state = self.game_state
        
        # 同步规则
        self.game_state_manager.rules = self.rule_manager.active_rules
        
        # 同步NPC（转换格式）
        npcs = []
        for npc_id, npc_data in self.game_state.npcs.items():
            npc_dict = {
                'id': npc_id,
                'name': npc_data.get('name', 'Unknown'),
                'hp': npc_data.get('hp', 100),
                'sanity': npc_data.get('sanity', 100),
                'fear': npc_data.get('fear', 0),
                'location': npc_data.get('location', 'unknown'),
                'traits': npc_data.get('traits', []),
                'status': npc_data.get('status', 'normal'),
                'is_alive': npc_data.get('hp', 100) > 0
            }
            npcs.append(npc_dict)
        self.game_state_manager.npcs = npcs
    
    def _sync_state_from_manager(self):
        """从GameStateManager同步状态回游戏"""
        if not self.game_state_manager:
            return
        
        # 同步事件历史
        self.game_state = self.game_state_manager.state
        
        # 同步NPC状态变化
        for npc in self.game_state_manager.npcs:
            if isinstance(npc, dict):
                npc_id = npc.get('id')
                if npc_id and npc_id in self.game_state.npcs:
                    self.game_state.npcs[npc_id].update({
                        'hp': npc.get('hp', 100),
                        'sanity': npc.get('sanity', 100),
                        'fear': npc.get('fear', 0),
                        'location': npc.get('location', 'unknown'),
                        'status': npc.get('status', 'normal')
                    })
