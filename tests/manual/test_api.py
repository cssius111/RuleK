#!/usr/bin/env python
"""
RuleK API 快速测试脚本
测试游戏的核心功能
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分节标题"""
    print(f"\n{'=' * 50}")
    print(f"{title}")
    print('=' * 50)

def test_game_api():
    """测试游戏 API"""
    
    # 你已创建的游戏 ID
    existing_game_id = "game_07ecb3a5"
    
    print_section("1. 获取已创建的游戏状态")
    try:
        response = requests.get(f"{BASE_URL}/api/games/{existing_game_id}")
        if response.status_code == 200:
            game_data = response.json()
            print(f"✅ 游戏状态获取成功!")
            print(f"   游戏ID: {game_data['game_id']}")
            print(f"   当前回合: {game_data['current_turn']}")
            print(f"   恐惧点数: {game_data['fear_points']}")
            print(f"   游戏阶段: {game_data['phase']}")
            print(f"   时间段: {game_data['time_of_day']}")
            print(f"   存活NPC数: {len([npc for npc in game_data['npcs'] if npc['is_alive']])}")
            print(f"   活跃规则数: {game_data['active_rules']}")
            
            # 显示NPC详情
            print("\n   NPC列表:")
            for npc in game_data['npcs'][:3]:  # 只显示前3个
                print(f"     - {npc['name']}: HP={npc['hp']}, 理智={npc['sanity']}, 位置={npc['location']}")
        else:
            print(f"❌ 获取失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print_section("2. 创建新游戏")
    try:
        create_data = {
            "difficulty": "hard",
            "npc_count": 6
        }
        response = requests.post(f"{BASE_URL}/api/games", json=create_data)
        if response.status_code == 200:
            new_game = response.json()
            new_game_id = new_game['game_id']
            print(f"✅ 新游戏创建成功!")
            print(f"   游戏ID: {new_game_id}")
            print(f"   NPC数量: {len(new_game['npcs'])}")
            
            # 测试新游戏的其他功能
            print_section("3. 测试新游戏功能")
            
            # 3.1 推进回合
            print("\n3.1 推进回合...")
            turn_response = requests.post(f"{BASE_URL}/api/games/{new_game_id}/turn")
            if turn_response.status_code == 200:
                turn_data = turn_response.json()
                print(f"✅ 回合推进成功!")
                print(f"   新回合: {turn_data.get('current_turn', 'N/A')}")
            else:
                print(f"❌ 回合推进失败: {turn_response.status_code}")
            
            # 3.2 创建规则
            print("\n3.2 创建规则...")
            rule_data = {
                "name": "禁止夜间开灯",
                "description": "夜晚时段在任何房间开灯会触发恐怖事件",
                "trigger_type": "action",
                "effect_type": "fear",
                "cost": 100
            }
            rule_response = requests.post(f"{BASE_URL}/api/games/{new_game_id}/rules", json=rule_data)
            if rule_response.status_code == 200:
                print(f"✅ 规则创建成功!")
            else:
                print(f"❌ 规则创建失败: {rule_response.status_code}")
                
            # 3.3 检查AI状态
            print("\n3.3 检查AI状态...")
            ai_status = requests.get(f"{BASE_URL}/api/games/{new_game_id}/ai/status")
            if ai_status.status_code == 200:
                ai_data = ai_status.json()
                print(f"✅ AI状态:")
                print(f"   AI启用: {ai_data.get('ai_enabled', False)}")
                print(f"   AI初始化: {ai_data.get('ai_initialized', False)}")
            else:
                print(f"❌ AI状态获取失败: {ai_status.status_code}")
                
        else:
            print(f"❌ 创建失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print_section("4. 其他端点测试")
    
    # 测试根路径
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"/ 端点: {response.status_code} - {response.json() if response.status_code == 200 else response.text[:50]}")
    except:
        print(f"/ 端点: 失败")
    
    # 测试健康检查
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"/health 端点: {response.status_code} - {response.json() if response.status_code == 200 else response.text[:50]}")
    except:
        print(f"/health 端点: 失败")
    
    # 测试文档端点
    for endpoint in ["/docs", "/redoc", "/openapi.json"]:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"{endpoint} 端点: ✅ 可访问")
            else:
                print(f"{endpoint} 端点: ❌ {response.status_code}")
        except:
            print(f"{endpoint} 端点: ❌ 连接失败")

if __name__ == "__main__":
    print("=" * 50)
    print("RuleK API 测试脚本")
    print("=" * 50)
    print(f"目标服务器: {BASE_URL}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_game_api()
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)
