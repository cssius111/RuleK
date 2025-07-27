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


@dataclass
class GameState:
    """游戏状态数据类"""
    # 基础信息
    game_id: str
    started_at: datetime = field(default_factory=datetime.now)
    current_turn: int = 0
    
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
    turn: int = 0  # 当前回合（与current_turn同步）
    
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
            "fear_points": self.fear_points,
            "phase": self.phase.value,
            "mode": self.mode.value,
            "time_of_day": self.time_of_day,
            "total_fear_gained": self.total_fear_gained,
            "npcs_died": self.npcs_died,
            "rules_triggered": self.rules_triggered,
            "difficulty": self.difficulty,
            "npcs": self.npcs
        }


class GameStateManager:
    """游戏状态管理器"""
    
    def __init__(self, save_dir: str = "data/saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.state: Optional[GameState] = None
        self.rules: List[Any] = []  # 将存储Rule对象
        self.npcs: List[Dict[str, Any]] = []
        self.spirits: List[Dict[str, Any]] = []
        self.game_log: List[str] = []
        
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
            save_file = self.save_dir / filename
        else:
            save_file = self.save_dir / f"{self.state.game_id}.json"
        
        try:
            # 转换NPC对象为纯字典
            serialized_state_npcs = {}
            for npc_id, npc in self.state.npcs.items():
                if hasattr(npc, "model_dump"):
                    serialized_state_npcs[npc_id] = npc.model_dump()
                elif hasattr(npc, "dict"):
                    serialized_state_npcs[npc_id] = npc.dict()
                elif isinstance(npc, dict):
                    serialized_state_npcs[npc_id] = npc
                else:
                    serialized_state_npcs[npc_id] = npc.__dict__

            serialized_npcs = []
            for npc in self.npcs:
                if hasattr(npc, "model_dump"):
                    serialized_npcs.append(npc.model_dump())
                elif hasattr(npc, "dict"):
                    serialized_npcs.append(npc.dict())
                elif isinstance(npc, dict):
                    serialized_npcs.append(npc)
                else:
                    serialized_npcs.append(npc.__dict__)

            state_data = self.state.to_dict()
            state_data["npcs"] = serialized_state_npcs

            save_data = {
                "state": state_data,
                "rules": [r.dict() if hasattr(r, 'dict') else r for r in self.rules],
                "npcs": serialized_npcs,
                "spirits": self.spirits,
                "game_log": self.game_log[-100:],  # 只保存最近100条日志
                "saved_at": datetime.now().isoformat()
            }
            
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
                
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
        self._trigger_event("turn_start", {"turn": self.state.current_turn})
        
        # 更新时间
        time_progression = ["morning", "afternoon", "evening", "night"]
        current_index = time_progression.index(self.state.time_of_day)
        self.state.time_of_day = time_progression[(current_index + 1) % 4]
        
        self.log(f"\n{'='*50}")
        self.log(f"第 {self.state.current_turn} 回合 - {self.get_time_display()}")
        self.log(f"当前恐惧点数: {self.state.fear_points}")
        
    def change_phase(self, new_phase: GamePhase):
        """改变游戏阶段"""
        old_phase = self.state.phase
        self.state.phase = new_phase
        self.log(f"阶段转换: {old_phase.value} → {new_phase.value}")
        
    def add_fear_points(self, amount: int, source: str = "unknown"):
        """增加恐惧点数"""
        self.state.fear_points += amount
        self.state.total_fear_gained += amount
        self.log(f"获得 {amount} 恐惧点数 (来源: {source})")
        self._trigger_event("fear_gained", {"amount": amount, "source": source})
        
    def spend_fear_points(self, amount: int) -> bool:
        """消耗恐惧点数"""
        if self.state.fear_points >= amount:
            self.state.fear_points -= amount
            return True
        return False
        
    def add_rule(self, rule: Any):
        """添加规则"""
        self.rules.append(rule)
        self.log(f"规则 [{rule.name}] 已添加到游戏中")
        
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
        for i, npc in enumerate(self.npcs):
            if npc.get("id") == npc_id:
                dead_npc = self.npcs.pop(i)
                if self.state:
                    self.state.npcs.pop(npc_id, None)
                self.state.npcs_died += 1
                self.log(f"NPC [{dead_npc['name']}] 已死亡")
                self._trigger_event("npc_died", {"npc": dead_npc})
                break
                
    def get_active_npcs(self) -> List[Dict[str, Any]]:
        """获取存活的NPC列表"""
        return [npc for npc in self.npcs if npc.get("hp", 0) > 0]
        
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
        return {
            "turns_played": self.current_turn,
            "fear_points_final": self.state.fear_points,
            "total_fear_gained": self.state.total_fear_gained,
            "npcs_died": self.state.npcs_died,
            "rules_created": len(self.rules),
            "rules_triggered": self.state.rules_triggered,
            "survival_rate": f"{len(self.get_active_npcs())}/{len(self.npcs)}"
        }

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
                    "location": "living_room"
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
