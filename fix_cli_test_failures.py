#!/usr/bin/env python3
"""修复CLI测试失败的问题"""
import subprocess
import sys
import os
from pathlib import Path

def run_single_test(test_name):
    """运行单个测试查看详细错误"""
    print(f"\n🔍 运行测试: {test_name}")
    print("-" * 60)
    
    cmd = [
        sys.executable, '-m', 'pytest',
        f'tests/cli/test_cli_game.py::{test_name}',
        '-vvs',
        '--tb=short'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ 测试失败")
        print("\n错误输出：")
        print(result.stdout)
        if result.stderr:
            print("\nStderr:")
            print(result.stderr)
    else:
        print("✅ 测试通过")
    
    return result.returncode

def main():
    """主函数"""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    os.environ['PYTEST_RUNNING'] = '1'
    
    print("🔧 分析失败的CLI测试...")
    print("=" * 60)
    
    # 失败的测试
    failed_tests = [
        "TestMainMenu::test_new_game_creation_success",
        "TestRuleManagement::test_create_rule_from_template_success",
        "TestRuleManagement::test_create_rule_insufficient_points"
    ]
    
    print(f"\n发现 {len(failed_tests)} 个失败的测试")
    
    # 运行每个失败的测试查看详细信息
    for test in failed_tests:
        run_single_test(test)
        print("\n" + "=" * 60)
    
    # 提供修复建议
    print("\n💡 可能的问题和修复建议：")
    print("\n1. test_new_game_creation_success:")
    print("   - 可能是AI初始化导致的延迟")
    print("   - 检查 game_loop 的 mock 是否正确")
    
    print("\n2. test_create_rule_from_template_success:")
    print("   - 可能是规则创建后没有正确添加到 active_rules")
    print("   - 检查 add_rule 方法的返回值")
    
    print("\n3. test_create_rule_insufficient_points:")
    print("   - 可能是错误消息文本不匹配")
    print("   - 检查实际的错误提示文本")
    
    print("\n📝 下一步：")
    print("1. 查看上面的详细错误信息")
    print("2. 运行: python auto_fix_cli_tests.py")
    print("3. 或手动修复具体问题")

if __name__ == "__main__":
    main()
