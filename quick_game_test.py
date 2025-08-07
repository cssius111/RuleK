#!/usr/bin/env python
"""
简单的游戏操作脚本
使用新创建的游戏进行基本操作
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
GAME_ID = "game_18833acc"  # 使用刚创建的游戏

def pretty_print(data, title=""):
    if title:
        print(f"\n{'='*50}")
        print(f"{title}")
        print('='*50)
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    print("🎮 RuleK 游戏操作演示")
    print(f"游戏ID: {GAME_ID}")
    
    # 1. 获取游戏状态
    print("\n📊 获取当前游戏状态...")
    response = requests.get(f"{BASE_URL}/api/games/{GAME_ID}")
    if response.status_code == 200:
        game_data = response.json()
        print(f"✅ 游戏状态:")
        print(f"  - 回合: {game_data['current_turn']}")
        print(f"  - 阶段: {game_data['phase']}")
        print(f"  - 恐惧点数: {game_data['fear_points']}")
        print(f"  - 时间: {game_data['time_of_day']}")
        print(f"  - NPC数量: {len(game_data['npcs'])}")
        
        # 显示前3个NPC
        print("\n👥 NPC列表 (前3个):")
        for npc in game_data['npcs'][:3]:
            print(f"  - {npc['name']}: HP={npc['hp']}, 理智={npc['sanity']}, 位置={npc['location']}")
    else:
        print(f"❌ 获取失败: {response.status_code}")
        print("需要创建新游戏")
        return
    
    # 2. 获取规则列表
    print("\n📜 获取规则列表...")
    response = requests.get(f"{BASE_URL}/api/games/{GAME_ID}/rules")
    if response.status_code == 200:
        rules = response.json()
        if rules:
            print(f"✅ 当前有 {len(rules)} 条规则")
            for rule in rules:
                print(f"  - {rule.get('name', '未命名')}: {rule.get('description', '无描述')}")
        else:
            print("📝 当前没有规则")
    
    # 3. 尝试创建一个简单规则
    print("\n➕ 创建新规则...")
    
    # 尝试最简单的规则格式
    simple_rule = {
        "name": "午夜惊魂",
        "description": "午夜时分触发恐怖事件"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/games/{GAME_ID}/rules",
        json=simple_rule
    )
    
    if response.status_code == 200:
        print("✅ 规则创建成功!")
        rule_data = response.json()
        pretty_print(rule_data, "创建的规则")
    elif response.status_code == 422:
        print("❌ 参数格式错误，尝试其他格式...")
        # 尝试更完整的格式
        full_rule = {
            "name": "禁止开灯",
            "description": "在黑暗中开灯会触发恐怖事件",
            "trigger": {
                "type": "action",
                "action": "turn_on_light",
                "condition": "time == 'night'"
            },
            "effect": {
                "type": "fear",
                "amount": 30,
                "target": "triggerer"
            },
            "cost": 100,
            "cooldown": 0
        }
        response = requests.post(
            f"{BASE_URL}/api/games/{GAME_ID}/rules",
            json=full_rule
        )
        if response.status_code == 200:
            print("✅ 使用完整格式创建成功!")
        else:
            print(f"❌ 仍然失败: {response.status_code}")
            print(f"错误: {response.text[:200]}")
    
    # 4. 获取NPC列表
    print("\n👥 获取NPC详细信息...")
    response = requests.get(f"{BASE_URL}/api/games/{GAME_ID}/npcs")
    if response.status_code == 200:
        npcs = response.json()
        print(f"✅ 共有 {len(npcs)} 个NPC")
        
        # 统计NPC状态
        alive_count = sum(1 for npc in npcs if npc.get('is_alive', True))
        locations = {}
        for npc in npcs:
            loc = npc.get('location', 'unknown')
            locations[loc] = locations.get(loc, 0) + 1
        
        print(f"  - 存活: {alive_count}/{len(npcs)}")
        print(f"  - 位置分布:")
        for loc, count in locations.items():
            print(f"    * {loc}: {count}人")
    
    # 5. 测试健康检查
    print("\n💚 健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        health = response.json()
        print(f"✅ 服务器健康")
        print(f"  - 状态: {health['status']}")
        print(f"  - 活跃游戏数: {health['active_games']}")
        print(f"  - 时间: {health['timestamp']}")
    
    print("\n" + "="*50)
    print("✨ 测试完成!")
    print("="*50)
    print("\n提示:")
    print("1. 访问 http://localhost:8000/docs 查看完整API文档")
    print("2. 使用 file:///Users/chenpinle/Desktop/杂/pythonProject/RuleK/api_test.html 进行可视化测试")
    print(f"3. 当前游戏ID: {GAME_ID}")

if __name__ == "__main__":
    main()
