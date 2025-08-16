#!/usr/bin/env python3
"""快速访问管理工具"""
import subprocess
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent.parent
manage_tool = project_root / "tools" / "manage.py"

if manage_tool.exists():
    subprocess.run([sys.executable, str(manage_tool)])
else:
    print(f"❌ 找不到管理工具: {manage_tool}")
    sys.exit(1)
