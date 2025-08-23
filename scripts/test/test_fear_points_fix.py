#!/usr/bin/env python
"""
测试修复验证 - 测试AI创建规则时恐惧积分扣除
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.game_state import GameStateManager
from unittest.mock import AsyncMock, MagicMock
import asyncio

async def test_ai_create_rule_deducts_points():
    """测试AI创建规则时正确扣除恐惧积分"""
    print("\n🧪 测试AI创建规则时的恐惧积分扣除...")
    
    # 创建游戏管理器
    game_manager = GameStateManager()
    game_manager.ai_enabled = True
    
    # 创建新游戏
    game_manager.new_game("test_game", config={
        "initial_fear_points": 1000,
        "create_test_npcs": True,
        "test_npc_count": 3
    })
    
    # 记录初始积分
    initial_points = game_manager.state.fear_points
    print(f"  初始恐惧积分: {initial_points}")
    
    # 创建规则数据
    rule_data = {
        "name": "黑暗禁令",
        "description": "晚上不能开灯",
        "cost": 150,  # 成本
        "difficulty": 5,
        "trigger": {"action": "custom"},
        "effect": {"type": "fear_gain", "fear_gain": 30}
    }
    
    # 调用create_rule方法
    rule_id = game_manager.create_rule(rule_data)
    
    # 验证结果
    if rule_id:
        current_points = game_manager.state.fear_points
        expected_points = initial_points - rule_data["cost"]
        
        print(f"  规则ID: {rule_id}")
        print(f"  当前恐惧积分: {current_points}")
        print(f"  预期恐惧积分: {expected_points}")
        
        if current_points == expected_points:
            print("  ✅ 测试通过：恐惧积分正确扣除！")
            return True
        else:
            print(f"  ❌ 测试失败：积分扣除错误 (差值: {current_points - expected_points})")
            return False
    else:
        print("  ❌ 测试失败：规则创建失败")
        return False

async def test_insufficient_points():
    """测试积分不足时不能创建规则"""
    print("\n🧪 测试积分不足时的规则创建...")
    
    # 创建游戏管理器
    game_manager = GameStateManager()
    
    # 创建新游戏，设置很少的积分
    game_manager.new_game("test_game_2", config={
        "initial_fear_points": 50,  # 只有50积分
        "create_test_npcs": True,
        "test_npc_count": 3
    })
    
    initial_points = game_manager.state.fear_points
    print(f"  初始恐惧积分: {initial_points}")
    
    # 尝试创建成本高于积分的规则
    rule_data = {
        "name": "昂贵规则",
        "cost": 200,  # 成本200，但只有50积分
        "trigger": {"action": "custom"},
        "effect": {"type": "fear_gain"}
    }
    
    # 调用create_rule方法
    rule_id = game_manager.create_rule(rule_data)
    
    # 验证结果
    current_points = game_manager.state.fear_points
    
    if not rule_id and current_points == initial_points:
        print(f"  当前恐惧积分: {current_points} (未变化)")
        print("  ✅ 测试通过：积分不足时正确拒绝创建规则！")
        return True
    else:
        print(f"  ❌ 测试失败：不应该创建规则或扣除积分")
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🔧 RuleK 恐惧积分扣除修复验证")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(await test_ai_create_rule_deducts_points())
    results.append(await test_insufficient_points())
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"  通过: {passed}/{total}")
    
    if all(results):
        print("\n✅ 所有测试通过！修复成功！")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查代码。")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
