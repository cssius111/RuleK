import pytest
from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType


@pytest.mark.unit
def test_time_range_normal_interval():
    rule = Rule(
        id="r1",
        name="normal",
        trigger=TriggerCondition(action="act", time_range={"from": "08:00", "to": "12:00"}),
        effect=RuleEffect(type=EffectType.FEAR_GAIN, fear_gain=10)
    )

    context_in = {"current_time": "09:00", "actor_location": None, "actor_items": []}
    context_out = {"current_time": "13:00", "actor_location": None, "actor_items": []}

    assert rule.can_trigger(context_in) is True
    assert rule.can_trigger(context_out) is False


@pytest.mark.unit
def test_time_range_overnight_interval():
    rule = Rule(
        id="r2",
        name="overnight",
        trigger=TriggerCondition(action="act", time_range={"from": "22:00", "to": "02:00"}),
        effect=RuleEffect(type=EffectType.FEAR_GAIN, fear_gain=10)
    )

    context_in_late = {"current_time": "23:30", "actor_location": None, "actor_items": []}
    context_in_early = {"current_time": "01:30", "actor_location": None, "actor_items": []}
    context_out = {"current_time": "03:00", "actor_location": None, "actor_items": []}

    assert rule.can_trigger(context_in_late) is True
    assert rule.can_trigger(context_in_early) is True
    assert rule.can_trigger(context_out) is False
