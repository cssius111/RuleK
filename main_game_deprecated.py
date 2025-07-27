#!/usr/bin/env python
"""
[DEPRECATED] 这个文件已被弃用，请使用 rulek.py 作为统一入口

运行游戏：
  python rulek.py          # 运行CLI游戏
  python rulek.py demo     # 运行演示
  python rulek.py web      # 启动Web服务器
"""
import warnings
warnings.warn(
    "main_game.py 已被弃用，请使用 'python rulek.py' 启动游戏",
    DeprecationWarning,
    stacklevel=2
)

import subprocess
import sys

# 重定向到新的入口
subprocess.run([sys.executable, "rulek.py"] + sys.argv[1:])
