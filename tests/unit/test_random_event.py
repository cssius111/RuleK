import sys
from pathlib import Path

import pytest

# ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from web.backend.services import game_service as gs_module
from web.backend.services.game_service import GameService


@pytest.mark.asyncio
async def test_random_event_generation(monkeypatch):
    """随机事件应记录在 events 列表和 game_log 中"""
    monkeypatch.setattr(gs_module.random, "random", lambda: 0.1)
    monkeypatch.setattr(gs_module.random, "choice", lambda seq: "窗外传来诡异声响")

    service = GameService()
    await service.initialize()

    service.npc_behavior.decide_action = lambda *args, **kwargs: None
    service.rule_executor.execute = lambda *args, **kwargs: None

    async def fake_dialogue(self):
        return []

    async def fake_broadcast(self, update):
        return None

    async def fake_narrative(*args, **kwargs):
        return None

    service.narrator.generate_narrative = fake_narrative
    monkeypatch.setattr(GameService, "_run_dialogue_phase", fake_dialogue)
    monkeypatch.setattr(GameService, "broadcast_update", fake_broadcast)

    result = await service.advance_turn()

    assert any(e["type"] == "ambient" for e in result.events)
    assert any("窗外传来诡异声响" in log for log in service.game_state_manager.game_log)

