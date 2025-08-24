"""SessionManager.load_game path validation tests."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from web.backend.services import session_manager as sm_module


class DummyState:
    game_id = "dummy"


class DummyGameService:
    game_state = DummyState()

    async def initialize(self) -> None:
        return None


@pytest.mark.asyncio
async def test_load_game_valid_path(monkeypatch, tmp_path):
    monkeypatch.setattr(sm_module, "SAVE_DIR", tmp_path)

    def fake_load_from_file(cls, filename):
        assert filename == "valid.rulek"
        return DummyGameService()

    monkeypatch.setattr(sm_module.GameService, "load_from_file", classmethod(fake_load_from_file))

    manager = sm_module.SessionManager()
    game = await manager.load_game("valid.rulek")

    assert game.game_state.game_id == "dummy"


@pytest.mark.asyncio
async def test_load_game_invalid_path(monkeypatch, tmp_path):
    monkeypatch.setattr(sm_module, "SAVE_DIR", tmp_path)

    manager = sm_module.SessionManager()
    with pytest.raises(ValueError):
        await manager.load_game("../evil.rulek")

