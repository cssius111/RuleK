#!/usr/bin/env python3
"""
游戏启动器
直接运行这个文件来启动游戏
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli_game import main

if __name__ == "__main__":
    print("正在启动游戏...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n游戏已退出")
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
