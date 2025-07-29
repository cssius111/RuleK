#!/usr/bin/env python3
"""立即修复并运行测试"""
import subprocess
import sys
import os
from pathlib import Path

# 清理缓存
print("🧹 清理缓存...")
subprocess.run([sys.executable, '-c', '''
import shutil
from pathlib import Path
for p in Path(".").rglob("__pycache__"): 
    shutil.rmtree(p, ignore_errors=True)
if Path(".pytest_cache").exists():
    shutil.rmtree(".pytest_cache", ignore_errors=True)
print("✓ 缓存已清理")
'''])

# 设置环境
os.environ['PYTEST_RUNNING'] = '1'

# 先运行final_fix_cli.py
print("\n🔧 运行修复脚本...")
result = subprocess.run([sys.executable, "final_fix_cli.py"])

if result.returncode != 0:
    print("\n❌ 修复脚本执行失败")
    sys.exit(1)

print("\n✅ 修复完成，测试结果见上")
