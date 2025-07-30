"""
事件系统兼容层 (Compatibility Shim)
为了保持向后兼容，提供旧测试期望的接口
TODO: 在完全迁移到 src/models/event.py 后删除此文件
"""
from typing import Any, Dict

try:
    # 尝试从新位置导入已迁移的定义
    from src.models.event import Event as GameEvent, EventType
except ImportError:
    # 极端 fallback：定义极简版本保证 import，不破坏主流程
    from enum import Enum
    from dataclasses import dataclass
    
    class EventType(str, Enum):
        """事件类型枚举（兼容版本）"""
        GENERIC = "generic"
        NPC_ACTION = "npc_action"
        NPC_DIALOGUE = "npc_dialogue"
        RULE_TRIGGERED = "rule_triggered"
        RULE_CREATED = "rule_created"
        NPC_DEATH = "npc_death"
        FEAR_GAINED = "fear_gained"
        GAME_START = "game_start"
        GAME_OVER = "game_over"
        PHASE_CHANGE = "phase_change"
        NARRATIVE = "narrative"
    
    @dataclass
    class GameEvent:
        """游戏事件（兼容版本）"""
        type: EventType = EventType.GENERIC
        description: str = ""
        turn: int = 0
        metadata: Dict[str, Any] = None
        
        def __post_init__(self):
            if self.metadata is None:
                self.metadata = {}
        
        def to_dict(self) -> Dict[str, Any]:
            """转换为字典"""
            return {
                "type": self.type.value if hasattr(self.type, 'value') else str(self.type),
                "description": self.description,
                "turn": self.turn,
                "metadata": self.metadata
            }


# 为了兼容性，也导出 Event 作为 GameEvent 的别名
Event = GameEvent

class EventSystem:
    """Simple event system used for integration tests."""

    def __init__(self) -> None:
        self.events: list[GameEvent] = []

    def record_event(self, event: GameEvent) -> None:
        """Record an event for later retrieval."""
        self.events.append(event)

    def check_and_trigger_events(self, game_state: Dict[str, Any]) -> list[Dict[str, Any]]:
        """Dummy implementation returning previously recorded events.

        Parameters
        ----------
        game_state: Dict[str, Any]
            Current game state; ignored in this simple implementation.

        Returns
        -------
        List of event dictionaries for compatibility with tests.
        """
        results = []
        for evt in self.events:
            results.append({
                "event_name": getattr(evt, "description", "event"),
                "messages": [evt.description] if getattr(evt, "description", "") else [],
                "effects_applied": evt.metadata.get("effects", []) if evt.metadata else []
            })
        return results


__all__ = ['GameEvent', 'Event', 'EventType', 'EventSystem']
