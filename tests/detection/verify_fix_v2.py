"""
再次验证修复
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("验证修复（第二次）...")

async def test():
    try:
        # 1. 测试Config类
        from src.utils.config import Config, load_config
        config = load_config()
        print(f"✅ Config加载成功: {type(config)}")
        print(f"   - 能访问get方法: {hasattr(config, 'get')}")
        print(f"   - 能访问_config: {hasattr(config, '_config')}")
        
        # 2. 测试GameStateManager
        from src.core.game_state import GameStateManager
        gsm = GameStateManager(save_dir="data/saves", config={"ai_enabled": False})
        print(f"✅ GameStateManager创建成功")
        
        # 3. 测试GameService
        from web.backend.services.game_service import GameService
        game_service = GameService()
        await game_service.initialize()
        
        print(f"✅ GameService初始化成功")
        print(f"   - game_state_manager: {type(game_service.game_state_manager)}")
        print(f"   - game_state: {game_service.game_state is not None}")
        print(f"   - npc_behavior: {type(game_service.npc_behavior)}")
        print(f"   - rule_executor: {type(game_service.rule_executor)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    print("\n" + "="*50)
    if success:
        print("✅ 所有测试通过！可以启动Web服务器了")
    else:
        print("❌ 测试失败，请检查错误")
