#!/usr/bin/env python3
"""
RuleK 统一入口
Usage:
    python rulek.py         # 显示帮助
    python rulek.py web     # 启动Web服务器
    python rulek.py cli     # 启动CLI游戏
    python rulek.py test    # 运行测试
    python rulek.py manage  # 项目管理
"""
import sys
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def print_banner():
    """打印横幅"""
    print("""
╔══════════════════════════════════════════════════╗
║           RuleK - 规则怪谈管理者                ║
╚══════════════════════════════════════════════════╝
    """)

def show_help():
    """显示帮助信息"""
    print("""
使用方法:
    python rulek.py <command>

可用命令:
    web     - 启动Web服务器 (http://localhost:8000)
    cli     - 启动命令行游戏
    test    - 运行测试套件
    manage  - 项目管理工具
    help    - 显示此帮助信息

示例:
    python rulek.py web     # 启动Web服务器
    python rulek.py manage  # 打开管理菜单
    """)

def start_web():
    """启动Web服务器"""
    print_banner()
    print("🚀 启动Web服务器...")
    print("   地址: http://localhost:8000")
    print("   文档: http://localhost:8000/docs")
    print("   按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 确保在项目根目录
    import os
    os.chdir(PROJECT_ROOT)
    
    try:
        import uvicorn
        uvicorn.run(
            "web.backend.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ 错误: uvicorn 未安装")
        print("   请运行: pip install uvicorn fastapi")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n✅ 服务器已停止")

def start_cli():
    """启动CLI游戏"""
    print_banner()
    print("🎮 启动命令行游戏...")
    print("-" * 50)
    
    try:
        from src.cli_game import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"❌ 无法启动CLI游戏: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 游戏已退出")

def run_tests():
    """运行测试"""
    print_banner()
    print("🧪 运行测试套件...")
    print("-" * 50)
    
    try:
        import pytest
        pytest.main(["-v", "tests/"])
    except ImportError:
        print("❌ pytest 未安装")
        print("   请运行: pip install pytest")
        sys.exit(1)

def manage_project():
    """打开项目管理工具"""
    subprocess.run([sys.executable, "tools/manage.py"])

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_banner()
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        "web": start_web,
        "cli": start_cli,
        "test": run_tests,
        "manage": manage_project,
        "help": lambda: (print_banner(), show_help()),
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ 未知命令: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
