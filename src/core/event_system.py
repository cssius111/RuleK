"""
随机事件系统
增加游戏的不可预测性和氛围
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """事件类型枚举"""
    ENVIRONMENTAL = "environmental"    # 环境事件
    NPC_EVENT = "npc_event"           # NPC相关事件
    ITEM_EVENT = "item_event"         # 物品事件
    SUPERNATURAL = "supernatural"      # 超自然事件
    SYSTEM = "system"                 # 系统事件


class EventPriority(str, Enum):
    """事件优先级"""
    LOW = "low"          # 低优先级（氛围）
    MEDIUM = "medium"    # 中等优先级（影响游戏）
    HIGH = "high"        # 高优先级（重要）
    CRITICAL = "critical" # 关键（必须处理）


@dataclass
class EventTriggerCondition:
    """事件触发条件"""
    min_turn: int = 0
    max_turn: Optional[int] = None
    min_fear_average: int = 0
    max_fear_average: Optional[int] = None
    required_locations: List[str] = field(default_factory=list)
    required_npcs_alive: int = 1
    time_of_day: Optional[List[str]] = None
    probability: float = 1.0
    cooldown: int = 0  # 冷却回合数
    max_occurrences: Optional[int] = None  # 最大发生次数
    
    def check_conditions(self, game_state: Dict[str, Any]) -> bool:
        """检查是否满足触发条件"""
        current_turn = game_state.get("current_turn", 0)
        
        # 回合检查
        if current_turn < self.min_turn:
            return False
        if self.max_turn and current_turn > self.max_turn:
            return False
            
        # 恐惧值检查
        avg_fear = game_state.get("average_fear", 0)
        if avg_fear < self.min_fear_average:
            return False
        if self.max_fear_average and avg_fear > self.max_fear_average:
            return False
            
        # 存活NPC检查
        alive_npcs = game_state.get("alive_npcs", 0)
        if alive_npcs < self.required_npcs_alive:
            return False
            
        # 时间检查
        if self.time_of_day:
            current_time = game_state.get("time_of_day", "day")
            if current_time not in self.time_of_day:
                return False
                
        # 概率检查
        if random.random() > self.probability:
            return False
            
        return True


@dataclass
class EventEffect:
    """事件效果"""
    effect_type: str  # fear_change, sanity_change, spawn_item, etc.
    target: str = "random"  # all, random, specific_npc, location
    amount: int = 0
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class GameEvent:
    """游戏事件定义"""
    id: str
    name: str
    description: str
    event_type: EventType
    priority: EventPriority
    trigger: EventTriggerCondition
    effects: List[EventEffect]
    messages: List[str] = field(default_factory=list)  # 显示给玩家的消息
    sound_effects: List[str] = field(default_factory=list)
    visual_effects: List[str] = field(default_factory=list)
    
    # 运行时状态
    occurrences: int = 0
    last_triggered: Optional[int] = None
    
    def can_trigger(self, game_state: Dict[str, Any]) -> bool:
        """检查事件是否可以触发"""
        # 检查最大次数
        if self.trigger.max_occurrences and self.occurrences >= self.trigger.max_occurrences:
            return False
            
        # 检查冷却
        if self.last_triggered:
            current_turn = game_state.get("current_turn", 0)
            if current_turn - self.last_triggered < self.trigger.cooldown:
                return False
                
        # 检查触发条件
        return self.trigger.check_conditions(game_state)
    
    def trigger_event(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """触发事件"""
        self.occurrences += 1
        self.last_triggered = game_state.get("current_turn", 0)
        
        result = {
            "event_id": self.id,
            "event_name": self.name,
            "effects_applied": [],
            "messages": self.messages.copy(),
            "sounds": self.sound_effects.copy(),
            "visuals": self.visual_effects.copy()
        }
        
        # 应用效果
        for effect in self.effects:
            effect_result = self._apply_effect(effect, game_state)
            result["effects_applied"].append(effect_result)
            
        return result
    
    def _apply_effect(self, effect: EventEffect, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """应用单个效果"""
        result = {
            "type": effect.effect_type,
            "target": effect.target,
            "success": True
        }
        
        # 这里只是记录效果，实际应用由游戏系统处理
        if effect.effect_type == "fear_change":
            result["amount"] = effect.amount
            result["description"] = effect.description or f"恐惧值变化 {effect.amount}"
            
        elif effect.effect_type == "sanity_change":
            result["amount"] = effect.amount
            result["description"] = effect.description or f"理智值变化 {effect.amount}"
            
        elif effect.effect_type == "spawn_item":
            result["item"] = effect.params.get("item_id", "unknown")
            result["location"] = effect.params.get("location", "random")
            
        elif effect.effect_type == "environmental":
            result["change"] = effect.params.get("change", "unknown")
            
        return result


class EventSystem:
    """事件系统管理器"""
    
    def __init__(self):
        self.events: Dict[str, GameEvent] = {}
        self.event_queue: List[str] = []
        self.event_history: List[Dict[str, Any]] = []
        self._initialize_default_events()
        
    def _initialize_default_events(self):
        """初始化默认事件"""
        default_events = [
            # 环境事件
            GameEvent(
                id="power_outage",
                name="停电",
                description="整栋建筑突然陷入黑暗",
                event_type=EventType.ENVIRONMENTAL,
                priority=EventPriority.HIGH,
                trigger=EventTriggerCondition(
                    min_turn=5,
                    min_fear_average=40,
                    probability=0.3,
                    cooldown=10,
                    max_occurrences=2
                ),
                effects=[
                    EventEffect(
                        effect_type="environmental",
                        target="all_areas",
                        params={"change": "lights_off", "duration": 5}
                    ),
                    EventEffect(
                        effect_type="fear_change",
                        target="all",
                        amount=15,
                        description="黑暗带来的恐惧"
                    )
                ],
                messages=[
                    "突然，所有的灯都熄灭了...",
                    "黑暗如潮水般涌来，吞噬了一切光明。"
                ],
                sound_effects=["power_down", "darkness_ambient"]
            ),
            
            GameEvent(
                id="strange_noise",
                name="诡异声响",
                description="从某个方向传来不明的声音",
                event_type=EventType.ENVIRONMENTAL,
                priority=EventPriority.LOW,
                trigger=EventTriggerCondition(
                    min_turn=2,
                    probability=0.4,
                    cooldown=3
                ),
                effects=[
                    EventEffect(
                        effect_type="fear_change",
                        target="random",
                        amount=10,
                        description="听到诡异的声音"
                    )
                ],
                messages=[
                    "咯吱...咯吱...楼上传来奇怪的声音。",
                    "墙壁里似乎有什么东西在爬动...",
                    "远处传来若有若无的哭泣声。"
                ],
                sound_effects=["creaking", "scratching", "whisper"]
            ),
            
            GameEvent(
                id="temperature_drop",
                name="温度骤降",
                description="房间突然变得异常寒冷",
                event_type=EventType.ENVIRONMENTAL,
                priority=EventPriority.MEDIUM,
                trigger=EventTriggerCondition(
                    min_fear_average=30,
                    probability=0.35,
                    cooldown=5
                ),
                effects=[
                    EventEffect(
                        effect_type="environmental",
                        target="current_area",
                        params={"change": "cold", "duration": 3}
                    ),
                    EventEffect(
                        effect_type="fear_change",
                        target="area_npcs",
                        amount=5
                    )
                ],
                messages=[
                    "温度突然下降，每个人都能看到自己呼出的白雾。",
                    "一股刺骨的寒意从虚无中袭来。"
                ],
                visual_effects=["frost_breath", "ice_crystals"]
            ),
            
            # NPC事件
            GameEvent(
                id="nightmare",
                name="噩梦",
                description="NPC做了可怕的噩梦",
                event_type=EventType.NPC_EVENT,
                priority=EventPriority.LOW,
                trigger=EventTriggerCondition(
                    time_of_day=["night"],
                    probability=0.25,
                    cooldown=5
                ),
                effects=[
                    EventEffect(
                        effect_type="sanity_change",
                        target="random",
                        amount=-15,
                        description="噩梦的折磨"
                    ),
                    EventEffect(
                        effect_type="fear_change",
                        target="same",
                        amount=10
                    )
                ],
                messages=[
                    "{npc_name}从噩梦中惊醒，满头冷汗。",
                    "恐怖的梦境让{npc_name}无法安眠。"
                ]
            ),
            
            GameEvent(
                id="hallucination",
                name="幻觉",
                description="NPC看到了不存在的东西",
                event_type=EventType.NPC_EVENT,
                priority=EventPriority.MEDIUM,
                trigger=EventTriggerCondition(
                    min_fear_average=50,
                    probability=0.3,
                    cooldown=4
                ),
                effects=[
                    EventEffect(
                        effect_type="sanity_change",
                        target="random",
                        amount=-20,
                        description="幻觉的冲击"
                    )
                ],
                messages=[
                    "{npc_name}指着空无一物的角落尖叫起来。",
                    "'{npc_name}看到了什么？那里明明什么都没有...",
                    "{npc_name}喃喃自语着一些听不懂的话。"
                ]
            ),
            
            # 物品事件
            GameEvent(
                id="item_appears",
                name="神秘物品出现",
                description="一个奇怪的物品凭空出现",
                event_type=EventType.ITEM_EVENT,
                priority=EventPriority.MEDIUM,
                trigger=EventTriggerCondition(
                    min_turn=3,
                    probability=0.2,
                    cooldown=8,
                    max_occurrences=3
                ),
                effects=[
                    EventEffect(
                        effect_type="spawn_item",
                        target="random_area",
                        params={"item_id": "mysterious_key", "cursed": True}
                    )
                ],
                messages=[
                    "一把锈迹斑斑的钥匙出现在地板上。",
                    "没有人知道这个东西是从哪来的..."
                ]
            ),
            
            GameEvent(
                id="item_breaks",
                name="物品损坏",
                description="关键物品突然损坏",
                event_type=EventType.ITEM_EVENT,
                priority=EventPriority.MEDIUM,
                trigger=EventTriggerCondition(
                    min_fear_average=60,
                    probability=0.25,
                    cooldown=6
                ),
                effects=[
                    EventEffect(
                        effect_type="break_item",
                        target="random_npc",
                        params={"item_type": "flashlight"}
                    ),
                    EventEffect(
                        effect_type="fear_change",
                        target="item_owner",
                        amount=15
                    )
                ],
                messages=[
                    "咔嚓一声，{npc_name}的手电筒突然坏了。",
                    "在最需要的时候，装备却背叛了它的主人。"
                ]
            ),
            
            # 超自然事件
            GameEvent(
                id="ghost_sighting",
                name="灵体目击",
                description="有人看到了游魂",
                event_type=EventType.SUPERNATURAL,
                priority=EventPriority.HIGH,
                trigger=EventTriggerCondition(
                    min_turn=7,
                    min_fear_average=45,
                    probability=0.35,
                    cooldown=8
                ),
                effects=[
                    EventEffect(
                        effect_type="spawn_spirit",
                        target="random_area",
                        params={"spirit_type": "wandering_soul", "duration": 3}
                    ),
                    EventEffect(
                        effect_type="fear_change",
                        target="witnesses",
                        amount=25,
                        description="目击灵体的恐惧"
                    )
                ],
                messages=[
                    "一个半透明的身影在走廊尽头一闪而过。",
                    "那是...人吗？不，它没有脚...",
                    "空气中弥漫着腐朽的气味，伴随着低沉的呻吟声。"
                ],
                sound_effects=["ghost_moan", "chains_rattle"],
                visual_effects=["translucent_figure", "cold_breath"]
            ),
            
            GameEvent(
                id="possession_attempt",
                name="附身尝试",
                description="恶灵试图附身",
                event_type=EventType.SUPERNATURAL,
                priority=EventPriority.CRITICAL,
                trigger=EventTriggerCondition(
                    min_turn=10,
                    min_fear_average=70,
                    required_npcs_alive=2,
                    probability=0.2,
                    cooldown=15,
                    max_occurrences=1
                ),
                effects=[
                    EventEffect(
                        effect_type="possession",
                        target="lowest_sanity",
                        params={"resist_check": "sanity", "difficulty": 60}
                    ),
                    EventEffect(
                        effect_type="fear_change",
                        target="all",
                        amount=30,
                        description="目睹附身的恐怖"
                    )
                ],
                messages=[
                    "{npc_name}的眼睛突然翻白，身体开始剧烈抽搐。",
                    "一个看不见的存在正试图夺取{npc_name}的身体！",
                    "房间里充满了硫磺的味道..."
                ],
                sound_effects=["demonic_whisper", "possession_scream"]
            )
        ]
        
        # 添加到事件字典
        for event in default_events:
            self.add_event(event)
    
    def add_event(self, event: GameEvent):
        """添加事件"""
        self.events[event.id] = event
        logger.info(f"Added event: {event.name} ({event.id})")
    
    def remove_event(self, event_id: str):
        """移除事件"""
        if event_id in self.events:
            del self.events[event_id]
            logger.info(f"Removed event: {event_id}")
    
    def check_and_trigger_events(self, game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查并触发事件"""
        triggered_events = []
        
        # 按优先级排序事件
        sorted_events = sorted(
            self.events.values(),
            key=lambda e: ["low", "medium", "high", "critical"].index(e.priority.value),
            reverse=True
        )
        
        for event in sorted_events:
            if event.can_trigger(game_state):
                result = event.trigger_event(game_state)
                triggered_events.append(result)
                
                # 记录历史
                self.event_history.append({
                    "event_id": event.id,
                    "turn": game_state.get("current_turn", 0),
                    "timestamp": datetime.now(),
                    "result": result
                })
                
                logger.info(f"Triggered event: {event.name}")
                
                # 高优先级事件可能阻止其他事件
                if event.priority == EventPriority.CRITICAL:
                    break
        
        return triggered_events
    
    def get_event_by_id(self, event_id: str) -> Optional[GameEvent]:
        """根据ID获取事件"""
        return self.events.get(event_id)
    
    def get_events_by_type(self, event_type: EventType) -> List[GameEvent]:
        """根据类型获取事件"""
        return [e for e in self.events.values() if e.event_type == event_type]
    
    def get_event_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取事件历史"""
        return self.event_history[-limit:] if self.event_history else []
    
    def load_events_from_json(self, file_path: str):
        """从JSON文件加载事件"""
        import json
        from pathlib import Path
        
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Event file not found: {file_path}")
            return
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for event_data in data.get('events', []):
                # 构建触发条件
                trigger_data = event_data.get('trigger', {})
                trigger = EventTriggerCondition(**trigger_data)
                
                # 构建效果列表
                effects = []
                for effect_data in event_data.get('effects', []):
                    effects.append(EventEffect(**effect_data))
                
                # 创建事件
                event = GameEvent(
                    id=event_data['id'],
                    name=event_data['name'],
                    description=event_data.get('description', ''),
                    event_type=EventType(event_data.get('event_type', 'environmental')),
                    priority=EventPriority(event_data.get('priority', 'medium')),
                    trigger=trigger,
                    effects=effects,
                    messages=event_data.get('messages', []),
                    sound_effects=event_data.get('sound_effects', []),
                    visual_effects=event_data.get('visual_effects', [])
                )
                
                self.add_event(event)
                
            logger.info(f"Loaded {len(data.get('events', []))} events from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load events from {file_path}: {e}")


# 测试代码
if __name__ == "__main__":
    # 创建事件系统
    event_system = EventSystem()
    
    print("=== 事件系统测试 ===\n")
    
    # 显示所有事件
    print("已注册事件:")
    for event_id, event in event_system.events.items():
        print(f"- {event.name} ({event.id})")
        print(f"  类型: {event.event_type.value}")
        print(f"  优先级: {event.priority.value}")
        print(f"  触发概率: {event.trigger.probability}")
        print()
    
    # 模拟游戏状态
    game_state = {
        "current_turn": 8,
        "average_fear": 55,
        "alive_npcs": 4,
        "time_of_day": "night"
    }
    
    print("\n模拟事件触发:")
    print(f"游戏状态: 回合{game_state['current_turn']}, 平均恐惧{game_state['average_fear']}")
    
    # 检查并触发事件
    triggered = event_system.check_and_trigger_events(game_state)
    
    if triggered:
        print(f"\n触发了 {len(triggered)} 个事件:")
        for result in triggered:
            print(f"\n事件: {result['event_name']}")
            if result['messages']:
                print(f"消息: {result['messages'][0]}")
            print(f"效果: {len(result['effects_applied'])} 个")
            for effect in result['effects_applied']:
                print(f"  - {effect.get('description', effect['type'])}")
    else:
        print("\n没有事件被触发")
    
    # 显示事件历史
    print("\n事件历史:")
    history = event_system.get_event_history()
    for record in history:
        print(f"- 回合{record['turn']}: {record['event_id']}")
