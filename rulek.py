#!/usr/bin/env python
"""
规则怪谈管理者 - 统一游戏入口
支持多种运行模式：CLI、Demo、测试等
"""
import sys
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from src.utils.config import config, load_config


def run_cli_game():
    """运行CLI版本的游戏"""
    from src.cli_game import main as cli_main
    cli_main()


def run_demo_game():
    """运行演示版本（已集成到 CLI）"""
    print("Demo 模式已合并到 CLI，直接启动 CLI 版本")
    run_cli_game()


def run_web_server():
    """启动Web服务器"""
    import subprocess
    import os
    
    # 切换到backend目录
    backend_dir = project_root / "web" / "backend"
    if backend_dir.exists():
        os.chdir(backend_dir)
        subprocess.run([sys.executable, "run_server.py"])
    else:
        print("Web后端目录不存在，请先运行 Sprint 3 初始化")
        sys.exit(1)


def run_tests(test_type="all"):
    """运行测试"""
    import pytest
    
    test_args = ["-v"]
    
    if test_type == "unit":
        test_args.append("tests/unit/")
    elif test_type == "integration":
        test_args.append("tests/integration/")
    elif test_type == "api":
        test_args.append("tests/api/")
    else:
        test_args.append("tests/")
    
    # 运行pytest
    exit_code = pytest.main(test_args)
    sys.exit(exit_code)


def verify_environment():
    """验证环境配置"""
    from scripts.verify_env import main as verify_main
    verify_main()


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="规则怪谈管理者 - 统一游戏入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
运行模式说明:
  cli         - 运行命令行版本游戏（默认）
  demo        - 运行Sprint 2功能演示
  web         - 启动Web服务器
  test        - 运行测试套件
  verify      - 验证环境配置
  
示例:
  python rulek.py              # 运行CLI游戏
  python rulek.py demo         # 运行演示
  python rulek.py web          # 启动Web服务器
  python rulek.py test unit    # 只运行单元测试
  python rulek.py verify       # 验证环境
        """
    )
    
    parser.add_argument(
        "mode",
        nargs="?",
        default="cli",
        choices=["cli", "demo", "web", "test", "verify"],
        help="运行模式"
    )
    
    parser.add_argument(
        "subcommand",
        nargs="?",
        help="子命令（例如test模式下的unit/integration/api）"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="指定配置文件路径"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别（支持传入 logging.INFO 或 "INFO" 等值）
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger("main", level=log_level)
    
    # 加载配置
    if args.config:
        config = load_config(args.config)
    else:
        config = load_config()
    
    logger.info(f"启动规则怪谈管理者 - 模式: {args.mode}")
    
    # 根据模式执行不同的功能
    try:
        if args.mode == "cli":
            run_cli_game()
        elif args.mode == "demo":
            run_demo_game()
        elif args.mode == "web":
            run_web_server()
        elif args.mode == "test":
            test_type = args.subcommand or "all"
            run_tests(test_type)
        elif args.mode == "verify":
            verify_environment()
        else:
            logger.error(f"未知的运行模式: {args.mode}")
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
