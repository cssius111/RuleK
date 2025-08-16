"""
日志工具
提供统一的日志记录功能
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Union

# 创建日志目录
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    # ANSI颜色代码
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        # 根据级别添加emoji
        emoji_map = {
            "DEBUG": "🐛",
            "INFO": "📝",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "💀",
        }

        original_levelname = levelname.strip()
        if original_levelname in emoji_map:
            record.msg = f"{emoji_map[original_levelname]} {record.msg}"

        return super().format(record)


def setup_logger(
    name: str,
    level: Union[str, int] = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
) -> logging.Logger:
    """设置日志器

    Parameters
    ----------
    name : str
        日志器名称
    level : str | int, optional
        日志级别，可以是 ``"INFO"`` 这样的字符串或 ``logging.INFO`` 的整数值。
    log_file : Optional[str], optional
        如果提供则写入指定的日志文件
    console : bool, optional
        是否输出到控制台
    """

    logger = logging.getLogger(name)
    if isinstance(level, int):
        logger.setLevel(level)
    else:
        logger.setLevel(LOG_LEVELS.get(str(level).upper(), logging.INFO))

    # 清除现有处理器
    logger.handlers.clear()

    # 控制台处理器
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        file_path = LOG_DIR / log_file
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """获取日志器（便捷方法）"""
    # 从环境变量或配置文件读取日志级别
    import os

    log_level = os.environ.get("LOG_LEVEL", "INFO")

    # 自动创建日志文件
    today = datetime.now().strftime("%Y%m%d")
    log_file = f"game_{today}.log"

    return setup_logger(name, level=log_level, log_file=log_file)


# 全局日志器
root_logger = get_logger("RuleK")


def log_game_event(event_type: str, **kwargs):
    """记录游戏事件（特殊格式）"""
    event_data = {"type": event_type, "timestamp": datetime.now().isoformat(), **kwargs}

    # 使用特殊格式记录
    root_logger.info(f"[GAME_EVENT] {event_type} | {kwargs}")

    # 同时写入事件日志文件
    event_file = LOG_DIR / "game_events.jsonl"
    with open(event_file, "a", encoding="utf-8") as f:
        import json

        f.write(json.dumps(event_data, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    # 测试日志
    logger = get_logger(__name__)

    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误")

    # 测试游戏事件日志
    log_game_event("rule_created", rule_name="午夜镜子", cost=150)
    log_game_event("npc_death", npc_name="张三", cause="触发规则")
