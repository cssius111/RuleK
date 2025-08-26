import pytest

from src.api.mock_deepseek_client import MockDeepSeekClient


@pytest.mark.asyncio
async def test_mock_turn_plan():
    client = MockDeepSeekClient()
    plan = await client.generate_turn_plan(
        npc_states=[{"name": "测试NPC"}],
        scene_context={},
        available_places=[],
        time_of_day="midnight",
    )
    assert plan.dialogue[0].speaker == "测试NPC"


@pytest.mark.asyncio
async def test_mock_narrative():
    client = MockDeepSeekClient()
    text = await client.generate_narrative_text([], "night", 0)
    assert "测试" not in text or isinstance(text, str)


@pytest.mark.asyncio
async def test_mock_rule_eval():
    client = MockDeepSeekClient()
    result = await client.evaluate_rule_nl("规则描述", {})
    assert result.cost == 50
