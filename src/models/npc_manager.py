from __future__ import annotations

from typing import Dict, Optional

from .npc import NPC, NPCPersonality


class NPCManager:
    """Minimal manager for handling NPC objects."""

    def __init__(self) -> None:
        self.npcs: Dict[str, NPC] = {}

    def create_npc(
        self,
        name: str,
        rationality: int = 5,
        courage: int = 5,
        curiosity: int = 5,
        sociability: int = 5,
        paranoia: int = 3,
        **kwargs,
    ) -> NPC:
        """Create an NPC with a custom personality and store it."""
        personality = NPCPersonality(
            rationality=rationality,
            courage=courage,
            curiosity=curiosity,
            sociability=sociability,
            paranoia=paranoia,
        )
        npc = NPC(name=name, personality=personality, **kwargs)
        self.npcs[npc.id] = npc
        return npc

    def add_npc(self, npc: NPC) -> None:
        """Add an existing NPC to the manager."""
        self.npcs[npc.id] = npc

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Retrieve an NPC by ID."""
        return self.npcs.get(npc_id)

    def remove_npc(self, npc_id: str) -> None:
        """Remove an NPC from the manager."""
        self.npcs.pop(npc_id, None)

    def all_npcs(self) -> Dict[str, NPC]:
        """Return all managed NPCs."""
        return self.npcs
