#!/usr/bin/env python3
"""
快速测试修复效果
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 设置测试环境
os.environ['PYTEST_RUNNING'] = '1'

from src.core.game_state import GameStateManager

def test_game_state_with_test_npcs():
    """测试带测试NPC的游戏状态管理"""
    print("测试游戏状态管理...")
    
    game_manager = GameStateManager()
    # 为测试创建NPC
    state = game_manager.new_game(config={"create_test_npcs": True, "test_npc_count": 3})
    
    assert state is not None, "游戏状态应该被创建"
    assert state.game_id is not None, "游戏ID应该存在"
    assert state.fear_points == 1000, "初始恐惧积分应该是1000"
    assert len(state.npcs) > 0, f"应该有NPC被创建，但实际有 {len(state.npcs)} 个"
    
    print(f"✅ 测试通过！创建了 {len(state.npcs)} 个NPC")
    
    # 打印NPC信息
    for npc_id, npc_data in state.npcs.items():
        print(f"  - {npc_data['name']} (ID: {npc_id})")
    
    return True

def test_normal_game_without_test_npcs():
    """测试正常游戏（不创建测试NPC）"""
    print("\n测试正常游戏模式...")
    
    game_manager = GameStateManager()
    # 正常游戏不创建测试NPC
    state = game_manager.new_game()
    
    assert state is not None, "游戏状态应该被创建"
    assert len(state.npcs) == 0, f"不应该自动创建NPC，但实际有 {len(state.npcs)} 个"
    
    print(f"✅ 测试通过！没有自动创建NPC")
    
    return True

def test_add_npc():
    """测试添加NPC功能"""
    print("\n测试添加NPC...")
    
    game_manager = GameStateManager()
    state = game_manager.new_game()
    
    # 手动添加NPC
    npc_data = {
        "id": "test_npc_1",
        "name": "Test NPC",
        "hp": 100,
        "sanity": 100,
        "fear": 0,
        "location": "living_room",
        "alive": True
    }
    
    game_manager.add_npc(npc_data)
    
    assert len(state.npcs) == 1, "应该有1个NPC"
    assert "test_npc_1" in state.npcs, "NPC应该被添加到状态中"
    
    print(f"✅ 测试通过！成功添加NPC")
    
    return True

def test_get_alive_npcs():
    """测试获取存活NPC"""
    print("\n测试获取存活NPC...")
    
    game_manager = GameStateManager()
    game_manager.new_game(config={"create_test_npcs": True, "test_npc_count": 3})
    
    alive_npcs = game_manager.get_alive_npcs()
    assert len(alive_npcs) == 3, f"应该有3个存活的NPC，但实际有 {len(alive_npcs)} 个"
    
    # 杀死一个NPC
    first_npc_id = list(game_manager.state.npcs.keys())[0]
    game_manager.state.npcs[first_npc_id]["alive"] = False
    game_manager.state.npcs[first_npc_id]["hp"] = 0
    
    alive_npcs = game_manager.get_alive_npcs()
    assert len(alive_npcs) == 2, f"应该有2个存活的NPC，但实际有 {len(alive_npcs)} 个"
    
    print(f"✅ 测试通过！正确统计存活NPC")
    
    return True

def main():
    print("="*60)
    print("测试修复验证")
    print("="*60)
    
    tests = [
        test_game_state_with_test_npcs,
        test_normal_game_without_test_npcs,
        test_add_npc,
        test_get_alive_npcs
    ]
    
    results = []
    for test in tests:
        try:
            success = test()
            results.append((test.__name__, success))
        except Exception as e:
            print(f"❌ {test.__name__} 失败: {e}")
            results.append((test.__name__, False))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name:40} {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试都通过了！")
        return 0
    else:
        print(f"\n⚠️  还有 {total - passed} 个测试需要修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
