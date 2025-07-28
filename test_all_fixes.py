#!/usr/bin/env python3
"""
综合测试验证脚本
验证所有修复是否正常工作
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_file_saving():
    """测试文件保存修复"""
    print("\n🧪 测试文件保存修复...")
    
    from src.core.game_state import GameStateManager
    
    gsm = GameStateManager()
    gsm.new_game("test_save_fix")
    
    # 测试不同的文件名情况
    test_cases = [
        ("test_save", "test_save.json"),
        ("test_save.json", "test_save.json"),
        ("my_save_file", "my_save_file.json"),
        ("my_save_file.json", "my_save_file.json"),
    ]
    
    success = True
    for input_name, expected_name in test_cases:
        path = gsm.save_game(input_name)
        if path:
            actual_name = Path(path).name
            if actual_name == expected_name:
                print(f"✅ 输入 '{input_name}' -> 输出 '{actual_name}' (正确)")
            else:
                print(f"❌ 输入 '{input_name}' -> 输出 '{actual_name}' (期望 '{expected_name}')")
                success = False
        else:
            print(f"❌ 保存失败: {input_name}")
            success = False
    
    # 清理测试文件
    for input_name, _ in test_cases:
        for ext in ['', '.json']:
            test_file = gsm.save_dir / f"{input_name}{ext}"
            if test_file.exists():
                test_file.unlink()
    
    return success


async def test_api_methods():
    """测试 API 方法修复"""
    print("\n🧪 测试 DeepSeek API 方法...")
    
    from src.api.deepseek_client import DeepSeekClient, APIConfig
    
    # 使用 Mock 模式测试
    config = APIConfig(mock_mode=True)
    client = DeepSeekClient(config)
    
    success = True
    
    # 测试 evaluate_rule_async
    try:
        rule_draft = {"name": "测试规则", "trigger": {"action": "test"}}
        result = await client.evaluate_rule_async(rule_draft, {})
        print(f"✅ evaluate_rule_async 方法存在并可调用")
    except AttributeError as e:
        print(f"❌ evaluate_rule_async 方法缺失: {e}")
        success = False
    except Exception as e:
        print(f"⚠️ evaluate_rule_async 调用出错: {e}")
    
    # 测试 generate_narrative_async
    try:
        events = [{"type": "test", "description": "测试事件"}]
        result = await client.generate_narrative_async(events)
        print(f"✅ generate_narrative_async 方法存在并可调用")
    except AttributeError as e:
        print(f"❌ generate_narrative_async 方法缺失: {e}")
        success = False
    except Exception as e:
        print(f"⚠️ generate_narrative_async 调用出错: {e}")
    
    # 测试 generate_npc_batch_async
    try:
        npcs = await client.generate_npc_batch_async(2, ["勇敢", "理性"])
        print(f"✅ generate_npc_batch_async 方法存在并可调用")
        if isinstance(npcs, list) and len(npcs) > 0:
            print(f"   生成了 {len(npcs)} 个 NPC")
            for npc in npcs:
                if "name" in npc and "background" in npc:
                    print(f"   - {npc['name']}: {npc['background'][:20]}...")
    except AttributeError as e:
        print(f"❌ generate_npc_batch_async 方法缺失: {e}")
        success = False
    except Exception as e:
        print(f"⚠️ generate_npc_batch_async 调用出错: {e}")
    
    await client.close()
    return success


def test_cli_save_integration():
    """测试 CLI 游戏保存集成"""
    print("\n🧪 测试 CLI 游戏保存集成...")
    
    from src.cli_game import CLIGame
    from src.core.game_state import GameStateManager
    
    # 设置测试环境
    os.environ['PYTEST_RUNNING'] = '1'
    
    cli_game = CLIGame()
    cli_game.game_manager.new_game("test_cli_save")
    
    # 模拟保存操作
    import io
    from unittest import mock
    
    # 测试不带扩展名的保存
    test_input = "test_cli_save\n\n"
    fake_in = io.StringIO(test_input)
    fake_out = io.StringIO()
    with mock.patch("sys.stdin", fake_in), mock.patch("sys.stdout", fake_out):
        cli_game.save_game()
    output_str = fake_out.getvalue()

    
    # 检查保存的文件
    expected_file = cli_game.game_manager.save_dir / "test_cli_save.json"
    if expected_file.exists():
        print("✅ CLI 保存功能正常工作")
        # 检查文件内容
        with open(expected_file, 'r') as f:
            data = json.load(f)
            if "state" in data and "saved_at" in data:
                print("✅ 保存的文件格式正确")
                success = True
            else:
                print("❌ 保存的文件格式不正确")
                success = False
        expected_file.unlink()  # 清理
    else:
        print("❌ CLI 保存失败，文件未创建")
        success = False
    
    return success


def run_pytest_for_fixed_tests():
    """运行修复后的特定测试"""
    print("\n🧪 运行修复后的 pytest 测试...")
    
    import subprocess
    
    # 只运行之前失败的测试
    failed_tests = [
        "tests/cli/test_cli_game.py::TestSetupPhase::test_setup_phase_save_game",
        "tests/cli/test_cli_game.py::TestSaveLoad::test_save_game_success",
        "tests/cli/test_cli_game.py::TestIntegration::test_complete_game_flow",
        "tests/api/test_deepseek_api.py::TestDeepSeekAPI::test_rule_evaluation",
        "tests/api/test_deepseek_api.py::TestDeepSeekAPI::test_narrative_generation",
        "tests/api/test_deepseek_api.py::TestDeepSeekAPI::test_batch_npc_generation",
    ]
    
    # 运行测试
    cmd = ["pytest", "-v", "--tb=short"] + failed_tests
    env = os.environ.copy()
    env["PYTEST_RUNNING"] = "1"
    
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    
    print("\n测试结果:")
    if result.returncode == 0:
        print("✅ 所有修复的测试通过！")
        return True
    else:
        print("❌ 仍有测试失败")
        print("\n失败详情:")
        print(result.stdout)
        if result.stderr:
            print("\n错误信息:")
            print(result.stderr)
        return False


async def main():
    """主函数"""
    print("="*60)
    print("RuleK 修复验证脚本")
    print("="*60)
    
    all_success = True
    
    # 测试文件保存修复
    if not test_file_saving():
        all_success = False
    
    # 测试 API 方法修复
    if not await test_api_methods():
        all_success = False
    
    # 测试 CLI 集成
    if not test_cli_save_integration():
        all_success = False
    
    # 运行 pytest
    print("\n" + "="*60)
    if all_success:
        print("✅ 所有手动测试通过，现在运行 pytest...")
        if run_pytest_for_fixed_tests():
            print("\n🎉 所有修复验证完成！")
        else:
            print("\n⚠️ pytest 仍有失败，请查看上面的错误信息")
            all_success = False
    else:
        print("❌ 有手动测试失败，请先修复这些问题")
    
    return all_success


if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
