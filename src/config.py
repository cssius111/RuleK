"""Compatibility configuration helpers used throughout the project."""
from __future__ import annotations

from typing import Any, Dict, Optional

from src.utils.config import config as global_config


class APIConfig:
    """Simple container for DeepSeek API settings."""

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None) -> None:
        if config_dict is None:
            ds = global_config.get_deepseek_config()
            self.deepseek_api_key = ds["api_key"]
            self.base_url = ds["base_url"]
            self.model = ds["model"]
            self.timeout = global_config.get("api", {}).get("timeout", 30)
            self.max_retries = global_config.get("api", {}).get(
                "max_retries", 3
            )
        else:
            self.deepseek_api_key = config_dict.get("deepseek_api_key", "")
            self.base_url = config_dict.get(
                "base_url", "https://api.deepseek.com/v1"
            )
            self.model = config_dict.get("model", "deepseek-chat")
            self.timeout = config_dict.get("timeout", 30)
            self.max_retries = config_dict.get("max_retries", 3)


class Config:
    """Wrapper around :mod:`src.utils.config` for backward compatibility."""

    def __init__(self) -> None:
        self._config = global_config._config
        self.api = APIConfig()

    def get(self, key: str, default: Any = None) -> Any:
        return global_config.get(key, default)

    def get_deepseek_config(self) -> Dict[str, str]:
        return global_config.get_deepseek_config()

    def is_test_mode(self) -> bool:
        return global_config.is_test_mode()

    def is_debug_mode(self) -> bool:
        return global_config.is_debug_mode()

    def get_log_level(self) -> str:
        return global_config.get_log_level()

    def get_web_config(self) -> Dict[str, Any]:
        return global_config.get_web_config()


config = Config()

__all__ = ["APIConfig", "Config", "config"]
