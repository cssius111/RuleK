"""
游戏状态管理器
负责管理整个游戏的状态，包括积分、规则、NPC等
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import json
from pathlib import Path

from .enums import GamePhase, GameMode
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ai.turn_pipeline import AITurnPipeline


@dataclass
class GameState:
    """游戏状态数据类"""
    # 基础信息
    game_id: str
    started_at: datetime = field(default_factory=datetime.now)
    current_turn: int = 0
    day: int = 1
    
    # 资源
    fear_points: int = 1000
    
    # 游戏阶段
    phase: GamePhase = GamePhase.SETUP
    time_of_day: str = "morning"  # morning, afternoon, evening, night
    mode: GameMode = GameMode.BACKSTAGE
    
    # 统计
    total_fear_gained: int = 0
    npcs_died: int = 0
    rules_triggered: int = 0

    # 规则
    active_rules: List[str] = field(default_factory=list)
    events_history: List[Dict[str, Any]] = field(default_factory=list)

    # 兼容旧字段
    @property
    def current_time(self) -> str:
        """向后兼容的时间字段"""
        return self.time_of_day

    @current_time.setter
    def current_time(self, value: str):
        self.time_of_day = value

    @property
    def event_log(self) -> List[Dict[str, Any]]:
        """向后兼容的事件日志字段"""
        return self.events_history

    @event_log.setter
    def event_log(self, value: List[Dict[str, Any]]):
        self.events_history = value

    @property
    def turn(self) -> int:
        """向后兼容的回合属性"""
        return self.current_turn

    @turn.setter
    def turn(self, value: int):
        self.current_turn = value
    
    # 角色
    npcs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # 游戏设置
    difficulty: str = "normal"  # easy, normal, hard
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "game_id": self.game_id,
            "started_at": self.started_at.isoformat(),
            "current_turn": self.current_turn,
            "turn": self.turn,
            "day": self.day,
            "fear_points": self.fear_points,
            "phase": self.phase.value,
            "mode": self.mode.value,
            "time_of_day": self.time_of_day,
            "current_time": self.current_time,
            "active_rules": self.active_rules,
            "events_history": self.events_history,
            "total_fear_gained": self.total_fear_gained,
            "npcs_died": self.npcs_died,
            "rules_triggered": self.rules_triggered,
            "difficulty": self.difficulty,
            "npcs": self.npcs
        }


class GameStateManager:
    """游戏状态管理器"""
    
    def __init__(self, save_dir: str = "data/saves", config: Dict[str, Any] = None):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.state: Optional[GameState] = None
        self.rules: List[Any] = []  # 将存储Rule对象
        self.npcs: List[Dict[str, Any]] = []
        self.spirits: List[Dict[str, Any]] = []
        self.game_log: List[str] = []
        
        # 配置
        self.config = config or {}
        self.ai_enabled = self.config.get("ai_enabled", False)
        self.ai_pipeline: Optional['AITurnPipeline'] = None
        
        # 事件监听器
        self.event_listeners = {
            "turn_start": [],
            "turn_end": [],
            "rule_triggered": [],
            "npc_died": [],
            "fear_gained": []
        }
        
    def new_game(self, game_id: Optional[str] = None, config: Dict[str, Any] = None) -> GameState:
        """开始新游戏

        Args:
            game_id: 游戏ID，如未提供则使用当前时间生成
            config: 游戏配置
        """
        if game_id is None:
            game_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        config = config or {}
        
        self.state = GameState(
            game_id=game_id,
            fear_points=config.get("initial_fear_points", 1000),
            difficulty=config.get("difficulty", "normal"),
            phase=GamePhase.SETUP,
            mode=GameMode.BACKSTAGE,
        )
        self.state.turn = self.state.current_turn
        self.state.day = 1
        self.state.npcs = {}
        
        self.rules = []
        self.npcs = []
        self.spirits = []
        self.game_log = []
        
        self.log(f"新游戏开始 - ID: {game_id}")
        self._trigger_event("game_start", {"state": self.state})
        
        # 创建默认NPC
        self._create_default_npcs()
        
        return self.state
    
    def _serialize_npc(self, npc: Any) -> Dict[str, Any]:
        """序列化NPC对象为可保存的字典格式"""
        if isinstance(npc, dict):
            # 处理字典中的嵌套对象
            result = {}
            for key, value in npc.items():
                if hasattr(value, 'dict'):  # Pydantic模型
                    result[key] = value.model_dump()
                elif hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    # 其他对象
                    result[key] = value.__dict__
                else:
                    result[key] = value
            return result
        elif hasattr(npc, "model_dump"):
            return npc.model_dump()
        elif hasattr(npc, "dict"):
            return npc.model_dump()
        elif hasattr(npc, "__dict__"):
            # 递归处理嵌套对象
            return self._serialize_npc(npc.__dict__)
        else:
            return npc
    
    def _serialize_rule(self, rule: Any) -> Dict[str, Any]:
        """序列化规则对象为可保存的字典格式"""
        if isinstance(rule, dict):
            return rule
        elif hasattr(rule, "model_dump"):
            return rule.model_dump()
        elif hasattr(rule, "dict"):
            return rule.model_dump()
        elif hasattr(rule, "__dict__"):
            # 处理自定义类对象
            result = {}
            for key, value in rule.__dict__.items():
                if key.startswith("_"):  # 跳过私有属性
                    continue
                if hasattr(value, "value"):  # 处理枚举
                    result[key] = value.value
                elif hasattr(value, "dict"):  # 处理嵌套的 Pydantic 模型
                    result[key] = value.model_dump()
                elif hasattr(value, "__dict__") and not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    result[key] = self._serialize_rule(value)
                else:
                    result[key] = value
            return result
        else:
            return str(rule)  # 最后的选择：转换为字符串
        
    def load_game(self, game_id: str) -> bool:
        """加载游戏存档"""
        save_file = self.save_dir / f"{game_id}.json"
        
        if not save_file.exists():
            return False
            
        try:
            with open(save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # 恢复游戏状态
            self.state = GameState(
                game_id=data["state"]["game_id"],
                started_at=datetime.fromisoformat(data["state"]["started_at"]),
                current_turn=data["state"]["current_turn"],
                fear_points=data["state"]["fear_points"],
                phase=GamePhase(data["state"].get("phase", GamePhase.SETUP.value)),
                time_of_day=data["state"]["time_of_day"],
                mode=GameMode(data["state"].get("mode", GameMode.BACKSTAGE.value)),
                total_fear_gained=data["state"]["total_fear_gained"],
                npcs_died=data["state"]["npcs_died"],
                rules_triggered=data["state"]["rules_triggered"],
                difficulty=data["state"]["difficulty"]
            )
            self.state.turn = self.state.current_turn
            self.state.day = data["state"].get("day", 1)
            self.state.active_rules = data["state"].get("active_rules", [])
            self.state.events_history = data["state"].get("events_history", [])
            
            self.rules = data.get("rules", [])
            self.npcs = list(data.get("state", {}).get("npcs", {}).values())
            self.state.npcs = data.get("state", {}).get("npcs", {})
            self.spirits = data.get("spirits", [])
            self.game_log = data.get("game_log", [])
            
            self.log(f"游戏读取成功 - 第{self.current_turn}回合")
            return True
            
        except Exception as e:
            print(f"读取存档失败: {e}")
            return False
            
    def save_game(self, filename: Optional[str] = None) -> Optional[str]:
        """保存游戏

        Returns the path to the saved file if successful, otherwise ``None``.
        """
        if not self.state:
            return None
            
        if filename:
            # 检查文件名是否已经包含.json扩展名
            if not filename.endswith('.json'):
                save_file = self.save_dir / f"{filename}.json"
            else:
                save_file = self.save_dir / filename
        else:
            save_file = self.save_dir / f"{self.state.game_id}.json"
        
        try:
            # 转换NPC对象为纯字典
            serialized_state_npcs = {}
            for npc_id, npc in self.state.npcs.items():
                serialized_state_npcs[npc_id] = self._serialize_npc(npc)

            serialized_npcs = []
            for npc in self.npcs:
                serialized_npcs.append(self._serialize_npc(npc))

            state_data = self.state.to_dict()
            state_data["npcs"] = serialized_state_npcs

            # 序列化规则
            serialized_rules = []
            for rule in self.rules:
                serialized_rules.append(self._serialize_rule(rule))

            save_data = {
                "state": state_data,
                "rules": serialized_rules,
                "npcs": serialized_npcs,
                "spirits": self.spirits,
                "game_log": self.game_log[-100:],  # 只保存最近100条日志
                "saved_at": datetime.now().isoformat()
            }
            
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False, default=str)
                
            self.log("游戏已保存")
            return str(save_file)
            
        except Exception as e:
            print(f"保存游戏失败: {e}")
            return None
            
    def advance_turn(self):
        """推进回合"""
        if not self.state:
            raise RuntimeError("游戏未初始化")

        self.state.current_turn += 1
        self.state.turn = self.state.current_turn
        self._trigger_event("turn_start", {"turn": self.state.current_turn})

        # 更新时间
        time_progression = ["morning", "afternoon", "evening", "night"]
        current_index = time_progression.index(self.state.time_of_day)
        self.state.time_of_day = time_progression[(current_index + 1) % 4]
        if current_index == len(time_progression) - 1:
            self.state.day += 1
        
        self.log(f"\n{'='*50}")
        self.log(f"第 {self.state.current_turn} 回合 - {self.get_time_display()}")
        self.log(f"当前恐惧点数: {self.state.fear_points}")
        
    def change_phase(self, new_phase: GamePhase):
        """改变游戏阶段"""
        if self.state is None:
            raise RuntimeError("游戏未初始化")
        state: GameState = self.state
        old_phase = state.phase
        state.phase = new_phase
        self.log(f"阶段转换: {old_phase.value} → {new_phase.value}")
        
    def add_fear_points(self, amount: int, source: str = "unknown"):
        """增加恐惧点数"""
        if self.state is None:
            raise RuntimeError("游戏未初始化")
        state: GameState = self.state
        state.fear_points += amount
        state.total_fear_gained += amount
        self.log(f"获得 {amount} 恐惧点数 (来源: {source})")
        self._trigger_event("fear_gained", {"amount": amount, "source": source})
        
    def spend_fear_points(self, amount: int) -> bool:
        """消耗恐惧点数"""
        if self.state is None:
            raise RuntimeError("游戏未初始化")
        state: GameState = self.state
        if state.fear_points >= amount:
            state.fear_points -= amount
            return True
        return False
        
    def add_rule(self, rule: Any):
        """添加规则
        
        Returns:
            bool: 是否添加成功
        """
        self.rules.append(rule)
        if self.state:
            self.state.active_rules.append(rule.id)
        self.log(f"规则 [{rule.name}] 已添加到游戏中")
        return True
        
    def add_npc(self, npc: Dict[str, Any]):
        """添加NPC"""
        self.npcs.append(npc)
        if self.state:
            self.state.npcs[npc.get("id")] = npc
        self.log(f"NPC [{npc['name']}] 加入游戏")
        
    def update_npc(self, npc_id: str, updates: Dict[str, Any]):
        """更新NPC状态"""
        for npc in self.npcs:
            if npc.get("id") == npc_id:
                npc.update(updates)
                break
        if self.state and npc_id in self.state.npcs:
            self.state.npcs[npc_id].update(updates)
                
    def remove_npc(self, npc_id: str):
        """移除NPC（死亡）"""
        if self.state is None:
            raise RuntimeError("游戏未初始化")
        state: GameState = self.state
        for i, npc in enumerate(self.npcs):
            if npc.get("id") == npc_id:
                dead_npc = self.npcs.pop(i)
                state.npcs.pop(npc_id, None)
                state.npcs_died += 1
                self.log(f"NPC [{dead_npc['name']}] 已死亡")
                self._trigger_event("npc_died", {"npc": dead_npc})
                break
                
    def get_active_npcs(self) -> List[Dict[str, Any]]:
        """获取存活的NPC列表"""
        return [npc for npc in self.npcs if npc.get("hp", 0) > 0]

    def get_npcs_in_location(self, location: str) -> List[Dict[str, Any]]:
        """获取指定位置的NPC"""
        return [npc for npc in self.npcs
                if npc.get("location") == location]

    def get_alive_npcs(self) -> List[Dict[str, Any]]:
        """获取仍然存活且未被标记为死亡的NPC"""
        return [
            npc for npc in self.npcs
            if npc.get("hp", 0) > 0 and npc.get("alive", True) is not False
        ]
        
    def get_active_rules(self) -> List[Any]:
        """获取激活的规则列表"""
        return [rule for rule in self.rules if getattr(rule, 'active', True)]
        
    def log(self, message: str):
        """添加游戏日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.game_log.append(log_entry)
        print(log_entry)  # 同时输出到控制台
        
    def get_time_display(self) -> str:
        """获取时间显示文本"""
        if self.state is None:
            return "未知"
        time_map = {
            "morning": "早晨 ☀️",
            "afternoon": "下午 🌤️",
            "evening": "傍晚 🌅",
            "night": "深夜 🌙"
        }
        return time_map.get(self.state.time_of_day, "未知")
        
    def register_event_listener(self, event: str, callback):
        """注册事件监听器"""
        if event in self.event_listeners:
            self.event_listeners[event].append(callback)
            
    def _trigger_event(self, event: str, data: Dict[str, Any]):
        """触发事件"""
        if event in self.event_listeners:
            for callback in self.event_listeners[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"事件处理出错 {event}: {e}")
                    
    @property
    def current_turn(self) -> int:
        """当前回合数"""
        return self.state.current_turn if self.state else 0
        
    @property
    def difficulty(self) -> str:
        """获取当前游戏难度"""
        return self.state.difficulty if self.state else "normal"
        
    @property
    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        if not self.state:
            return True
            
        # 所有NPC死亡
        if len(self.get_active_npcs()) == 0:
            return True
            
        # 回合数超过限制（可配置）
        if self.current_turn >= 50:
            return True
            
        return False
        
    def get_summary(self) -> Dict[str, Any]:
        """获取游戏总结"""
        if self.state is None:
            raise RuntimeError("游戏未初始化")
        state: GameState = self.state
        return {
            "turns_played": self.current_turn,
            "fear_points_final": state.fear_points,
            "total_fear_gained": state.total_fear_gained,
            "npcs_died": state.npcs_died,
            "rules_created": len(self.rules),
            "rules_triggered": state.rules_triggered,
            "survival_rate": f"{len(self.get_active_npcs())}/{len(self.npcs)}"
        }
    
    # ========== AI集成方法 ==========
    
    async def init_ai_pipeline(self):
        """初始化AI管线"""
        if self.ai_enabled:
            try:
                from src.api.deepseek_client import DeepSeekClient, APIConfig
                from src.ai.turn_pipeline import AITurnPipeline
                
                # 创建DeepSeek客户端
                api_config = APIConfig()
                ds_client = DeepSeekClient(api_config)
                
                # 创建AI管线
                self.ai_pipeline = AITurnPipeline(self, ds_client)
                self.log("AI管线初始化成功")
                return True
            except Exception as e:
                self.log(f"AI管线初始化失败: {str(e)}")
                self.ai_enabled = False
                return False
        return False
    
    async def run_ai_turn(self, force_dialogue: bool = True):
        """运行AI驱动的回合"""
        if not self.ai_pipeline:
            self.log("AI未启用或未初始化")
            return None
        
        try:
            # 执行AI回合
            plan = await self.ai_pipeline.run_turn_ai(force_dialogue=force_dialogue)
            self.log(f"AI回合执行完成，生成{len(plan.dialogue)}条对话，{len(plan.actions)}个行动")
            return plan
        except Exception as e:
            self.log(f"AI回合执行失败: {str(e)}")
            return None
    
    async def generate_narrative(self, include_hidden: bool = False) -> str:
        """生成回合叙事"""
        if not self.ai_pipeline:
            return "AI叙事生成未启用"
        
        try:
            narrative = await self.ai_pipeline.generate_turn_narrative(
                include_hidden_events=include_hidden
            )
            return narrative
        except Exception as e:
            self.log(f"叙事生成失败: {str(e)}")
            return "叙事生成失败，请查看日志"
    
    async def evaluate_rule_nl(self, rule_description: str) -> Dict[str, Any]:
        """评估自然语言规则"""
        if not self.ai_pipeline:
            return {
                "error": "AI未启用",
                "suggestion": "请先启用AI功能"
            }
        
        try:
            result = await self.ai_pipeline.evaluate_player_rule(rule_description)
            return result
        except Exception as e:
            self.log(f"规则评估失败: {str(e)}")
            return {
                "error": str(e),
                "suggestion": "请尝试更清晰地描述规则"
            }
    
    def get_npc_states_for_ai(self) -> List[Dict[str, Any]]:
        """为AI准备NPC状态数据"""
        npc_states = []
        for npc in self.get_active_npcs():
            npc_state = {
                "name": npc.get("name", "未知"),
                "fear": npc.get("fear", 0),
                "sanity": npc.get("sanity", 100),
                "traits": npc.get("traits", []),
                "status": npc.get("status", "正常"),
                "location": npc.get("location", "未知位置"),
                "inventory": npc.get("inventory", [])
            }
            npc_states.append(npc_state)
        return npc_states
    
    def get_scene_context_for_ai(self) -> Dict[str, Any]:
        """为AI准备场景上下文"""
        if not self.state:
            return {}
        
        # 获取最近事件
        recent_events = self.state.events_history[-5:] if self.state.events_history else []
        recent_event_descriptions = []
        for event in recent_events:
            if isinstance(event, dict):
                desc = event.get("description", str(event))
            else:
                desc = str(event)
            recent_event_descriptions.append(desc)
        
        # 构建上下文
        context = {
            "current_location": "游戏世界",  # TODO: 实现具体位置追踪
            "recent_events": recent_event_descriptions,
            "active_rules": self.state.active_rules,
            "ambient_fear_level": self._calculate_ambient_fear(),
            "special_conditions": self._get_special_conditions()
        }
        
        return context
    
    def _calculate_ambient_fear(self) -> int:
        """计算环境恐惧等级"""
        base_fear = 30
        
        # 时间因素
        if self.state and self.state.time_of_day == "night":
            base_fear += 20
        
        # 死亡事件影响
        if self.state:
            base_fear += self.state.npcs_died * 10
        
        # 规则数量影响
        base_fear += len(self.rules) * 5
        
        return min(100, base_fear)
    
    def _get_special_conditions(self) -> List[str]:
        """获取特殊条件"""
        conditions = []
        
        if self.state:
            # 时间条件
            if self.state.time_of_day == "night":
                conditions.append("深夜时分")
            
            # 生存状况
            alive_count = len(self.get_active_npcs())
            if alive_count <= 2:
                conditions.append("仅剩少数幸存者")
            
            # 恐惧等级
            avg_fear = sum(npc.get("fear", 0) for npc in self.get_active_npcs()) / max(alive_count, 1)
            if avg_fear > 70:
                conditions.append("集体恐慌")
        
        return conditions
    
    async def close_ai(self):
        """关闭AI客户端"""
        if self.ai_pipeline and hasattr(self.ai_pipeline, 'ds_client'):
            await self.ai_pipeline.ds_client.close()
            self.log("AI客户端已关闭")

    def _create_default_npcs(self):
        """创建默认NPC"""
        try:
            from ..models.npc import generate_random_npc
            
            default_npc_names = ["张三", "李四", "王五"]
            for name in default_npc_names:
                npc = generate_random_npc(name)
                npc_dict = npc.__dict__ if hasattr(npc, '__dict__') else npc
                self.add_npc(npc_dict)
        except ImportError:
            # 如果无法导入NPC模块，创建简单的NPC
            for i, name in enumerate(["张三", "李四", "王五"]):
                simple_npc = {
                    "id": f"npc_{i+1}",
                    "name": name,
                    "hp": 100,
                    "sanity": 100,
                    "fear": 0,
                    "location": "living_room",
                    "alive": True
                }
                self.add_npc(simple_npc)


# 单元测试
if __name__ == "__main__":
    # 测试游戏状态管理器
    gsm = GameStateManager()
    
    # 创建新游戏
    state = gsm.new_game("test_game_001")
    print(f"游戏创建成功: {state.game_id}")
    
    # 添加NPC
    gsm.add_npc({"id": "npc_1", "name": "测试员1", "hp": 100})
    gsm.add_npc({"id": "npc_2", "name": "测试员2", "hp": 100})
    
    # 推进几个回合
    for i in range(3):
        gsm.advance_turn()
        gsm.add_fear_points(50, "测试触发")
        
    # 保存游戏
    gsm.save_game()
    
    # 显示总结
    summary = gsm.get_summary()
    print(f"\n游戏总结: {summary}")
