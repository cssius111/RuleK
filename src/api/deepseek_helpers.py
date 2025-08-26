from .deepseek_client import DeepSeekClient
from .deepseek_http_client import APIConfig
from src.utils.config import get_deepseek_config, is_test_mode
from src.utils.logger import get_logger

logger = get_logger("deepseek.helpers")


# 便捷函数：从config目录或环境变量创建客户端
async def create_default_client() -> DeepSeekClient:
    """创建默认配置的客户端"""
    # 获取配置
    deepseek_config = get_deepseek_config()

    # 创建API配置
    config = APIConfig()

    # 如果有API密钥，使用真实模式
    if deepseek_config.get("api_key"):
        config.api_key = deepseek_config["api_key"]
        config.base_url = deepseek_config.get("base_url", config.base_url)
        config.model = deepseek_config.get("model", config.model)
        config.mock_mode = False
        logger.info("使用真实API模式")
    else:
        # 否则使用Mock模式
        config.mock_mode = True
        logger.info("使用Mock模式（未配置API密钥）")

    # 测试模式下总是使用Mock
    if is_test_mode():
        config.mock_mode = True
        logger.info("测试模式：强制使用Mock")

    return DeepSeekClient(config)
