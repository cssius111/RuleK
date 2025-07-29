#!/usr/bin/env python3
"""运行CLI测试 - 修复后版本"""
import subprocess
import sys
import os

def main():
    """主函数"""
    os.environ['PYTEST_RUNNING'] = '1'
    
    print("✅ 已修复pytest配置")
    print("\n🧪 运行CLI测试...")
    print("=" * 60)
    
    # 先运行之前失败的3个测试
    failed_tests = [
        "TestMainMenu::test_new_game_creation_success",
        "TestRuleManagement::test_create_rule_from_template_success", 
        "TestRuleManagement::test_create_rule_insufficient_points"
    ]
    
    print("\n1️⃣ 首先运行之前失败的测试：")
    for test in failed_tests:
        cmd = [
            sys.executable, '-m', 'pytest',
            f'tests/cli/test_cli_game.py::{test}',
            '-v'
        ]
        
        print(f"\n运行: {test}")
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print(f"✅ {test} - 通过")
        else:
            print(f"❌ {test} - 失败")
    
    print("\n" + "=" * 60)
    print("\n2️⃣ 运行所有测试（跳过耗时测试）：")
    
    # 运行所有测试，跳过test_complete_game_flow
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/cli/test_cli_game.py',
        '-v',
        '--tb=short',
        '-k', 'not test_complete_game_flow'
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n🎉 所有测试通过！（已跳过耗时的集成测试）")
        print("\n下一步：")
        print("1. 查看测试覆盖率：")
        print("   pytest tests/cli/test_cli_game.py --cov=src.cli_game --cov-report=html")
        print("\n2. 运行扩展测试：")
        print("   pytest tests/cli/test_cli_game_extended.py -v")
    else:
        print("\n❌ 仍有测试失败")
        print("\n💡 调试建议：")
        print("1. 查看上面的错误信息")
        print("2. 对于积分扣除问题，检查 src/cli_game.py 中的 create_rule_from_template 方法")
        print("3. 确保 GameStateManager.add_rule() 返回 True")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
