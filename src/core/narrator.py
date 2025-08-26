"""
叙事生成器
生成恐怖氛围的游戏叙事
"""
import logging
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

from src.api.deepseek_client import DeepSeekClient
from src.api.deepseek_http_client import APIConfig
from src.api.llm_client import LLMClient

logger = logging.getLogger(__name__)


class EventSeverity(str, Enum):
    """Severity levels for narrative events."""

    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class NarrativeStyle(str, Enum):
    """Narrative tone presets."""

    DEFAULT = "default"
    HORROR = "horror"
    COMEDY = "comedy"


@dataclass
class GameEvent:
    """Simple structure describing a narrative event."""

    event_type: str
    severity: EventSeverity
    actors: List[str]
    location: str
    details: Dict[str, Any]


class Narrator:
    """叙事生成器"""

    def __init__(self, deepseek_client: LLMClient | None = None):
        """Initialize the narrator with an optional DeepSeek client."""
        self.deepseek_client = deepseek_client or DeepSeekClient(APIConfig(mock_mode=True))
        self.api_client = self.deepseek_client
        self.style: NarrativeStyle = NarrativeStyle.DEFAULT
        self.narrative_templates = {
            "npc_action": [
                "{npc}小心翼翼地{action}，空气中弥漫着不祥的气息。",
                "在昏暗的{location}中，{npc}{action}，似乎有什么在暗中窥视。",
                "{npc}的身影在{location}中{action}，留下了一串不安的回响。",
            ],
            "rule_triggered": [
                "规则的力量开始显现，{rule}被触发了，恐怖笼罩着整个空间。",
                "违背了禁忌，{rule}的诅咒降临，无人能够逃脱。",
                "古老的规则被打破，{rule}带来了不可名状的恐惧。",
            ],
            "dialogue": [
                "在压抑的氛围中，{participants}交换着不安的眼神。",
                "{participants}的对话在空荡的房间里回响，每个字都充满了恐惧。",
                "颤抖的声音中，{participants}试图寻找一丝希望。",
            ],
            "time_change": {
                "morning": "晨光透过破碎的窗户，却无法驱散笼罩的阴霾。",
                "afternoon": "午后的阳光显得格外苍白，仿佛被什么吸走了生机。",
                "evening": "夜幕降临，黑暗中潜伏着未知的恐怖。",
                "night": "深夜的寂静被诡异的声响打破，恐惧在每个角落蔓延。",
            },
        }

    def set_style(self, style: NarrativeStyle) -> None:
        """Set narrative style (currently unused)."""
        self.style = style

    async def generate_narrative(
        self, events: List[Dict[str, Any]], game_state: Any
    ) -> str:
        """生成叙事文本"""
        if self.deepseek_client:
            # 使用AI生成叙事
            try:
                # 准备事件描述
                event_descriptions = []
                for event in events:
                    event_type = event.get("type", "unknown")
                    if event_type == "npc_action":
                        desc = f"{event.get('npc', '某人')}在{event.get('location', '某处')}{event.get('action', '做了什么')}"
                    elif event_type == "rule_triggered":
                        desc = f"规则'{event.get('rule', '未知规则')}'被触发，{event.get('result', {}).get('description', '产生了恐怖的后果')}"
                    elif event_type == "dialogue":
                        participants = event.get("participants", [])
                        desc = f"{' 和 '.join(participants)}进行了一段对话"
                    else:
                        desc = event.get("description", "发生了一些事情")
                    event_descriptions.append(desc)

                # 调用AI生成叙事
                time_of_day = (
                    game_state.get("time_of_day")
                    if isinstance(game_state, dict)
                    else getattr(game_state, "time_of_day", None)
                )
                narrative = await self.deepseek_client.generate_narrative_text(
                    events=event_descriptions,
                    time_of_day=time_of_day,
                    min_len=200,
                )
                return narrative
            except Exception:
                logger.exception("Failed to generate narrative via AI, falling back to templates")

        # 使用模板生成叙事
        narrative_parts = []

        # 添加时间描述
        time_of_day = (
            game_state.get("time_of_day")
            if isinstance(game_state, dict)
            else getattr(game_state, "time_of_day", None)
        )
        time_desc = self.narrative_templates["time_change"].get(
            time_of_day, "时间在恐惧中流逝。"
        )
        narrative_parts.append(time_desc)

        # 处理每个事件
        for event in events[-3:]:  # 只处理最近3个事件
            event_type = event.get("type", "unknown")

            if event_type == "npc_action":
                template = random.choice(self.narrative_templates["npc_action"])
                text = template.format(
                    npc=event.get("npc", "某人"),
                    action=event.get("action", "移动"),
                    location=event.get("location", "未知地点"),
                )
                narrative_parts.append(text)

            elif event_type == "rule_triggered":
                template = random.choice(self.narrative_templates["rule_triggered"])
                text = template.format(rule=event.get("rule", "未知规则"))
                narrative_parts.append(text)

            elif event_type == "dialogue":
                template = random.choice(self.narrative_templates["dialogue"])
                participants = event.get("participants", ["某些人"])
                text = template.format(participants="和".join(participants))
                narrative_parts.append(text)

        # 组合叙事
        narrative = " ".join(narrative_parts)

        # 添加氛围描述
        if (
            game_state.get("fear_points", 0)
            if isinstance(game_state, dict)
            else getattr(game_state, "fear_points", 0)
        ) > 500:
            narrative += " 恐惧已经达到了临界点，整个空间都在颤抖。"

        return narrative

    async def narrate_turn(self, events: List[GameEvent], game_state: Dict[str, Any]):
        """Generate a simple chapter object for a turn."""
        text = await self.generate_narrative([e.__dict__ for e in events], game_state)
        current_turn = (
            game_state.get("current_turn", 0)
            if isinstance(game_state, dict)
            else getattr(game_state, "current_turn", 0)
        )
        title = f"Turn {current_turn}" if game_state else "Narrative"
        return type("Chapter", (), {"title": title, "content": text})()
