#!/usr/bin/env python3
"""诊断API密钥加载问题"""
import sys
import os
sys.path.insert(0, '/Users/chenpinle/Desktop/杂/pythonProject/RuleK')

print("="*60)
print("API密钥加载诊断")
print("="*60)

# 1. 检查python-dotenv是否已安装
print("\n1. 检查python-dotenv安装状态：")
try:
    import dotenv
    print("  ✅ python-dotenv已安装")
    print(f"     版本: {dotenv.__version__}")
except ImportError:
    print("  ❌ python-dotenv未安装！")
    print("     请运行: pip install python-dotenv")

# 2. 直接读取.env文件
print("\n2. 直接读取.env文件：")
env_path = '/Users/chenpinle/Desktop/杂/pythonProject/RuleK/.env'
if os.path.exists(env_path):
    print(f"  ✅ .env文件存在: {env_path}")
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('DEEPSEEK_API_KEY'):
                key = line.split('=')[1].strip()
                print(f"     API密钥: {key[:10]}...{key[-4:]}")
                break
else:
    print(f"  ❌ .env文件不存在: {env_path}")

# 3. 检查环境变量
print("\n3. 检查环境变量：")
api_key_env = os.environ.get('DEEPSEEK_API_KEY')
if api_key_env:
    print(f"  ✅ 环境变量已设置: {api_key_env[:10]}...{api_key_env[-4:]}")
else:
    print("  ❌ 环境变量未设置")

# 4. 使用Config类加载
print("\n4. 使用Config类加载：")
try:
    from src.utils.config import Config
    config = Config()
    deepseek_config = config.get_deepseek_config()
    api_key = deepseek_config.get('api_key')
    if api_key:
        print(f"  ✅ Config加载成功: {api_key[:10]}...{api_key[-4:]}")
        print(f"     base_url: {deepseek_config.get('base_url')}")
        print(f"     model: {deepseek_config.get('model')}")
    else:
        print("  ❌ Config未能加载API密钥")
except Exception as e:
    print(f"  ❌ Config加载失败: {e}")

# 5. 测试DeepSeekClient
print("\n5. 测试DeepSeekClient：")
try:
    from src.api.deepseek_client import DeepSeekClient
    client = DeepSeekClient()
    print(f"  API密钥: {client.config.api_key[:10] if client.config.api_key else 'None'}...")
    print(f"  Mock模式: {client.config.mock_mode}")
    if client.config.mock_mode:
        print("  ⚠️  客户端在mock模式下运行（没有读取到API密钥）")
    else:
        print("  ✅ 客户端使用真实API密钥")
except Exception as e:
    print(f"  ❌ 创建客户端失败: {e}")

print("\n" + "="*60)
print("诊断结果")
print("="*60)

if not api_key_env and 'dotenv' not in sys.modules:
    print("❌ 问题：python-dotenv未安装，.env文件未被加载")
    print("\n解决方案：")
    print("1. 安装python-dotenv:")
    print("   pip install python-dotenv")
    print("\n2. 或手动设置环境变量:")
    print("   export DEEPSEEK_API_KEY=你的密钥")
elif api_key_env:
    print("✅ API密钥已正确加载")
else:
    print("⚠️ 可能的问题：")
    print("- .env文件格式不正确")
    print("- Config类加载逻辑有问题")
