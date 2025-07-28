#!/usr/bin/env python3
"""
最小化测试 - 只测试核心功能
"""
import asyncio
import warnings
warnings.filterwarnings("ignore")

async def test():
    print("🔧 最小化测试开始...\n")
    
    try:
        # 测试GameService初始化
        from web.backend.services.game_service import GameService
        
        print("1. 创建GameService...")
        game = GameService()
        
        print("2. 初始化游戏...")
        await game.initialize()
        
        print("3. 检查核心组件...")
        print(f"   ✓ game_state_manager: {'✅' if game.game_state_manager else '❌'}")
        print(f"   ✓ npc_behavior: {'✅' if game.npc_behavior else '❌'}")
        print(f"   ✓ rule_executor: {'✅' if game.rule_executor else '❌'}")
        
        print("\n✅ 核心功能测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    
    success = asyncio.run(test())
    
    if success:
        print("\n现在可以运行: python start_web_server.py")
    else:
        print("\n请检查错误信息")
