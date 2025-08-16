#!/usr/bin/env python3
"""快速安装缺失的依赖"""
import subprocess
import sys

print("="*60)
print("安装缺失的依赖")
print("="*60)

packages = [
    ('python-dotenv', '1.0.0', '读取.env文件'),
    ('tenacity', '9.1.2', 'API重试机制'),
    ('httpx', '0.25.2', 'HTTP客户端'),
]

print("\n需要安装的包：")
for pkg, version, desc in packages:
    print(f"  - {pkg}=={version} ({desc})")

print("\n开始安装...")
for pkg, version, desc in packages:
    print(f"\n安装 {pkg}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", f"{pkg}=={version}"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✅ {pkg} 安装成功")
        else:
            print(f"  ❌ {pkg} 安装失败")
            print(f"     错误: {result.stderr}")
    except Exception as e:
        print(f"  ❌ 安装失败: {e}")

print("\n" + "="*60)
print("验证安装")
print("="*60)

# 验证
print("\n检查包是否已安装：")
for pkg, _, _ in packages:
    try:
        __import__(pkg.replace('-', '_'))
        print(f"  ✅ {pkg} 已安装")
    except ImportError:
        print(f"  ❌ {pkg} 未安装")

print("\n下一步：")
print("1. 运行诊断脚本验证API密钥加载：")
print("   python scripts/test/diagnose_api_key.py")
print("\n2. 运行API测试：")
print("   pytest tests/api/ -v")
