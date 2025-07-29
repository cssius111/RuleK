"""
事件模型（供 AI 管线、CLI 等统一使用）
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime


class EventType(str, Enum):
    """游戏内支持的事件类型"""

    NPC_DIALOGUE = "npc_dialogue"          # NPC 说话
    NPC_ACTION   = "npc_action"            # NPC 行动
    RULE_TRIGGER = "rule_triggered"        # 规则触发
    FEAR_GAIN    = "fear_gained"           # 恐惧积分变化
    NPC_DEATH    = "npc_death"             # NPC 死亡
    SYSTEM       = "system"                # 系统提示、存档等
    NARRATION    = "narration"             # AI 生成叙事


@dataclass
class Event:
    """
    通用事件结构  
      • `type` : 事件类型  
      • `description` : 文本描述（⽤于日志 / UI）  
      • `turn` : 回合号  
      • `game_time` : 游戏内时间片（morning / night…）  
      • `data` : 任意附加字段，便于规则或 AI 使用
    """

    type: EventType
    description: str
    turn: int
    game_time: str = ""
    data: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.utcnow()

    # ---- 序列化辅助 --------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """转为可 JSON 序列化字典（枚举 → str）"""
        d = asdict(self)
        d["type"] = self.type.value
        d["created_at"] = self.created_at.isoformat()
        return d
