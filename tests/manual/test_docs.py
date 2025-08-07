#!/usr/bin/env python
"""测试 API 文档端点"""

import requests

base_url = "http://localhost:8000"

print("=" * 50)
print("测试 RuleK API 端点")
print("=" * 50)

# 测试各种可能的文档端点
endpoints = [
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/docs",
    "/api",
]

for endpoint in endpoints:
    url = base_url + endpoint
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"✅ {endpoint:20} - 状态: {response.status_code}")
            if endpoint == "/":
                print(f"   响应: {response.json()}")
        else:
            print(f"❌ {endpoint:20} - 状态: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint:20} - 错误: {e}")

print("\n" + "=" * 50)
print("游戏 API 测试")
print("=" * 50)

# 测试游戏相关端点
try:
    # 获取已创建的游戏
    response = requests.get(f"{base_url}/api/games/game_07ecb3a5")
    if response.status_code == 200:
        print("✅ 游戏获取成功:")
        game_data = response.json()
        print(f"   - 游戏ID: {game_data.get('game_id')}")
        print(f"   - 当前回合: {game_data.get('current_turn')}")
        print(f"   - NPC数量: {len(game_data.get('npcs', []))}")
    else:
        print(f"❌ 游戏获取失败: {response.status_code}")
        print(f"   响应: {response.text}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n提示: 如果 /docs 不工作，可能是 FastAPI 版本或配置问题")
print("尝试访问 /openapi.json 查看 OpenAPI 规范")
