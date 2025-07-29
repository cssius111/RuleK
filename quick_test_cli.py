#!/usr/bin/env python3
"""快速运行CLI测试并显示结果"""
import subprocess
import sys
import os
from pathlib import Path

def run_cli_tests():
    """运行CLI测试"""
    # 设置环境
    os.environ['PYTEST_RUNNING'] = '1'
    project_root = Path(__file__).parent
    
    # 构建命令
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/cli/test_cli_game.py',
        '-v',
        '--tb=short',
        '--no-header',
        '-q'
    ]
    
    print("🧪 运行 CLI 测试...")
    print("=" * 60)
    
    # 运行测试
    result = subprocess.run(cmd, cwd=project_root)
    
    print("\n" + "=" * 60)
    
    if result.returncode == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 有测试失败")
        print("\n💡 提示：")
        print("1. 运行 python fix_cli_test_env.py 修复环境")
        print("2. 查看具体错误信息并修复代码")
        print("3. 重新运行测试")
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_cli_tests()
    sys.exit(exit_code)
