"""
对话系统
生成NPC之间的对话
"""
import logging
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from src.api.deepseek_client import APIConfig, DeepSeekClient

logger = logging.getLogger(__name__)


class DialogueType(Enum):
    """对话类型枚举"""

    MORNING = "morning"
    DISCOVERY = "discovery"
    FEAR = "fear"
    INVESTIGATION = "investigation"
    COMFORT = "comfort"
    PANIC = "panic"


@dataclass
class DialogueContext:
    """对话上下文"""

    location: str
    time: str
    participants: List[str]
    recent_events: Optional[List[str]] = None
    mood: str = "normal"
    discovered_clues: Optional[List[str]] = None

    def __post_init__(self):
        if self.recent_events is None:
            self.recent_events = []
        if self.discovered_clues is None:
            self.discovered_clues = []


class DialogueEntry:
    """对话条目"""

    def __init__(self, turn: int, dialogue_type: DialogueType):
        self.turn = turn
        self.dialogue_type = dialogue_type
        self.dialogues: List[dict[str, str]] = []


class DialogueSystem:
    """对话系统"""

    def __init__(self, deepseek_client=None):
        """Initialize dialogue system with an optional DeepSeek client."""
        self.deepseek_client = deepseek_client or DeepSeekClient(
            APIConfig(mock_mode=True), http_client=None
        )
        self.api_client = self.deepseek_client  # backward compatibility
        self.dialogue_templates = {
            "fear": [
                "{npc1}: 你有没有感觉到...这里不太对劲？",
                "{npc2}: 我们必须离开这里，马上！",
                "{npc1}: 那个声音...你听到了吗？",
                "{npc2}: 别说了，我不想知道那是什么。",
            ],
            "investigation": [
                "{npc1}: 这里一定有什么秘密。",
                "{npc2}: 也许我们不该深究下去。",
                "{npc1}: 看这些痕迹，像是有人故意留下的。",
                "{npc2}: 或者...不是人留下的。",
            ],
            "comfort": [
                "{npc1}: 冷静点，我们会没事的。",
                "{npc2}: 你真的这么认为吗？",
                "{npc1}: 只要我们遵守规则，就能活下去。",
                "{npc2}: 但是谁知道还有多少规则？",
            ],
            "panic": [
                "{npc1}: 不！这不可能！",
                "{npc2}: 冷静！现在慌张只会害死我们！",
                "{npc1}: 它就在那里！就在那里！",
                "{npc2}: 闭嘴！你会把它引过来的！",
            ],
        }

    async def generate_dialogue(
        self, npcs: List[Any], context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """生成NPC对话"""
        if len(npcs) < 2:
            return []

        if self.deepseek_client:
            # 使用AI生成对话
            try:
                # 准备NPC状态
                npc_states = []
                for npc in npcs[:2]:  # 只取前两个NPC
                    npc_states.append(
                        {
                            "name": npc.name,
                            "fear": getattr(npc, "fear", 50),
                            "sanity": getattr(npc, "sanity", 80),
                            "traits": getattr(npc, "traits", []),
                            "status": getattr(npc, "status", "normal"),
                        }
                    )

                # 调用AI生成对话
                dialogue = await self.deepseek_client.generate_dialogue(
                    npc_states=npc_states,
                    scene_context={
                        "time": context.get("time", "night"),
                        "recent_events": context.get("recent_events", []),
                    },
                )

                # 格式化返回
                result = []
                for turn in dialogue:
                    result.append({"speaker": turn.speaker, "text": turn.text})
                return result
            except Exception:
                logger.exception("Failed to generate dialogue via AI, falling back to templates")

        # 使用模板生成对话
        npc1, npc2 = npcs[0], npcs[1]

        # 根据NPC状态选择对话类型
        avg_fear = (getattr(npc1, "fear", 50) + getattr(npc2, "fear", 50)) / 2
        avg_sanity = (getattr(npc1, "sanity", 80) + getattr(npc2, "sanity", 80)) / 2

        if avg_fear > 70 or avg_sanity < 30:
            dialogue_type = "panic"
        elif avg_fear > 50:
            dialogue_type = "fear"
        elif "好奇" in getattr(npc1, "traits", []) or "好奇" in getattr(npc2, "traits", []):
            dialogue_type = "investigation"
        else:
            dialogue_type = "comfort"

        # 选择对话模板
        templates = self.dialogue_templates[dialogue_type]
        selected_templates = random.sample(templates, min(2, len(templates)))

        # 生成对话
        dialogue = []
        for i, template in enumerate(selected_templates):
            # 随机分配说话者
            if i % 2 == 0:
                text = template.format(npc1=npc1.name, npc2=npc2.name)
                # 提取实际说话者
                if npc1.name in text:
                    speaker = npc1.name
                else:
                    speaker = npc2.name
            else:
                text = template.format(npc1=npc2.name, npc2=npc1.name)
                if npc2.name in text:
                    speaker = npc2.name
                else:
                    speaker = npc1.name

            # 清理文本（移除说话者前缀）
            text = text.split(": ", 1)[-1] if ": " in text else text

            dialogue.append({"speaker": speaker, "text": text})

        return dialogue

    async def generate_dialogue_round(
        self,
        npcs: List[Any],
        context: DialogueContext,
        dialogue_type: DialogueType,
        turn: int,
    ) -> DialogueEntry:
        """生成一轮对话"""
        # 创建对话条目
        entry = DialogueEntry(turn=turn, dialogue_type=dialogue_type)

        # 根据类型选择模板
        template_key = "fear"  # 默认
        if dialogue_type == DialogueType.FEAR:
            template_key = "fear"
        elif dialogue_type == DialogueType.INVESTIGATION:
            template_key = "investigation"
        elif dialogue_type == DialogueType.COMFORT:
            template_key = "comfort"
        elif dialogue_type == DialogueType.PANIC:
            template_key = "panic"
        elif dialogue_type == DialogueType.DISCOVERY:
            template_key = "investigation"  # 发现类对话使用调查模板
        elif dialogue_type == DialogueType.MORNING:
            template_key = "comfort"  # 早间对话使用安慰模板

        # 生成对话
        templates = self.dialogue_templates.get(template_key, [])
        if templates and len(npcs) >= 2:
            # 选择模板
            selected_templates = random.sample(templates, min(2, len(templates)))
            npc1, npc2 = random.sample(npcs, 2)

            for template in selected_templates:
                # 替换模板中的NPC名字
                dialogue_text = template.replace(
                    "{npc1}", npc1.name if hasattr(npc1, "name") else str(npc1)
                )
                dialogue_text = dialogue_text.replace(
                    "{npc2}", npc2.name if hasattr(npc2, "name") else str(npc2)
                )

                # 解析对话
                if ":" in dialogue_text:
                    speaker, text = dialogue_text.split(":", 1)
                    entry.dialogues.append(
                        {"speaker": speaker.strip(), "text": text.strip()}
                    )

        return entry
