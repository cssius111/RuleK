"""Tests for configuration parsing and NPC serialization."""

from dataclasses import dataclass

from pydantic import BaseModel

from src.core.game_state import GameStateManager
from src.utils.config import _parse_cors_origins


# ---------------------------------------------------------------------------
# _parse_cors_origins
# ---------------------------------------------------------------------------

def test_parse_cors_origins_json() -> None:
    """JSON string input should return a list of origins."""

    origins = _parse_cors_origins('["http://a.com", "http://b.com"]')

    assert origins == ["http://a.com", "http://b.com"]
    assert isinstance(origins, list)


def test_parse_cors_origins_python_list() -> None:
    """Python list string should return a list of origins."""

    origins = _parse_cors_origins("['http://a.com', 'http://b.com']")

    assert origins == ["http://a.com", "http://b.com"]
    assert isinstance(origins, list)


def test_parse_cors_origins_comma_separated() -> None:
    """Comma separated string should return a list of origins."""

    origins = _parse_cors_origins('http://a.com, http://b.com')

    assert origins == ["http://a.com", "http://b.com"]
    assert isinstance(origins, list)


# ---------------------------------------------------------------------------
# _serialize_npc
# ---------------------------------------------------------------------------


def test_serialize_dict_npc() -> None:
    """Dictionaries should be returned unchanged."""

    manager = GameStateManager()
    npc = {"name": "Hero", "hp": 10}
    serialized = manager._serialize_npc(npc)

    assert serialized == {"name": "Hero", "hp": 10}
    assert isinstance(serialized, (dict, list))


class NPCModel(BaseModel):
    """Simple Pydantic model for testing."""

    name: str
    hp: int


def test_serialize_pydantic_model() -> None:
    """Pydantic models should be converted to dictionaries."""

    manager = GameStateManager()
    npc = NPCModel(name="Hero", hp=10)
    serialized = manager._serialize_npc(npc)

    assert serialized == {"name": "Hero", "hp": 10}
    assert isinstance(serialized, (dict, list))


@dataclass
class NPCDataclass:
    """Simple dataclass for testing."""

    name: str
    hp: int


def test_serialize_dataclass() -> None:
    """Dataclasses should be serialized to dictionaries."""

    manager = GameStateManager()
    npc = NPCDataclass(name="Hero", hp=10)
    serialized = manager._serialize_npc(npc)

    assert serialized == {"name": "Hero", "hp": 10}
    assert isinstance(serialized, (dict, list))


class SimpleNPC:
    """Plain object for serialization testing."""

    def __init__(self, name: str, hp: int) -> None:
        self.name = name
        self.hp = hp


def test_serialize_plain_object() -> None:
    """Plain objects should be converted to dictionaries."""

    manager = GameStateManager()
    npc = SimpleNPC(name="Hero", hp=10)
    serialized = manager._serialize_npc(npc)

    assert serialized == {"name": "Hero", "hp": 10}
    assert isinstance(serialized, (dict, list))

