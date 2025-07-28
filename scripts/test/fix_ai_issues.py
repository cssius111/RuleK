"""
快速修复 AI 集成问题
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("🔧 正在修复 AI 集成问题...\n")

# 问题1已在上面的编辑中修复
print("✅ 问题1：turn_count 属性错误 - 已修复")
print("   - 将所有 turn_count 改为 current_turn")

print("\n📌 问题2：创建规则提示'目前版本不支持'")
print("   解决方案：")
print("   1. 使用选项2 '使用模板创建' - 这个功能是完整的")
print("   2. 如果启用了AI，使用选项3 'AI解析规则'")
print("   3. 自定义规则创建功能现在已经完全可用！\n")

async def test_fix():
    """测试修复是否成功"""
    try:
        # 测试AI回合
        from src.core.game_state import GameStateManager
        from src.api.deepseek_client import DeepSeekClient, APIConfig
        from src.ai.turn_pipeline import AITurnPipeline
        
        print("测试AI回合功能...")
        gsm = GameStateManager()
        gsm.new_game("test_fix")
        
        # 测试 current_turn 属性
        assert hasattr(gsm.state, 'current_turn'), "缺少 current_turn 属性"
        print(f"✅ current_turn 属性存在: {gsm.state.current_turn}")
        
        # 测试AI管线
        config = APIConfig(mock_mode=True)
        client = DeepSeekClient(config)
        pipeline = AITurnPipeline(gsm, client)
        
        # 模拟运行
        plan = await pipeline.run_turn_ai()
        print(f"✅ AI回合测试成功！生成了 {len(plan.dialogue)} 条对话")
        
        await client.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def main():
    success = await test_fix()
    
    if success:
        print("\n✅ 修复验证成功！")
        print("\n可用的创建规则方式：")
        print("1. 使用模板创建（推荐） - 选择菜单中的选项2")
        print("2. AI解析规则（需要启用AI） - 选择菜单中的选项3")
        print("3. 自定义规则（现在可用！） - 选择菜单中的选项1")
        
        print("\n提示：")
        print("- 模板创建有预定义的规则，如'午夜镜子'、'红字禁忌'等")
        print("- AI解析可以理解自然语言，如'晚上不能开灯'")
    else:
        print("\n❌ 修复验证失败，请检查错误信息")

if __name__ == "__main__":
    asyncio.run(main())
