"""
简化的AI集成测试
逐步测试各个组件
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
logger = setup_logger("test_ai_simple")


async def test_basic_imports():
    """测试基本导入"""
    logger.info("测试基本导入...")
    
    try:
        # 1. 导入GameState相关
        from src.core.game_state import GameState, GameStateManager
        logger.info("✅ GameState导入成功")
        
        # 2. 导入MapManager
        from src.models.map import MapManager
        logger.info("✅ MapManager导入成功")
        
        # 3. 导入NPCManager
        from src.models.npc_manager import NPCManager
        logger.info("✅ NPCManager导入成功")
        
        # 4. 导入其他必要组件
        from src.core.narrator import Narrator
        from src.core.dialogue_system import DialogueSystem
        from src.core.event_system import EventSystem
        from src.core.npc_behavior import NPCBehavior
        from src.core.rule_executor import RuleExecutor
        logger.info("✅ 所有核心组件导入成功")
        
        return True
    except ImportError as e:
        logger.error(f"❌ 导入失败: {e}")
        return False


async def test_game_service_basic():
    """测试GameService基本功能（不含AI）"""
    logger.info("\n测试GameService基本功能...")
    
    try:
        from web.backend.services.game_service import GameService
        
        # 创建游戏服务
        game_service = GameService(npc_count=4)
        logger.info("✅ GameService创建成功")
        
        # 初始化（不包括AI）
        await game_service.initialize()
        logger.info("✅ GameService初始化成功")
        
        # 检查组件
        logger.info(f"  - 游戏ID: {game_service.game_id}")
        logger.info(f"  - NPC数量: {len(game_service.game_state.npcs)}")
        logger.info(f"  - 地图区域: {len(game_service.map_manager.areas)}")
        
        return game_service
    except Exception as e:
        logger.error(f"❌ GameService测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_ai_components():
    """测试AI组件"""
    logger.info("\n测试AI组件...")
    
    try:
        # 1. 测试DeepSeek客户端
        from src.api.deepseek_client import DeepSeekClient, APIConfig
        api_config = APIConfig()
        logger.info(f"✅ API配置加载成功 (Model: {api_config.model})")
        
        # 2. 创建客户端
        ds_client = DeepSeekClient(api_config)
        logger.info("✅ DeepSeek客户端创建成功")
        
        # 3. 测试AI管线
        from src.ai.turn_pipeline import AITurnPipeline
        from src.core.game_state import GameStateManager
        
        # 创建一个简单的GameStateManager
        gsm = GameStateManager()
        gsm.new_game("test_game")
        logger.info("✅ GameStateManager创建成功")
        
        # 创建AI管线
        ai_pipeline = AITurnPipeline(gsm, ds_client)
        logger.info("✅ AI管线创建成功")
        
        return True
    except Exception as e:
        logger.error(f"❌ AI组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ai_integration_simple():
    """测试简单的AI集成"""
    logger.info("\n测试AI集成...")
    
    try:
        from web.backend.services.game_service import GameService
        
        # 创建并初始化游戏
        game_service = GameService(npc_count=2)  # 使用较少的NPC
        await game_service.initialize()
        logger.info("✅ 游戏初始化成功")
        
        # 初始化AI
        success = await game_service.init_ai_pipeline()
        if not success:
            logger.error("❌ AI初始化失败")
            return False
        
        logger.info("✅ AI初始化成功")
        
        # 测试AI状态
        logger.info(f"  - AI启用: {game_service.is_ai_enabled()}")
        logger.info(f"  - AI已初始化: {game_service.is_ai_initialized()}")
        
        # 测试规则评估（最简单的AI功能）
        logger.info("\n测试规则评估...")
        try:
            result = await game_service.evaluate_rule_nl("晚上不能开灯")
            logger.info(f"✅ 规则评估成功: {result.get('name', 'Unknown')}")
            logger.info(f"  - 成本: {result.get('cost', 0)}")
            logger.info(f"  - 难度: {result.get('difficulty', 0)}")
        except Exception as e:
            logger.error(f"❌ 规则评估失败: {e}")
        
        # 清理
        await game_service.cleanup()
        
        return True
    except Exception as e:
        logger.error(f"❌ AI集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试流程"""
    logger.info("=== 开始AI集成简化测试 ===\n")
    
    # 1. 测试基本导入
    if not await test_basic_imports():
        logger.error("基本导入失败，停止测试")
        return
    
    # 2. 测试GameService基本功能
    game_service = await test_game_service_basic()
    if not game_service:
        logger.error("GameService基本功能测试失败")
        return
    
    # 清理第一个测试的资源
    await game_service.cleanup()
    
    # 3. 测试AI组件
    if not await test_ai_components():
        logger.error("AI组件测试失败")
        return
    
    # 4. 测试AI集成
    if not await test_ai_integration_simple():
        logger.error("AI集成测试失败")
        return
    
    logger.info("\n=== 所有测试完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
