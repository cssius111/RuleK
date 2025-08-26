"""
最终修复验证脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)

async def main():
    print_section("RuleK AI集成修复验证")
    
    all_passed = True
    
    # 1. 测试基础导入
    print_section("1. 测试基础导入")
    try:
        from src.utils.config import Config, load_config
        from src.core.game_state import GameState, GameStateManager
        from src.api.deepseek_client import DeepSeekClient
        from src.api.deepseek_http_client import APIConfig
        from src.ai.turn_pipeline import AITurnPipeline
        print("✅ 所有基础模块导入成功")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        all_passed = False
        return
    
    # 2. 测试配置系统
    print_section("2. 测试配置系统")
    try:
        config = load_config()
        print(f"✅ Config类型: {type(config)}")
        
        # 测试配置访问
        save_dir = config.get('save_dir', 'data/saves')
        print(f"✅ save_dir: {save_dir}")
        
        # 测试嵌套配置访问
        if hasattr(config, '_config'):
            game_cfg = config._config.get('game', {})
            print(f"✅ 游戏配置: 初始恐惧点={game_cfg.get('initial_fear_points', 1000)}")
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        all_passed = False
    
    # 3. 测试GameStateManager
    print_section("3. 测试GameStateManager")
    try:
        gsm = GameStateManager(save_dir="data/saves", config={"ai_enabled": False})
        gsm.new_game("test_game")
        print(f"✅ GameStateManager创建成功")
        print(f"   - 游戏ID: {gsm.state.game_id}")
        print(f"   - 恐惧点: {gsm.state.fear_points}")
    except Exception as e:
        print(f"❌ GameStateManager测试失败: {e}")
        all_passed = False
    
    # 4. 测试GameService
    print_section("4. 测试GameService")
    try:
        from web.backend.services.game_service import GameService
        
        game_service = GameService(npc_count=4)
        print("✅ GameService创建成功")
        
        await game_service.initialize()
        print("✅ GameService初始化成功")
        
        # 验证关键组件
        components = [
            ('game_state_manager', game_service.game_state_manager),
            ('game_state', game_service.game_state),
            ('npc_behavior', game_service.npc_behavior),
            ('rule_executor', game_service.rule_executor),
            ('deepseek_client', game_service.deepseek_client),
            ('map_manager', game_service.map_manager),
        ]
        
        for name, component in components:
            if component is None:
                print(f"❌ {name} 是 None")
                all_passed = False
            else:
                print(f"✅ {name}: {type(component).__name__}")
        
        # 测试游戏状态
        print(f"\n游戏状态:")
        print(f"   - 游戏ID: {game_service.game_id}")
        print(f"   - NPC数量: {len(game_service.game_state.npcs)}")
        print(f"   - 恐惧积分: {game_service.game_state.fear_points}")
        
    except Exception as e:
        print(f"❌ GameService测试失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # 5. 测试Web App
    print_section("5. 测试Web App导入")
    try:
        from web.backend.app import app
        print("✅ FastAPI app导入成功")
        
        # 计算路由数量
        route_count = len([r for r in app.routes if hasattr(r, 'path')])
        print(f"✅ 已注册 {route_count} 个路由")
    except Exception as e:
        print(f"❌ Web app导入失败: {e}")
        all_passed = False
    
    # 6. 测试AI功能（可选）
    print_section("6. AI功能状态")
    try:
        if hasattr(game_service, 'ai_pipeline'):
            if game_service.ai_pipeline:
                print("✅ AI管线已初始化")
            else:
                print("ℹ️  AI管线未初始化（需要调用init_ai_pipeline）")
        
        # 检查API配置
        api_config = APIConfig()
        if api_config.api_key:
            print("✅ DeepSeek API密钥已配置")
        else:
            print("⚠️  DeepSeek API密钥未配置（将使用Mock模式）")
    except Exception as e:
        print(f"⚠️  AI功能检查失败: {e}")
    
    # 总结
    print_section("验证结果")
    if all_passed:
        print("✅ 所有测试通过！")
        print("\n下一步:")
        print("1. 运行Web服务器: python start_web_server.py")
        print("2. 访问API文档: http://localhost:8000/docs")
        print("3. 测试游戏功能")
    else:
        print("❌ 有测试失败，请检查错误信息")

if __name__ == "__main__":
    # 禁用一些警告
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
    
    asyncio.run(main())
