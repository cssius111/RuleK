#!/usr/bin/env python3
"""
游戏核心功能测试
"""
import pytest
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from src.core.game_state import GameStateManager
from src.core.rule_executor import RuleExecutor, RuleContext
from src.core.npc_behavior import NPCBehavior
from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType, RULE_TEMPLATES


@pytest.mark.asyncio
async def test_game_state_manager():
    """测试游戏状态管理"""
    game_manager = GameStateManager()
    # 为测试创建NPC
    state = game_manager.new_game(config={"create_test_npcs": True, "test_npc_count": 3})
    
    assert state is not None
    assert state.game_id is not None
    assert state.fear_points == 1000
    assert len(state.npcs) > 0


@pytest.mark.asyncio
async def test_rule_creation():
    """测试规则创建"""
    template = RULE_TEMPLATES.get("mirror_death")
    
    if template:
        mirror_rule = Rule(
            id="test_rule_001",
            **template
        )
        
        cost = mirror_rule.calculate_total_cost()
        assert cost > 0
        assert mirror_rule.name is not None


@pytest.mark.asyncio
async def test_npc_behavior():
    """测试NPC行为系统"""
    game_manager = GameStateManager()
    # 为测试创建NPC
    game_manager.new_game(config={"create_test_npcs": True, "test_npc_count": 3})
    npc_behavior = NPCBehavior(game_manager)
    
    # 确保有NPC
    assert len(game_manager.state.npcs) > 0, "No NPCs created for test"
    
    # 随机选一个NPC测试
    test_npc = list(game_manager.state.npcs.values())[0]
    assert test_npc is not None
    
    decision = npc_behavior.decide_action(test_npc)
    assert decision is not None
    assert hasattr(decision, 'action')
    assert hasattr(decision, 'target')
    assert hasattr(decision, 'reason')


@pytest.mark.asyncio
async def test_rule_executor():
    """测试规则执行引擎"""
    game_manager = GameStateManager()
    # 为测试创建NPC
    game_manager.new_game(config={"create_test_npcs": True, "test_npc_count": 3})
    rule_executor = RuleExecutor(game_manager)
    
    # 添加测试规则
    template = RULE_TEMPLATES.get("mirror_death")
    if template:
        mirror_rule = Rule(
            id="test_rule_001",
            **template
        )
        game_manager.add_rule(mirror_rule)
        
        # 确保有NPC
        assert len(game_manager.state.npcs) > 0, "No NPCs created for test"
        
        # 创建一个会触发规则的上下文
        test_npc = list(game_manager.state.npcs.values())[0]
        test_npc["location"] = "bathroom"
        test_npc["inventory"] = ["mirror"]
        game_manager.state.current_time = "01:00"
        
        context = RuleContext(
            actor=test_npc,
            action="look_mirror",
            game_state=game_manager.state.to_dict()
        )
        
        # 检查规则
        triggered_rules = rule_executor.check_all_rules(context)
        assert isinstance(triggered_rules, list)


@pytest.mark.asyncio
async def test_game_save_load():
    """测试游戏保存/加载"""
    game_manager = GameStateManager()
    # 为测试创建NPC
    game_manager.new_game(config={"create_test_npcs": True, "test_npc_count": 3})
    
    # 保存游戏
    save_path = game_manager.save_game("test_save")
    assert isinstance(save_path, str)
    
    # 创建新的管理器并加载
    new_manager = GameStateManager()
    loaded = new_manager.load_game("test_save")
    assert loaded is True
    assert new_manager.state.fear_points == game_manager.state.fear_points


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
