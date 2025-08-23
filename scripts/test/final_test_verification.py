#!/usr/bin/env python
"""
RuleK 测试修复最终验证
运行所有测试并报告结果
"""
import subprocess
import sys
import os

def run_all_tests():
    """运行所有测试"""
    print("\n🧪 运行完整测试套件...")
    print("=" * 60)
    
    env = os.environ.copy()
    env['PYTEST_RUNNING'] = '1'
    
    cmd = [
        sys.executable,
        "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-q"  # 简洁输出
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    
    # 解析输出
    output = result.stdout
    
    # 提取关键信息
    lines = output.split('\n')
    for line in lines:
        if 'passed' in line or 'failed' in line or 'skipped' in line:
            print(line)
    
    return result.returncode == 0

def main():
    print("=" * 60)
    print("🔧 RuleK 测试修复最终验证")
    print("=" * 60)
    print("\n📝 已修复的问题:")
    print("1. ✅ CLI测试 - AI创建规则时恐惧积分扣除")
    print("2. ✅ Playwright测试 - event_loop fixture 问题")
    print("=" * 60)
    
    success = run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试套件运行成功！")
    else:
        print("⚠️ 部分测试可能失败，请查看详细输出")
    print("=" * 60)
    
    print("\n📊 修复总结:")
    print("- 删除了 game_state.py 中的重复方法定义")
    print("- 修复了 create_rule 方法的积分扣除逻辑")
    print("- 添加了 event_loop fixture 解决 pytest-asyncio 问题")
    
    print("\n💡 如果还有测试失败:")
    print("1. 检查是否所有服务都在运行（前端/后端）")
    print("2. 检查环境依赖是否安装完整")
    print("3. 查看 docs/dev/TEST_FIX_REPORT_V2.md 了解详情")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
