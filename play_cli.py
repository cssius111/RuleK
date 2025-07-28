#!/usr/bin/env python3
"""
RuleK CLI 游戏启动器
正确设置Python路径
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 运行CLI游戏
if __name__ == "__main__":
    from src.cli_game import main
    import asyncio
    
    print("🎮 启动规则怪谈管理者...")
    asyncio.run(main())
