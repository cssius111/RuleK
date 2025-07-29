#!/usr/bin/env python3
"""清理缓存并运行测试"""
import subprocess
import sys
import os
import shutil
from pathlib import Path

# 清理所有缓存
print("🧹 清理缓存...")
for pattern in [".pytest_cache", "__pycache__", "**/__pycache__"]:
    if "*" in pattern:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
    else:
        path = Path(pattern)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)

print("✅ 缓存已清理")

# 设置环境
os.environ['PYTEST_RUNNING'] = '1'

# 运行测试
print("\n🧪 运行CLI测试...")
cmd = [sys.executable, '-m', 'pytest', 'tests/cli/test_cli_game.py', '-v', '-x']
result = subprocess.run(cmd)

if result.returncode == 0:
    print("\n✅ 所有测试通过！")
else:
    print("\n❌ 测试失败，查看上面的错误信息")

sys.exit(result.returncode)
