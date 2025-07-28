"""
修复后的AI集成测试
"""
import asyncio
import logging
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger

# 设置日志
logger = setup_logger("test_ai_fixed")


async def test_game_service_with_fix():
    """测试修复后的GameService"""
    logger.info("=== 测试修复后的GameService ===")
    
    try:
        from web.backend.services.game_service import GameService
        
        # 创建游戏服务
        game_service = GameService(npc_count=4)
        logger.info("✅ GameService创建成功")
        
        # 初始化
        await game_service.initialize()
        logger.info("✅ GameService初始化成功")
        
        # 检查关键组件
        assert hasattr(game_service, 'game_state_manager'), "缺少game_state_manager"
        assert hasattr(game_service, 'npc_behavior'), "缺少npc_behavior"
        assert hasattr(game_service, 'rule_executor'), "缺少rule_executor"
        
        logger.info("✅ 所有关键组件都已创建")
        logger.info(f"  - 游戏ID: {game_service.game_id}")
        logger.info(f"  - NPC数量: {len(game_service.game_state.npcs)}")
        logger.info(f"  - 恐惧积分: {game_service.game_state.fear_points}")
        
        # 测试AI初始化
        logger.info("\n测试AI初始化...")
        result = await game_service.init_ai_pipeline()
        if result:
            logger.info("✅ AI管线初始化成功")
        else:
            logger.warning("⚠️ AI管线初始化失败（可能需要API密钥）")
        
        return game_service
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_web_server_startup():
    """测试Web服务器启动（不实际启动）"""
    logger.info("\n=== 测试Web服务器配置 ===")
    
    try:
        from web.backend.app import app
        logger.info("✅ FastAPI app导入成功")
        
        # 检查路由
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        logger.info(f"✅ 已注册 {len(routes)} 个路由")
        
        # 检查AI相关路由
        ai_routes = [r for r in routes if 'ai' in r.lower()]
        if ai_routes:
            logger.info(f"✅ 找到 {len(ai_routes)} 个AI相关路由:")
            for route in ai_routes[:5]:  # 最多显示5个
                logger.info(f"    - {route}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Web服务器测试失败: {e}")
        return False


async def main():
    """运行所有测试"""
    logger.info("📝 === 开始修复后的测试 ===\n")
    
    # 1. 测试GameService
    game_service = await test_game_service_with_fix()
    if not game_service:
        logger.error("❌ GameService测试失败，停止后续测试")
        return
    
    # 2. 测试Web服务器配置
    await test_web_server_startup()
    
    logger.info("\n✅ === 所有测试完成 ===")
    logger.info("\n下一步:")
    logger.info("1. 运行 Web 服务器: python start_web_server.py")
    logger.info("2. 访问 http://localhost:8000/docs 查看API文档")
    logger.info("3. 测试AI端点（需要有效的DeepSeek API密钥）")


if __name__ == "__main__":
    asyncio.run(main())
