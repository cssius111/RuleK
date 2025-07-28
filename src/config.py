"""
API配置数据模型
"""
from typing import Optional


class APIConfig:
    """API配置类"""
    
    def __init__(self, config_dict: dict = None):
        if config_dict is None:
            # 使用默认配置
            from src.utils.config import config
            deepseek_config = config.get_deepseek_config()
            self.deepseek_api_key = deepseek_config["api_key"]
            self.base_url = deepseek_config["base_url"]
            self.model = deepseek_config["model"]
            self.timeout = config.get("api", {}).get("timeout", 30)
            self.max_retries = config.get("api", {}).get("max_retries", 3)
        else:
            # 从字典初始化
            self.deepseek_api_key = config_dict.get("deepseek_api_key", "")
            self.base_url = config_dict.get("base_url", "https://api.deepseek.com/v1")
            self.model = config_dict.get("model", "deepseek-chat")
            self.timeout = config_dict.get("timeout", 30)
            self.max_retries = config_dict.get("max_retries", 3)
