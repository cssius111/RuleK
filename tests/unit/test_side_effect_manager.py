import logging
from src.core.side_effects import SideEffectManager


def test_update_active_effects_expiration(caplog):
    """Ensure expired side effects are removed based on duration."""
    manager = SideEffectManager()
    manager.active_effects = [
        {"effect_name": "e1", "turn_applied": 0, "context": {"duration": 2}},
        {"effect_name": "e2", "turn_applied": 3, "context": {"duration": 5}},
        {"effect_name": "e3", "turn_applied": 3, "context": {}},
    ]

    with caplog.at_level(logging.INFO):
        manager.update_active_effects(current_turn=4)

    assert len(manager.active_effects) == 1
    assert manager.active_effects[0]["effect_name"] == "e2"
    assert "副作用 e1 已过期" in caplog.text
    assert "副作用 e3 已过期" in caplog.text

