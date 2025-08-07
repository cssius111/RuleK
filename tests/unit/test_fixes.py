#!/usr/bin/env python3
"""
Test suite for API fixes
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType
from src.ai.action_schema import AIAction


def test_rule_creation():
    """Test rule creation with proper structure"""
    # Test data similar to API request
    rule_data = {
        "name": "Test Rule",
        "description": "Test description",
        "trigger": {"type": "time"},
        "effect": {"type": "damage", "value": 10},
        "cost": 100
    }
    
    # Create rule components
    trigger = TriggerCondition(
        action=rule_data["trigger"].get("type", "manual"),
        probability=0.8
    )
    
    effect = RuleEffect(
        type=EffectType.FEAR_GAIN,
        fear_gain=rule_data["effect"].get("value", 50)
    )
    
    # Create rule
    rule = Rule(
        id="test_rule_001",
        name=rule_data["name"],
        description=rule_data["description"],
        trigger=trigger,
        effect=effect,
        base_cost=rule_data["cost"]
    )
    
    assert rule.id == "test_rule_001"
    assert rule.name == "Test Rule"
    assert rule.trigger.action == "time"
    assert rule.effect.type == EffectType.FEAR_GAIN


def test_ai_action_priority():
    """Test AI action priority field handling"""
    # Test with int
    action1 = AIAction(
        npc="NPC_1",
        action="move",
        reason="test",
        priority=3
    )
    assert action1.priority == 3
    
    # Test with string (should convert)
    action2_data = {
        "npc": "NPC_2",
        "action": "talk",
        "reason": "test",
        "priority": "4"
    }
    action2 = AIAction(**action2_data)
    assert isinstance(action2.priority, int)
    assert action2.priority == 4
    
    # Test with invalid value (should default)
    action3_data = {
        "npc": "NPC_3",
        "action": "look",
        "reason": "test",
        "priority": "invalid"
    }
    action3 = AIAction(**action3_data)
    assert action3.priority == 1
    
    # Test with out of range (should clamp)
    action4 = AIAction(
        npc="NPC_4",
        action="run",
        reason="test",
        priority=10
    )
    assert action4.priority == 5


if __name__ == "__main__":
    test_rule_creation()
    print("✅ Rule creation test passed")
    
    test_ai_action_priority()
    print("✅ AI action priority test passed")
    
    print("\n✅ All tests passed!")
