from __future__ import annotations

from typing import Protocol, Any, Dict, List, Optional


class LLMClient(Protocol):
    """Large language model client interface."""

    async def generate_turn_plan(
        self,
        npc_states: List[Dict[str, Any]],
        scene_context: Dict[str, Any],
        available_places: List[str],
        time_of_day: str,
        min_dialogue: int = 1,
    ) -> Any:
        """Generate a turn plan based on NPC states and scene context."""

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
        """Generate narrative text describing recent events."""

    async def evaluate_rule_nl(
        self, rule_nl: str, world_ctx: Dict[str, Any]
    ) -> Any:
        """Evaluate a natural language rule within the given world context."""

    async def generate_dialogue(
        self,
        npc_states: List[Dict[str, Any]],
        scene_context: Dict[str, Any],
        dialogue_type: str = "normal",
    ) -> List[Dict[str, str]]:
        """Generate dialogue for NPCs."""

    async def close(self) -> None:
        """Release any held resources."""
