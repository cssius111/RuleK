#!/usr/bin/env python3
"""RuleK 统一入口程序

统一参数解析和调度，具体功能在 scripts 模块中实现。

Usage:
    python rulek.py              # 显示交互式菜单
    python rulek.py <command>    # 执行指定命令
    python rulek.py help         # 显示帮助信息
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Dict

from src.utils.logger import setup_logging

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


class Colors:
    """终端颜色"""

    CYAN = "\033[0;36m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_banner() -> None:
    """打印项目横幅"""
    print(
        f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════╗
║              🎮 RuleK - 规则怪谈管理者 🎮              ║
║                    统一管理入口 v2.0                     ║
╚══════════════════════════════════════════════════════════╝
{Colors.RESET}"""
    )


def print_menu() -> None:
    """显示交互式菜单"""
    menu_items = [
        ("1", "🎮 启动完整游戏", "前端+后端"),
        ("2", "🔧 启动Web API", "仅后端服务"),
        ("3", "🎨 启动前端界面", "仅前端服务"),
        ("4", "💻 启动CLI游戏", "命令行版本"),
        ("-", "-" * 40, ""),
        ("5", "🧪 运行测试", "完整测试套件"),
        ("6", "🔍 诊断系统", "检查环境和依赖"),
        ("7", "🔧 修复问题", "自动修复常见问题"),
        ("8", "🧹 清理项目", "清理缓存和临时文件"),
        ("-", "-" * 40, ""),
        ("9", "📚 查看文档", "项目文档"),
        ("0", "📊 项目状态", "查看项目信息"),
        ("-", "-" * 40, ""),
        ("h", "❓ 帮助", "命令行帮助"),
        ("q", "👋 退出", "退出程序"),
    ]

    print(f"\n{Colors.BOLD}请选择操作:{Colors.RESET}\n")
    for key, name, desc in menu_items:
        if key == "-":
            print(f"  {name}")
        else:
            print(
                f"  {Colors.CYAN}[{key}]{Colors.RESET} {name:<20} "
                f"{Colors.YELLOW}{desc}{Colors.RESET}"
            )
    print()


def show_help() -> None:
    """显示命令行帮助"""
    print(
        f"""{Colors.BOLD}命令行使用方法:{Colors.RESET}
    python rulek.py [command]

{Colors.BOLD}可用命令:{Colors.RESET}
    {Colors.CYAN}start{Colors.RESET}       - 启动完整游戏（前端+后端）
    {Colors.CYAN}web{Colors.RESET}         - 启动Web API服务器
    {Colors.CYAN}frontend{Colors.RESET}    - 启动前端开发服务器
    {Colors.CYAN}cli{Colors.RESET}         - 启动命令行游戏
    {Colors.CYAN}test{Colors.RESET}        - 运行测试套件
    {Colors.CYAN}diagnose{Colors.RESET}    - 诊断系统问题
    {Colors.CYAN}fix{Colors.RESET}         - 修复常见问题
    {Colors.CYAN}clean{Colors.RESET}       - 清理项目
    {Colors.CYAN}docs{Colors.RESET}        - 查看文档
    {Colors.CYAN}status{Colors.RESET}      - 查看项目状态
    {Colors.CYAN}help{Colors.RESET}        - 显示此帮助
"""
    )


def main() -> None:
    """主函数"""
    logger = setup_logging()
    logger.info("RuleK unified entry started")

    from scripts.startup.start_game import main as start_full_game
    from scripts.startup.start_web_server import main as start_backend
    from scripts.startup.start_frontend import main as start_frontend
    from scripts.startup.start_cli import main as start_cli
    from scripts.test.run_pytest import main as run_tests
    from scripts.diagnostic.system_check import run_diagnostics
    from scripts.fix.fix_issues import main as fix_issues
    from scripts.clean_project import clean as clean_project
    from scripts.show_docs import main as show_docs
    from scripts.status import check_status as show_status

    commands: Dict[str, Callable[[], None]] = {
        "start": start_full_game,
        "web": start_backend,
        "backend": start_backend,
        "frontend": start_frontend,
        "cli": start_cli,
        "test": run_tests,
        "diagnose": run_diagnostics,
        "fix": fix_issues,
        "clean": clean_project,
        "docs": show_docs,
        "status": show_status,
        "help": show_help,
    }

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        action = commands.get(command)
        if action:
            try:
                action()
            except KeyboardInterrupt:
                print(f"\n{Colors.GREEN}👋 再见！{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ 未知命令: {command}{Colors.RESET}")
            show_help()
            sys.exit(1)
        return

    print_banner()
    while True:
        print_menu()
        try:
            choice = input(f"{Colors.CYAN}请选择 > {Colors.RESET}").strip().lower()
            menu_actions: Dict[str, Callable[[], None]] = {
                "1": start_full_game,
                "2": start_backend,
                "3": start_frontend,
                "4": start_cli,
                "5": run_tests,
                "6": run_diagnostics,
                "7": fix_issues,
                "8": clean_project,
                "9": show_docs,
                "0": show_status,
                "h": show_help,
                "q": lambda: sys.exit(0),
            }
            if choice in menu_actions:
                if choice == "q":
                    print(f"{Colors.GREEN}👋 再见！{Colors.RESET}")
                    break
                menu_actions[choice]()
                if choice in {"1", "2", "3", "4"}:
                    break
            else:
                print(f"{Colors.RED}无效选择，请重试{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.GREEN}👋 再见！{Colors.RESET}")
            break


if __name__ == "__main__":
    main()
