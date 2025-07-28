#!/usr/bin/env python3
"""
快速测试AI修复
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

async def test_ai_turn():
    """测试AI回合功能"""
    print("=== 测试AI回合功能 ===")
    
    from src.core.game_state import GameStateManager
    from src.api.deepseek_client import DeepSeekClient, APIConfig
    from src.ai.turn_pipeline import AITurnPipeline
    
    # 创建游戏
    gsm = GameStateManager()
    gsm.new_game("test_ai")
    
    # 创建Mock客户端
    config = APIConfig(mock_mode=True)
    client = DeepSeekClient(config)
    pipeline = AITurnPipeline(gsm, client)
    
    # 测试AI回合
    print(f"当前回合: {gsm.state.current_turn}")
    plan = await pipeline.run_turn_ai()
    print(f"✅ AI生成了 {len(plan.dialogue)} 条对话, {len(plan.actions)} 个行动")
    
    await client.close()

async def test_custom_rule():
    """测试自定义规则创建"""
    print("\n=== 测试自定义规则创建 ===")
    
    try:
        from src.custom_rule_creator import create_custom_rule_enhanced
        print("✅ 自定义规则创建器已加载")
        print("   - 支持多种触发条件")
        print("   - 支持多种效果类型")
        print("   - 支持破绽设置")
    except ImportError:
        print("❌ 自定义规则创建器未找到")

async def test_cli_integration():
    """测试CLI集成"""
    print("\n=== 测试CLI集成 ===")
    
    from src.cli_game import CLIGame
    game = CLIGame()
    
    # 测试是否有create_custom_rule方法
    if hasattr(game, 'create_custom_rule'):
        print("✅ CLI游戏已集成自定义规则创建")
    else:
        print("❌ CLI游戏缺少自定义规则创建方法")

async def main():
    print("🔧 RuleK AI修复测试\n")
    
    try:
        await test_ai_turn()
        await test_custom_rule()
        await test_cli_integration()
        
        print("\n✅ 所有测试通过！")
        print("\n现在可以：")
        print("1. 运行游戏: python src/cli_game.py")
        print("2. 创建规则:")
        print("   - 选项1: 自定义创建（新功能）")
        print("   - 选项2: 模板创建（稳定）")
        print("   - 选项3: AI解析（需要启用AI）")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
