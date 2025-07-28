"""
快速验证修复
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("验证修复...")

# 1. 验证GameService初始化
try:
    import asyncio
    from web.backend.services.game_service import GameService
    
    async def quick_test():
        game_service = GameService()
        await game_service.initialize()
        
        # 检查关键属性
        assert hasattr(game_service, 'game_state_manager'), "缺少game_state_manager"
        assert game_service.game_state_manager is not None, "game_state_manager是None"
        assert hasattr(game_service, 'npc_behavior'), "缺少npc_behavior"
        assert hasattr(game_service, 'rule_executor'), "缺少rule_executor"
        
        print("✅ GameService初始化成功!")
        print(f"   - game_state_manager: {type(game_service.game_state_manager)}")
        print(f"   - npc_behavior: {type(game_service.npc_behavior)}")
        print(f"   - rule_executor: {type(game_service.rule_executor)}")
        
        return True
    
    success = asyncio.run(quick_test())
    
except Exception as e:
    print(f"❌ 验证失败: {e}")
    import traceback
    traceback.print_exc()
    success = False

# 2. 验证Web服务器导入
try:
    from web.backend.app import app
    print("\n✅ Web app导入成功")
except Exception as e:
    print(f"\n❌ Web app导入失败: {e}")

print("\n" + "="*50)
if success:
    print("✅ 修复验证通过！现在可以运行:")
    print("   python start_web_server.py")
else:
    print("❌ 修复验证失败，请检查错误信息")
