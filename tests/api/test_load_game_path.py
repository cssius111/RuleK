"""Tests for the /api/games/load endpoint path validation."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from web.backend import app as app_module


class DummyService:
    def get_state_response(self) -> dict:
        return {"status": "ok"}


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_load_game_endpoint_valid(monkeypatch, tmp_path, client):
    monkeypatch.setattr(app_module, "SAVE_DIR", tmp_path)

    async def fake_load_game(filename: str):
        assert filename == "valid.rulek"
        return DummyService()

    monkeypatch.setattr(app_module.session_manager, "load_game", fake_load_game)

    response = client.post("/api/games/load", params={"filename": "valid.rulek"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_load_game_endpoint_invalid(client):
    response = client.post("/api/games/load", params={"filename": "../bad.rulek"})
    assert response.status_code == 400

