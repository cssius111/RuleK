#!/usr/bin/env python3
"""
快速测试游戏创建和NPC生成
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from web.backend.services.game_service import GameService
from web.backend.services.session_manager import SessionManager


async def test_game_creation():
    """测试游戏创建流程"""
    print("="*60)
    print("测试游戏创建和NPC生成")
    print("="*60)
    
    # 创建会话管理器
    session_manager = SessionManager()
    
    # 创建新游戏（4个NPC）
    print("\n1. 创建新游戏（4个NPC）...")
    game_service = await session_manager.create_game(
        difficulty="normal",
        npc_count=4
    )
    
    print(f"   游戏ID: {game_service.game_id}")
    print(f"   难度: {game_service.difficulty}")
    print(f"   设置的NPC数量: {game_service.npc_count}")
    
    # 获取游戏状态
    state = game_service.get_state_response()
    
    print(f"\n2. 实际创建的NPC数量: {len(state.npcs)}")
    print("\n3. NPC列表:")
    for i, npc in enumerate(state.npcs):
        print(f"   [{i+1}] {npc.name}")
        print(f"       - HP: {npc.hp}, 理智: {npc.sanity}, 恐惧: {npc.fear}")
        print(f"       - 位置: {npc.location}")
        print(f"       - 存活: {npc.is_alive}")
    
    # 检查是否有硬编码的中文名字
    chinese_names = ["张三", "李四", "王五", "张明", "李静", "王芳"]
    found_chinese = []
    for npc in state.npcs:
        if npc.name in chinese_names:
            found_chinese.append(npc.name)
    
    if found_chinese:
        print(f"\n⚠️  发现硬编码的中文名字: {found_chinese}")
        print("   这些NPC可能是测试数据或默认创建的")
    else:
        print("\n✅ 没有发现硬编码的中文名字")
    
    # 测试规则创建
    print("\n4. 测试规则创建...")
    print(f"   当前恐惧点数: {state.fear_points}")
    
    try:
        # 创建一个简单的规则
        rule_data = {
            "name": "Test Rule",
            "description": "A test rule",
            "cost": 100,
            "trigger": {
                "type": "manual",
                "probability": 0.8
            },
            "effect": {
                "type": "fear_gain",
                "value": 50
            }
        }
        
        rule_id = await game_service.create_rule(rule_data)
        print(f"   ✅ 规则创建成功: {rule_id}")
        print(f"   剩余恐惧点数: {game_service.game_state.fear_points}")
    except Exception as e:
        print(f"   ❌ 规则创建失败: {e}")
    
    # 清理
    await session_manager.cleanup()
    print("\n测试完成！")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_game_creation())
