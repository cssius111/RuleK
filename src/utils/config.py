"""Utility module for loading configuration files and environment variables."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class Config:
    """Configuration loader."""

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
    def _load_config_files(self) -> None:
        """Load ``config.json`` and ``deepseek_config.json`` from the project."""
        config_dir = self.project_root / "config"

        main_cfg = config_dir / "config.json"
        if main_cfg.exists():
            try:
                with open(main_cfg, "r", encoding="utf-8") as fh:
                    self._config.update(json.load(fh))
            except Exception as exc:  # pragma: no cover - file reading errors
                logger.error("Failed to load %s: %s", main_cfg, exc)

        deepseek_cfg = config_dir / "deepseek_config.json"
        if deepseek_cfg.exists():
            try:
                with open(deepseek_cfg, "r", encoding="utf-8") as fh:
                    self._config["deepseek"] = json.load(fh)
            except Exception as exc:  # pragma: no cover - file reading errors
                logger.error("Failed to load %s: %s", deepseek_cfg, exc)

    # ------------------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value."""
        env_val = os.environ.get(key)
        if env_val is not None:
            return env_val
        return self._config.get(key, default)

    # ------------------------------------------------------------------
    def get_deepseek_config(self) -> Dict[str, str]:
        """Return DeepSeek API configuration settings."""
        ds_cfg = self._config.get("deepseek", {})
        return {
            "api_key": self.get("DEEPSEEK_API_KEY", ds_cfg.get("api_key", "")),
            "base_url": self.get(
                "DEEPSEEK_BASE_URL",
                ds_cfg.get("base_url", "https://api.deepseek.com/v1"),
            ),
            "model": self.get("DEEPSEEK_MODEL", ds_cfg.get("model", "deepseek-chat")),
        }

    # ------------------------------------------------------------------
    def is_test_mode(self) -> bool:
        return str(self.get("TEST_MODE", "false")).lower() == "true"

    def is_debug_mode(self) -> bool:
        return str(self.get("GAME_DEBUG", "false")).lower() == "true"

    def get_log_level(self) -> str:
        return str(self.get("GAME_LOG_LEVEL", "INFO"))

    def get_web_config(self) -> Dict[str, Any]:
        return {
            "host": self.get("WEB_HOST", "0.0.0.0"),
            "port": int(self.get("WEB_PORT", 8000)),
            "cors_origins": eval(
                self.get("WEB_CORS_ORIGINS", '["http://localhost:3000"]')
            ),
        }

    # ------------------------------------------------------------------
    def save_deepseek_config(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ) -> bool:
        """Persist DeepSeek configuration to ``deepseek_config.json``."""
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        path = config_dir / "deepseek_config.json"
        data = {
            "api_key": api_key,
            "base_url": base_url or "https://api.deepseek.com/v1",
            "model": model or "deepseek-chat",
        }
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            self._config["deepseek"] = data
            logger.info("DeepSeek configuration saved to %s", path)
            return True
        except Exception as exc:  # pragma: no cover - file writing errors
            logger.error("Failed to save deepseek config: %s", exc)
            return False


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
                    logger.warning("Config file %s does not contain a JSON object", path)
            except Exception as exc:  # pragma: no cover - file reading errors
                logger.error("Failed to load custom config: %s", exc)
        else:
            logger.error("Config file not found: %s", path)
    return config


def get_deepseek_config() -> Dict[str, str]:
    return config.get_deepseek_config()


def is_test_mode() -> bool:
    return config.is_test_mode()


def is_debug_mode() -> bool:
    return config.is_debug_mode()


__all__ = [
    "Config",
    "config",
    "load_config",
    "get_deepseek_config",
    "is_test_mode",
    "is_debug_mode",
]
