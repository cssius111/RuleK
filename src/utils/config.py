"""Utility module for loading configuration files and environment variables."""
from __future__ import annotations

import ast
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _parse_cors_origins(value: str) -> List[str]:
    """Parse a string of origins into a list.

    The function tries JSON decoding first, then falls back to
    ``ast.literal_eval``. If both methods fail, the string is split by
    commas and stripped of whitespace.
    """
    try:
        data = json.loads(value)
        if isinstance(data, list):
            return [str(item).strip() for item in data]
    except Exception as exc:
        logger.debug("Failed to parse CORS origins as JSON: %s", exc)

    try:
        data = ast.literal_eval(value)
        if isinstance(data, list):
            return [str(item).strip() for item in data]
    except Exception as exc:
        logger.debug("Failed to parse CORS origins via ast.literal_eval: %s", exc)

    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    """Configuration loader for project-wide settings."""

    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[2]
        self._config: Dict[str, Any] = {}
        self._load_env()
        self._load_config_files()

    # ------------------------------------------------------------------
    def _load_env(self) -> None:
        """Load variables from a ``.env`` file if python-dotenv is available."""
        try:
            from dotenv import find_dotenv, load_dotenv
        except Exception:  # pragma: no cover - optional dependency
            logger.warning("python-dotenv not installed, skipping .env loading")
            return

        search_path = self.project_root / ".env"
        dotenv_path = find_dotenv(str(search_path), usecwd=False)
        if dotenv_path and Path(dotenv_path).exists():
            load_dotenv(dotenv_path)
            logger.info("Loaded environment variables from %s", dotenv_path)
        else:
            logger.debug(".env file not found at %s", search_path)

    # ------------------------------------------------------------------
    def _expand_env(self, data: Any) -> Any:
        """Recursively expand environment variables in a data structure."""
        if isinstance(data, dict):
            return {k: self._expand_env(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._expand_env(v) for v in data]
        if isinstance(data, str):
            return os.path.expandvars(data)
        return data

    # ------------------------------------------------------------------
    def _load_config_files(self) -> None:
        """Load ``config.json`` from the project root."""
        config_dir = self.project_root / "config"
        main_cfg = config_dir / "config.json"
        if main_cfg.exists():
            try:
                with open(main_cfg, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                self._config.update(self._expand_env(data))
            except Exception as exc:  # pragma: no cover - file reading errors
                logger.error("Failed to load %s: %s", main_cfg, exc)

    # ------------------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value."""
        env_val = os.environ.get(key)
        if env_val is not None:
            return env_val
        return self._config.get(key, default)

    # ------------------------------------------------------------------
    def get_deepseek_config(self) -> Dict[str, Any]:
        """Return DeepSeek API configuration settings."""
        api_cfg = self._config.get("api", {})
        return {
            "api_key": self.get("DEEPSEEK_API_KEY", api_cfg.get("deepseek_api_key", "")),
            "endpoint": self.get(
                "DEEPSEEK_BASE_URL", api_cfg.get("deepseek_endpoint", "https://api.deepseek.com/v1")
            ),
            "model": self.get("DEEPSEEK_MODEL", api_cfg.get("model", "deepseek-chat")),
            "max_retries": int(self.get("DEEPSEEK_MAX_RETRIES", api_cfg.get("max_retries", 3))),
            "timeout": int(self.get("DEEPSEEK_TIMEOUT", api_cfg.get("timeout", 30))),
            "cache_ttl": int(self.get("DEEPSEEK_CACHE_TTL", api_cfg.get("cache_ttl", 300))),
        }

    # ------------------------------------------------------------------
    def is_test_mode(self) -> bool:
        return str(self.get("TEST_MODE", "false")).lower() == "true"

    def is_debug_mode(self) -> bool:
        return str(self.get("GAME_DEBUG", "false")).lower() == "true"

    def get_log_level(self) -> str:
        return str(self.get("GAME_LOG_LEVEL", "INFO"))

    def get_web_config(self) -> Dict[str, Any]:
        """Return Web server configuration settings."""
        web_cfg = self._config.get("web", {})
        origins = self.get(
            "WEB_CORS_ORIGINS",
            json.dumps(web_cfg.get("cors_origins", ["http://localhost:3000"])),
        )
        return {
            "host": self.get("WEB_HOST", web_cfg.get("host", "0.0.0.0")),
            "port": int(self.get("WEB_PORT", web_cfg.get("port", 8000))),
            "cors_origins": _parse_cors_origins(origins),
        }


# ---------------------------------------------------------------------------
# Global helpers
config = Config()


def load_config(path: str | None = None) -> Config:
    """Load an extra JSON configuration file into the global ``config`` object."""
    if path:
        cfg_path = Path(path)
        if cfg_path.exists():
            try:
                with open(cfg_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    config._config.update(data)
                    logger.info("Loaded custom config from %s", path)
                else:
                    logger.warning(
                        "Config file %s does not contain a JSON object", path
                    )
            except Exception as exc:  # pragma: no cover - file reading errors
                logger.error("Failed to load custom config: %s", exc)
        else:
            logger.error("Config file not found: %s", path)
    return config


def get_deepseek_config() -> Dict[str, Any]:
    return config.get_deepseek_config()


def get_web_config() -> Dict[str, Any]:
    return config.get_web_config()


def is_test_mode() -> bool:
    return config.is_test_mode()


def is_debug_mode() -> bool:
    return config.is_debug_mode()


__all__ = [
    "Config",
    "config",
    "load_config",
    "get_deepseek_config",
    "get_web_config",
    "is_test_mode",
    "is_debug_mode",
]
