#!/usr/bin/env python3
"""调试特定的失败测试"""
import subprocess
import sys
import os
from pathlib import Path

def debug_test(test_name, description):
    """调试单个测试"""
    print(f"\n🔍 调试: {description}")
    print("=" * 60)
    
    cmd = [
        sys.executable, '-m', 'pytest',
        f'tests/cli/test_cli_game.py::{test_name}',
        '-vvs',
        '--tb=long',
        '--capture=no'  # 显示所有print输出
    ]
    
    result = subprocess.run(cmd)
    print("\n" + "=" * 60)
    return result.returncode == 0

def main():
    """主函数"""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    os.environ['PYTEST_RUNNING'] = '1'
    
    print("🐛 调试失败的CLI测试...")
    print("=" * 60)
    
    # 失败的测试
    tests = [
        ("TestMainMenu::test_new_game_creation_success", "新游戏创建测试"),
        ("TestRuleManagement::test_create_rule_from_template_success", "模板创建规则测试"),
        ("TestRuleManagement::test_create_rule_insufficient_points", "积分不足测试")
    ]
    
    passed = 0
    failed = 0
    
    for test_name, description in tests:
        if debug_test(test_name, description):
            passed += 1
            print(f"✅ {description} - 通过")
        else:
            failed += 1
            print(f"❌ {description} - 失败")
    
    print("\n📊 总结：")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    
    if failed > 0:
        print("\n💡 修复建议：")
        print("1. 查看上面的详细错误输出")
        print("2. 运行: python auto_fix_cli_tests.py")
        print("3. 如果自动修复无效，手动检查：")
        print("   - GameManager.add_rule() 的返回值")
        print("   - spend_fear_points() 的调用时机")
        print("   - Mock对象的设置是否正确")

if __name__ == "__main__":
    main()
