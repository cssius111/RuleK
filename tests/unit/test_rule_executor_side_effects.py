import pytest
from src.core.game_state import GameStateManager
from src.core.rule_executor import RuleExecutor, RuleContext


def test_side_effect_fear_bonus_increases_fear_points():
    gm = GameStateManager()
    gm.new_game("side_effect_fear")
    executor = RuleExecutor(gm)

    # 取任意NPC作为触发者
    npc = list(gm.state.npcs.values())[0]

    context = RuleContext(actor=npc, action="test", game_state=gm.state.to_dict())
    initial_fear = gm.state.fear_points

    executor._apply_side_effect("blood_message", context)

    assert gm.state.fear_points > initial_fear
