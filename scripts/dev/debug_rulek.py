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
    print("2. 🔧 自动修复测试")
    print("3. 🤖 优化AI功能")
    print("4. 🎮 快速启动游戏")
    print("5. 📊 运行所有检查")
    
    choice = input("\n请选择 (1-5): ").strip()
    
    if choice == "1":
        print("\n运行智能诊断...")
        subprocess.run([sys.executable, "smart_debug.py"])
        
    elif choice == "2":
        print("\n运行自动测试修复...")
        subprocess.run([sys.executable, "auto_test_fix.py"])
        
    elif choice == "3":
        print("\n优化AI功能...")
        subprocess.run([sys.executable, "optimize_ai.py"])
        
    elif choice == "4":
        print("\n启动游戏...")
        # 先快速检查
        check_basic_requirements()
        # 启动游戏
        subprocess.run([sys.executable, "rulek.py", "cli"])
        
    elif choice == "5":
        print("\n运行完整检查...")
        # 依次运行所有检查
        print("\n[1/3] 智能诊断...")
        subprocess.run([sys.executable, "smart_debug.py"])
        
        print("\n[2/3] 测试修复...")
        subprocess.run([sys.executable, "auto_test_fix.py"])
        
        print("\n[3/3] AI优化...")
        subprocess.run([sys.executable, "optimize_ai.py"])
        
        print("\n✅ 所有检查完成！")
        print("\n查看生成的报告:")
        print("- debug_report.md")
        print("- test_fix_report.md")
        print("- ai_optimization_report.md")
        
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
