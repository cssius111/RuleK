"""启动命令行版游戏"""
from __future__ import annotations

import asyncio

from src.cli_game import main as cli_main


def main() -> None:
    """运行CLI游戏"""
    asyncio.run(cli_main())


if __name__ == "__main__":
    main()
