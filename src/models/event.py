"""
事件模型（供 AI 管线、CLI 等统一使用）
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any, Dict, Optional
import uuid
from datetime import datetime, UTC


class EventType(str, Enum):
    """游戏内支持的事件类型"""

    NPC_DIALOGUE = "npc_dialogue"          # NPC 说话
    NPC_ACTION   = "npc_action"            # NPC 行动
    RULE_TRIGGER = "rule_triggered"        # 规则触发
    FEAR_GAIN    = "fear_gained"           # 恐惧积分变化
    NPC_DEATH    = "npc_death"             # NPC 死亡
    SYSTEM       = "system"                # 系统提示、存档等
    NARRATION    = "narration"             # AI 生成叙事
    NARRATIVE    = "narrative"             # AI 生成叙事（别名）


@dataclass
class Event:
    """
    通用事件结构
      • `id` : 事件唯一标识
      • `type` : 事件类型
      • `description` : 文本描述（用于日志 / UI）
      • `turn` : 回合号
      • `game_time` : 游戏内时间片（morning / night…）
      • `meta` : 任意附加字段，便于规则或 AI 使用
    """

    # 必需字段（无默认值）
    type: EventType
    description: str
    turn: int
    
    # 可选字段（有默认值）
    id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    game_time: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # ---- 序列化辅助 --------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """转为可 JSON 序列化字典（枚举 → str）"""
        d = asdict(self)
        d["type"] = self.type.value
        d["created_at"] = self.created_at.isoformat()
        return d
