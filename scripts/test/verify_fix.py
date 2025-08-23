#!/usr/bin/env python
"""
测试修复脚本 - 重新运行测试并验证修复
"""
import subprocess
import sys

def run_tests():
    """运行测试并跳过有问题的测试"""
    print("🔧 运行测试修复验证...")
    print("=" * 60)
    
    # 跳过Playwright测试，因为它们需要运行的Web服务器
    # 只运行CLI测试来验证修复
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--ignore=tests/web/test_game_full_flow.py",  # 跳过Playwright测试
        "-k", "test_ai_create_rule_success",  # 只运行我们修复的测试
        "--tb=short"
    ]
    
    print(f"执行命令: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode

def main():
    """主函数"""
    print("\n🚀 RuleK 测试修复验证")
    print("=" * 60)
    print("已修复的问题:")
    print("1. ✅ CLI测试中AI创建规则时恐惧积分未正确扣除")
    print("2. ⏭️  跳过Playwright测试（需要运行的Web服务器）")
    print("=" * 60)
    
    exit_code = run_tests()
    
    if exit_code == 0:
        print("\n✅ 测试修复成功！")
        print("修复的测试现在可以正常通过。")
    else:
        print("\n❌ 测试仍有问题，请检查输出。")
        sys.exit(1)

if __name__ == "__main__":
    main()
