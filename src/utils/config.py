"""
配置加载工具
用于加载环境变量和配置文件
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """配置管理类"""
    
    def __init__(self):
        # 获取项目根目录，确保无论工作目录如何变化都能正确定位
        self.project_root = Path(__file__).resolve().parents[2]
        self._config = {}
        self._load_env()
        self._load_config_files()
    
    def _load_env(self):
        """加载环境变量"""
        from dotenv import find_dotenv, load_dotenv

        # 使用绝对路径查找 .env，兼容不同工作目录
        search_path = self.project_root / ".env"
        dotenv_path = find_dotenv(str(search_path), usecwd=False)

        if dotenv_path and Path(dotenv_path).exists():
            load_dotenv(dotenv_path)
            logger.info(f"环境变量加载成功: {dotenv_path}")
        else:
            logger.warning("未找到.env文件，使用默认配置")
    
    def _load_config_files(self):
        """加载配置文件"""
        config_dir = self.project_root / "config"
        
        # 加载主配置文件
        main_config = config_dir / "config.json"
        if main_config.exists():
            try:
                with open(main_config, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._config.update(data)
            except Exception as e:
                logger.error(f"加载config.json失败: {e}")
        
        # 加载DeepSeek配置（如果存在）
        deepseek_config = config_dir / "deepseek_config.json"
        if deepseek_config.exists():
            try:
                with open(deepseek_config, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._config['deepseek'] = data
            except Exception as e:
                logger.error(f"加载deepseek_config.json失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        # 先检查环境变量
        env_value = os.environ.get(key)
        if env_value is not None:
            return env_value
        
        # 再检查配置字典
        return self._config.get(key, default)
    
    def get_deepseek_config(self) -> Dict[str, str]:
        """获取DeepSeek API配置"""
        return {
            "api_key": self.get("DEEPSEEK_API_KEY", ""),
            "base_url": self.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            "model": self.get("DEEPSEEK_MODEL", "deepseek-chat")
        }
    
    def is_test_mode(self) -> bool:
        """是否处于测试模式"""
        return self.get("TEST_MODE", "false").lower() == "true"
    
    def is_debug_mode(self) -> bool:
        """是否处于调试模式"""
        return self.get("GAME_DEBUG", "false").lower() == "true"
    
    def get_log_level(self) -> str:
        """获取日志级别"""
        return self.get("GAME_LOG_LEVEL", "INFO")
    
    def get_web_config(self) -> Dict[str, Any]:
        """获取Web配置"""
        return {
            "host": self.get("WEB_HOST", "0.0.0.0"),
            "port": int(self.get("WEB_PORT", 8000)),
            "cors_origins": eval(self.get("WEB_CORS_ORIGINS", '["http://localhost:3000"]'))
        }
    
    def save_deepseek_config(self, api_key: str, base_url: Optional[str] = None, model: Optional[str] = None):
        """保存DeepSeek配置到文件"""
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        deepseek_config = config_dir / "deepseek_config.json"
        
        config_data = {
            "api_key": api_key,
            "base_url": base_url or "https://api.deepseek.com/v1",
            "model": model or "deepseek-chat"
        }
        
        try:
            with open(deepseek_config, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            logger.info("DeepSeek配置已保存")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False


# 全局配置实例
config = Config()


def load_config(path: str | None = None) -> Config:
    """从指定路径加载JSON配置并更新全局配置对象"""
    if path:
        cfg_path = Path(path)
        if cfg_path.exists():
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        config._config.update(data)
                        logger.info(f"已加载自定义配置: {path}")
                    else:
                        logger.warning(f"配置文件{path}不是有效的JSON对象")
            except Exception as e:
                logger.error(f"加载自定义配置失败: {e}")
        else:
            logger.error(f"配置文件不存在: {path}")
    return config


# 便捷函数
def get_deepseek_config() -> Dict[str, str]:
    """获取DeepSeek配置"""
    return config.get_deepseek_config()


def is_test_mode() -> bool:
    """是否处于测试模式"""
    return config.is_test_mode()


def is_debug_mode() -> bool:
    """是否处于调试模式"""
    return config.is_debug_mode()


__all__ = [
    "Config",
    "config",
    "load_config",
    "get_deepseek_config",
    "is_test_mode",
    "is_debug_mode",
]
