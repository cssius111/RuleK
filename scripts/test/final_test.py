#!/usr/bin/env python3
"""
最终测试：模拟用户创建游戏的完整流程
"""

import requests
import json
import time

print("="*60)
print("🎮 RuleK 游戏创建完整测试")
print("="*60)

# 配置
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:5173"

print("\n📍 访问地址:")
print(f"   前端: {FRONTEND_BASE}")
print(f"   新游戏页面: {FRONTEND_BASE}/new-game")
print(f"   API文档: {API_BASE}/docs")

print("\n" + "="*60)
print("✅ 服务状态检查")
print("="*60)

# 检查前端
try:
    r = requests.get(FRONTEND_BASE, timeout=2)
    print(f"✅ 前端服务: 运行中 (状态码: {r.status_code})")
except:
    print("❌ 前端服务: 未运行")

# 检查后端
try:
    r = requests.get(f"{API_BASE}/health", timeout=2)
    print(f"✅ 后端服务: 运行中 (状态码: {r.status_code})")
except:
    print("❌ 后端服务: 未运行")

print("\n" + "="*60)
print("🧪 API测试")
print("="*60)

# 测试不同的数据格式
test_configs = [
    {
        "name": "蛇形命名（snake_case）",
        "data": {
            "difficulty": "normal",
            "initial_fear_points": 1000,
            "initial_npc_count": 4,
            "ai_enabled": False,
            "player_name": "TestPlayer1"
        }
    },
    {
        "name": "驼峰命名（camelCase）",
        "data": {
            "difficulty": "normal",
            "initialFearPoints": 1000,
            "initialNPCCount": 4,
            "aiEnabled": False,
            "playerName": "TestPlayer2"
        }
    }
]

for config in test_configs:
    print(f"\n测试 {config['name']}:")
    try:
        response = requests.post(
            f"{API_BASE}/api/games",
            json=config["data"],
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 成功！游戏ID: {data.get('game_id', 'N/A')}")
        else:
            print(f"  ❌ 失败 (状态码: {response.status_code})")
            print(f"     错误: {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")

print("\n" + "="*60)
print("🌐 前端测试步骤")
print("="*60)

print("""
1. 打开浏览器访问: http://localhost:5173/new-game

2. 检查页面元素:
   - 玩家名称输入框
   - 难度选择按钮
   - NPC数量滑块
   - 恐惧点数输入
   - AI开关
   - "开启地狱之门"按钮

3. 填写表单并提交:
   - 输入任意玩家名称
   - 选择难度
   - 设置NPC数量为4
   - 恐惧点数为1000
   - 点击"开启地狱之门"

4. 打开浏览器控制台 (F12) 查看:
   - 是否有JavaScript错误
   - 网络请求是否发送到正确的API地址
   - 响应数据是否正确
""")

print("\n" + "="*60)
print("📝 常见问题和解决方案")
print("="*60)

print("""
问题1: "initGame is not a function"
解决: 已修复 - 删除了冲突的game.js文件

问题2: API请求失败
解决: 检查.env文件中的VITE_API_BASE_URL是否为http://localhost:8000

问题3: CORS错误
解决: 后端已配置允许http://localhost:5173的请求

问题4: 页面空白
解决: 清除浏览器缓存 (Cmd+Shift+R)
""")

print("\n" + "="*60)
print("✨ 测试完成！")
print("="*60)
print("\n请按照上述步骤在浏览器中测试游戏创建功能。")
print("如果仍有问题，请查看浏览器控制台的错误信息。\n")
