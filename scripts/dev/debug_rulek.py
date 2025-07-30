#!/usr/bin/env python3
"""
RuleK 一键调试脚本
快速诊断和修复常见问题
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 RuleK 一键调试工具")
    print("=" * 50)
    
    # 确保在项目根目录
    project_root = Path.cwd()
    if not (project_root / "rulek.py").exists():
        print("❌ 请在RuleK项目根目录运行此脚本！")
        return
        
    print("\n选择操作:")
    print("1. 🔍 智能诊断（推荐）")
    print("2. 🎮 快速启动游戏")
    
    choice = input("\n请选择 (1-2): ").strip()
    
    if choice == "1":
        print("\n运行智能诊断...")
        subprocess.run([sys.executable, "smart_debug.py"])
        
    elif choice == "2":
        print("\n启动游戏...")
        # 先快速检查
        check_basic_requirements()
        # 启动游戏
        subprocess.run([sys.executable, "rulek.py", "cli"])
        
    else:
        print("无效选择")
        
def check_basic_requirements():
    """快速检查基本要求"""
    print("\n快速检查...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("⚠️  Python版本过低，建议升级到3.8+")
        
    # 检查关键文件
    required_files = [
        "src/__init__.py",
        "src/cli_game.py",
        "config/config.json"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            
    if missing:
        print(f"⚠️  缺少文件: {', '.join(missing)}")
    else:
        print("✅ 基本检查通过")

if __name__ == "__main__":
    main()
