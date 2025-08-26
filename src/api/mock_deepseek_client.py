from __future__ import annotations

from typing import Any, Dict, List, Optional

from .llm_client import LLMClient
from .schemas import DialogueTurn, TurnPlan, RuleEvalResult, RuleTrigger, RuleEffect


class MockDeepSeekClient(LLMClient):
    """Mock implementation of :class:`LLMClient` for testing."""

    async def generate_turn_plan(
        self,
        npc_states: List[Dict[str, Any]],
        scene_context: Dict[str, Any],
        available_places: List[str],
        time_of_day: str,
        min_dialogue: int = 1,
    ) -> TurnPlan:
        dialogue = [
            DialogueTurn(speaker=npc_states[0]["name"], text="这是一个测试响应"),
        ]
        return TurnPlan(dialogue=dialogue, actions=[], atmosphere="calm")

    async def generate_narrative_text(
        self,
        events: List[Dict[str, Any]],
        time_of_day: str,
        survivor_count: int,
        ambient_fear: int = 50,
        location: str | None = None,
        npc_states: Optional[List[Dict[str, Any]]] = None,
        min_len: int = 200,
    ) -> str:
        return "在测试环境中，恐怖只是模拟。"

    async def evaluate_rule_nl(
        self, rule_nl: str, world_ctx: Dict[str, Any]
    ) -> RuleEvalResult:
        return RuleEvalResult(
            name="测试规则",
            trigger=RuleTrigger(type="event", conditions=[]),
            effect=RuleEffect(type="custom", params={}),
            cost=1,
            difficulty=1,
            loopholes=[],
            suggestion="保持谨慎",
        )

    async def generate_dialogue(
        self,
        npc_states: List[Dict[str, Any]],
        scene_context: Dict[str, Any],
        dialogue_type: str = "normal",
    ) -> List[Dict[str, str]]:
        return [{"speaker": npc_states[0]["name"], "text": "测试对话"}]

    async def close(self) -> None:
        return None
