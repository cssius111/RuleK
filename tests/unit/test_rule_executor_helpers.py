import pytest
from src.core.game_state import GameStateManager
from src.core.rule_executor import RuleExecutor

@pytest.mark.unit
def test_rule_executor_helpers_return():
    gm = GameStateManager()
    gm.new_game("helper_test")
    executor = RuleExecutor(gm)

    assert executor._add_scene_effect("bathroom", "blood") is True
    assert executor._change_room_temp("kitchen", -5) is True
    assert executor._trigger_light_event("hall") is True
