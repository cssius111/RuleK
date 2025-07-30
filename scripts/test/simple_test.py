#!/usr/bin/env python3
"""直接运行CLI测试（无任何修改）"""
import subprocess
import sys
import os

os.environ['PYTEST_RUNNING'] = '1'

# 最简单的测试命令
cmd = [
    sys.executable, '-m', 'pytest',
    'tests/cli/test_cli_game.py',
    '-v',
    '--tb=short',
    '-x',  # 在第一个错误时停止
]

print("🧪 直接运行CLI测试...")
print("=" * 60)
print(f"命令: {' '.join(cmd)}")
print("-" * 60)

result = subprocess.run(cmd)

if result.returncode == 0:
    print("\n✅ 所有测试通过！")
else:
    print("\n❌ 测试失败")
    print("\n💡 如果看到 'timeout' marker 错误，运行：")
    print("   python fix_timeout_marker.py")

sys.exit(result.returncode)
