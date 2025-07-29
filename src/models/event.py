"""事件模型，用于记录游戏中的各类事件"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ConfigDict


class EventType(str, Enum):
    """事件类型枚举"""

    NPC_DIALOGUE = "npc_dialogue"
    NPC_ACTION = "npc_action"
    ITEM_FOUND = "item_found"
    CLUE_FOUND = "clue_found"
    NARRATIVE = "narrative"
    SYSTEM = "system"
    NPC_DEATH = "npc_death"
    RULE_TRIGGERED = "rule_triggered"
    RULE_CREATED = "rule_created"
    RANDOM_EVENT = "random_event"


class Event(BaseModel):
    """通用事件数据模型"""

    type: EventType = Field(description="事件类型")
    description: str = Field(description="事件描述")
    turn: int = Field(0, description="发生的回合数")
    game_time: Optional[str] = Field(default=None, description="游戏内时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加数据")

    model_config = ConfigDict(use_enum_values=True, extra="allow")

    def to_dict(self) -> Dict[str, Any]:
        """返回可序列化的字典数据"""
        return self.model_dump()
