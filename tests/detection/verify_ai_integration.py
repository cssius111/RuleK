#!/usr/bin/env python
"""
验证AI集成是否正常工作
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=== 验证AI集成 ===\n")

# 1. 检查环境变量
print("1. 检查环境变量...")
try:
    from src.utils.config import config
    deepseek_config = config.get_deepseek_config()
    api_key = deepseek_config.get("api_key", "")
    if api_key and len(api_key) > 10:
        print("✅ DeepSeek API密钥已配置")
    else:
        print("❌ DeepSeek API密钥未配置或无效")
    print(f"   Base URL: {deepseek_config.get('base_url')}")
    print(f"   Model: {deepseek_config.get('model')}")
except Exception as e:
    print(f"❌ 配置加载失败: {e}")

# 2. 检查核心模块导入
print("\n2. 检查核心模块导入...")
modules_to_check = [
    ("API Schemas", "src.api.schemas"),
    ("API Prompts", "src.api.prompts"),
    ("DeepSeek Client", "src.api.deepseek_client"),
    ("AI Turn Pipeline", "src.ai.turn_pipeline"),
    ("Game State Manager", "src.core.game_state"),
    ("Web Models", "web.backend.models"),
    ("Game Service", "web.backend.services.game_service"),
]

for name, module in modules_to_check:
    try:
        __import__(module)
        print(f"✅ {name} ({module})")
    except ImportError as e:
        print(f"❌ {name} ({module}): {e}")

# 3. 检查AI功能类
print("\n3. 检查AI功能类...")
try:
    from src.api.deepseek_client import DeepSeekClient
    from src.ai.turn_pipeline import AITurnPipeline
    from src.api.schemas import TurnPlan, RuleEvalResult
    print("✅ AI核心类导入成功")
except Exception as e:
    print(f"❌ AI核心类导入失败: {e}")

# 4. 检查Web API模型
print("\n4. 检查Web API模型...")
try:
    from web.backend.models import (
        AITurnRequest, AITurnPlanResponse,
        AIRuleEvaluationRequest, AIRuleEvaluationResponse,
        AINarrativeRequest, AINarrativeResponse
    )
    print("✅ Web API AI模型导入成功")
except Exception as e:
    print(f"❌ Web API AI模型导入失败: {e}")

# 5. 检查GameService AI方法
print("\n5. 检查GameService AI方法...")
try:
    from web.backend.services.game_service import GameService
    ai_methods = [
        "init_ai_pipeline",
        "is_ai_enabled", 
        "is_ai_initialized",
        "run_ai_turn",
        "evaluate_rule_nl",
        "generate_narrative"
    ]
    
    missing_methods = []
    for method in ai_methods:
        if not hasattr(GameService, method):
            missing_methods.append(method)
    
    if missing_methods:
        print(f"❌ GameService缺少以下AI方法: {missing_methods}")
    else:
        print("✅ GameService包含所有AI方法")
except Exception as e:
    print(f"❌ 检查GameService失败: {e}")

# 6. 检查配置文件
print("\n6. 检查配置文件...")
try:
    import json
    config_path = project_root / "config" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            config_data = json.load(f)
        
        if "ai_enabled" in config_data.get("game", {}):
            print("✅ config.json包含ai_enabled配置")
        else:
            print("❌ config.json缺少ai_enabled配置")
            
        if "ai_features" in config_data:
            print("✅ config.json包含ai_features配置")
        else:
            print("❌ config.json缺少ai_features配置")
    else:
        print("❌ config.json文件不存在")
except Exception as e:
    print(f"❌ 检查配置文件失败: {e}")

print("\n=== 验证完成 ===")
print("\n如果所有检查都通过（✅），AI集成应该可以正常工作。")
print("如果有失败的检查（❌），请根据错误信息进行修复。")
print("\n下一步:")
print("1. 运行测试脚本: python test_ai_integration.py")
print("2. 启动Web服务器: python web/backend/app.py")
print("3. 测试API端点: 访问 http://localhost:8000/docs")
