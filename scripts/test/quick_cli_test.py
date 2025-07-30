#!/usr/bin/env python3
"""快速运行CLI测试（跳过耗时测试）"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    """主函数"""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    os.environ['PYTEST_RUNNING'] = '1'
    
    print("🚀 快速运行CLI测试（跳过耗时测试）...")
    print("=" * 60)
    
    # 运行测试，但排除耗时的集成测试
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/cli/test_cli_game.py',
        '-v',
        '--tb=short',
        '-k', 'not test_complete_game_flow',  # 排除耗时测试
        '--no-header'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    print("\n" + "-" * 60)
    
    result = subprocess.run(cmd)
    
    print("-" * 60)
    
    if result.returncode == 0:
        print("\n✅ 所有测试通过！（已跳过耗时的集成测试）")
        print("\n💡 如需运行完整测试（包括集成测试），使用：")
        print("   pytest tests/cli/test_cli_game.py -v")
    else:
        print("\n❌ 有测试失败")
        print("\n建议：")
        print("1. 运行: python fix_cli_test_failures.py  # 查看详细错误")
        print("2. 运行: python auto_fix_cli_tests.py     # 自动修复")
    
    # 显示失败的测试列表
    if result.returncode != 0:
        print("\n🔍 运行失败的测试查看详细信息：")
        failed_tests = [
            "TestMainMenu::test_new_game_creation_success",
            "TestRuleManagement::test_create_rule_from_template_success",
            "TestRuleManagement::test_create_rule_insufficient_points"
        ]
        
        for test in failed_tests:
            print(f"\npytest tests/cli/test_cli_game.py::{test} -vvs")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
