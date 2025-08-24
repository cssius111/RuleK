"""GameStateManager NPC serialization tests"""

import os
import sys
from dataclasses import dataclass


sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from src.core.game_state import GameStateManager  # noqa: E402


@dataclass
class Weapon:
    """Simple weapon dataclass for testing"""

    name: str
    damage: int


@dataclass
class Character:
    """Nested dataclass for NPC"""

    name: str
    weapon: Weapon


def test_serialize_dataclass_npc() -> None:
    """Dataclasses should be serialized recursively"""

    manager = GameStateManager()
    npc = Character(name="Hero", weapon=Weapon(name="Sword", damage=10))
    serialized = manager._serialize_npc(npc)

    assert serialized == {"name": "Hero", "weapon": {"name": "Sword", "damage": 10}}


def test_serialize_dataclass_in_dict() -> None:
    """Dataclasses nested inside dictionaries should be handled"""

    manager = GameStateManager()
    npc = {"character": Character(name="Hero", weapon=Weapon(name="Sword", damage=10))}
    serialized = manager._serialize_npc(npc)

    assert serialized == {
        "character": {"name": "Hero", "weapon": {"name": "Sword", "damage": 10}}
    }

