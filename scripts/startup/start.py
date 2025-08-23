#!/usr/bin/env python3
"""
RuleK 项目启动器
统一的项目启动和管理入口
"""
import sys
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """主函数 - 自动选择最佳启动方式"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║           RuleK - 规则怪谈管理者 🎮                        ║
║              一键启动和管理工具                             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        # 直接命令模式
        if command == "web":
            print("🚀 启动Web服务器...")
            import subprocess
            subprocess.run([sys.executable, "rulek.py", "web"])
        elif command == "cli":
            print("🎮 启动CLI游戏...")
            import subprocess
            subprocess.run([sys.executable, "rulek.py", "cli"])
        elif command == "test":
            print("🧪 运行测试...")
            test_script = PROJECT_ROOT / "scripts" / "test" / "quick_api_test.py"
            if test_script.exists():
                import subprocess
                subprocess.run([sys.executable, str(test_script)])
            else:
                print("❌ 测试脚本不存在")
        elif command == "fix":
            print("🔧 运行修复...")
            fix_script = PROJECT_ROOT / "scripts" / "fix" / "fix_api.py"
            if fix_script.exists():
                import subprocess
                subprocess.run([sys.executable, str(fix_script)])
            else:
                print("❌ 修复脚本不存在")
        elif command == "manage":
            print("📋 打开管理中心...")
            manage_script = PROJECT_ROOT / "tools" / "manage.py"
            if manage_script.exists():
                import subprocess
                subprocess.run([sys.executable, str(manage_script)])
            else:
                print("❌ 管理脚本不存在")
        elif command in ["help", "-h", "--help"]:
            print_help()
        else:
            print(f"❌ 未知命令: {command}")
            print_help()
    else:
        # 交互模式 - 默认打开管理中心
        manage_script = PROJECT_ROOT / "tools" / "manage.py"
        if manage_script.exists():
            import subprocess
            subprocess.run([sys.executable, str(manage_script)])
        else:
            # 如果管理脚本不存在，显示简单菜单
            show_simple_menu()


def print_help():
    """打印帮助信息"""
    print("""
使用方法:
    python start.py [command]

可用命令:
    web     - 启动Web服务器
    cli     - 启动CLI游戏
    test    - 运行API测试
    fix     - 诊断和修复问题
    manage  - 打开管理中心（默认）
    help    - 显示此帮助

示例:
    python start.py         # 打开管理中心
    python start.py web     # 直接启动Web服务器
    python start.py test    # 运行测试
    """)


def show_simple_menu():
    """显示简单菜单"""
    print("\n请选择操作:")
    print("1. 启动Web服务器")
    print("2. 启动CLI游戏")
    print("3. 运行测试")
    print("4. 修复问题")
    print("0. 退出")
    
    choice = input("\n请选择 (0-4): ").strip()
    
    import subprocess
    
    if choice == "1":
        subprocess.run([sys.executable, "rulek.py", "web"])
    elif choice == "2":
        subprocess.run([sys.executable, "rulek.py", "cli"])
    elif choice == "3":
        test_script = PROJECT_ROOT / "scripts" / "test" / "quick_api_test.py"
        if test_script.exists():
            subprocess.run([sys.executable, str(test_script)])
    elif choice == "4":
        fix_script = PROJECT_ROOT / "scripts" / "fix" / "fix_api.py"
        if fix_script.exists():
            subprocess.run([sys.executable, str(fix_script)])
    elif choice == "0":
        print("👋 再见!")
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 程序被中断")
        sys.exit(0)
