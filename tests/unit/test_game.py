#!/usr/bin/env python3
"""
游戏核心功能单元测试
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))


def test_imports():
    """测试所有模块是否能正常导入"""
    from src.core.game_state import GameStateManager
    from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType
    from src.models.npc import NPC, generate_random_npc
    from src.ui.cli import CLI
    
    # 如果导入失败会抛出 ImportError
    assert GameStateManager is not None
    assert Rule is not None
    assert NPC is not None
    assert CLI is not None


def test_game_state():
    """测试游戏状态管理"""
    from src.core.game_state import GameStateManager
    
    gsm = GameStateManager()
    state = gsm.new_game("test_001")
    
    assert state.game_id == "test_001"
    assert state.fear_points == 1000
    
    gsm.add_fear_points(100, "测试")
    assert gsm.state.fear_points == 1100


def test_npc_creation():
    """测试NPC创建"""
    from src.models.npc import generate_random_npc
    
    npc = generate_random_npc("测试NPC")
    assert npc.name == "测试NPC"
    assert 0 <= npc.hp <= 100
    assert hasattr(npc, 'personality')
    
    # 测试行为决策
    action = npc.decide_action({})
    assert action is not None


def test_rule_creation():
    """测试规则创建"""
    from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType
    
    rule = Rule(
        id="test_rule",
        name="测试规则",
        trigger=TriggerCondition(action="test_action"),
        effect=RuleEffect(type=EffectType.FEAR_GAIN, fear_gain=50)
    )
    
    assert rule.name == "测试规则"
    cost = rule.calculate_total_cost()
    assert cost > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
