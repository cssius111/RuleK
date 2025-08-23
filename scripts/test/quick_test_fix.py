#!/usr/bin/env python
"""
快速测试 - 验证恐惧积分扣除修复
"""
import subprocess
import sys
import os

def run_specific_test():
    """运行特定的修复测试"""
    print("\n🧪 运行恐惧积分扣除测试...")
    print("=" * 60)
    
    # 设置环境变量，表示在测试中运行
    env = os.environ.copy()
    env['PYTEST_RUNNING'] = '1'
    
    cmd = [
        sys.executable,
        "-m", "pytest",
        "tests/cli/test_cli_game.py::TestAIRuleCreation::test_ai_create_rule_success",
        "-v",
        "--tb=short"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0

def main():
    print("=" * 60)
    print("🔧 RuleK 测试修复验证")
    print("=" * 60)
    print("\n📝 修复内容:")
    print("1. 删除了 game_state.py 中的重复方法定义")
    print("2. 修复了 create_rule 方法的恐惧积分扣除逻辑")
    print("3. 确保 AI 创建规则时正确扣除成本")
    print("=" * 60)
    
    if run_specific_test():
        print("\n" + "=" * 60)
        print("✅ 测试通过！修复成功！")
        print("=" * 60)
        print("\n📊 修复总结:")
        print("- 问题: AI创建规则时恐惧积分未正确扣除")
        print("- 原因: create_rule 方法被重复定义，第二个定义缺少扣除逻辑")
        print("- 解决: 删除重复定义，修复扣除逻辑")
        print("\n💡 下一步:")
        print("- 运行完整测试套件: pytest tests/")
        print("- 检查 Playwright 测试环境")
        return 0
    else:
        print("\n❌ 测试失败，请检查修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
