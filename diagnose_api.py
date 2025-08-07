#!/usr/bin/env python
"""
诊断 API 错误的详细脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000"
GAME_ID = "game_18833acc"  # 使用新创建的游戏ID

def test_with_details():
    print("=" * 60)
    print("RuleK API 详细错误诊断")
    print("=" * 60)
    
    # 1. 获取当前游戏状态
    print("\n1. 获取游戏状态...")
    response = requests.get(f"{BASE_URL}/api/games/{GAME_ID}")
    if response.status_code == 200:
        game_data = response.json()
        print(f"✅ 游戏状态获取成功")
        print(f"   - 游戏阶段: {game_data['phase']}")
        print(f"   - 当前回合: {game_data['current_turn']}")
        print(f"   - NPC数量: {len(game_data['npcs'])}")
    else:
        print(f"❌ 获取失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return
    
    # 2. 尝试推进回合（带详细错误信息）
    print("\n2. 尝试推进回合...")
    try:
        response = requests.post(f"{BASE_URL}/api/games/{GAME_ID}/turn")
        print(f"   状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")
        
        # 尝试解析响应
        try:
            data = response.json()
            if response.status_code == 200:
                print(f"✅ 回合推进成功")
                print(f"   新回合: {data.get('current_turn')}")
            else:
                print(f"❌ 回合推进失败")
                print(f"   错误详情: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"❌ 响应解析失败")
            print(f"   原始响应: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 3. 尝试创建规则（使用正确的参数）
    print("\n3. 尝试创建规则...")
    
    # 查看OpenAPI规范了解正确的参数格式
    print("   3.1 检查规则创建的参数要求...")
    openapi_response = requests.get(f"{BASE_URL}/openapi.json")
    if openapi_response.status_code == 200:
        openapi = openapi_response.json()
        rule_endpoint = openapi.get('paths', {}).get('/api/games/{game_id}/rules', {}).get('post', {})
        if rule_endpoint:
            request_body = rule_endpoint.get('requestBody', {})
            schema = request_body.get('content', {}).get('application/json', {}).get('schema', {})
            if '$ref' in schema:
                ref_path = schema['$ref'].split('/')[-1]
                schema_def = openapi.get('components', {}).get('schemas', {}).get(ref_path, {})
                print(f"   规则创建需要的参数:")
                for prop, details in schema_def.get('properties', {}).items():
                    required = prop in schema_def.get('required', [])
                    print(f"     - {prop}: {details.get('type')} {'(必需)' if required else '(可选)'}")
                    if 'enum' in details:
                        print(f"       可选值: {details['enum']}")
    
    # 尝试几种不同的规则创建方式
    rule_attempts = [
        {
            "name": "测试规则1",
            "description": "这是一个测试规则",
            "trigger": {"type": "time", "value": "night"},
            "effect": {"type": "fear", "value": 20},
            "cost": 100
        },
        {
            "name": "测试规则2",
            "description": "简单的规则",
            "trigger_type": "action",
            "effect_type": "fear",
            "cost": 50
        },
        {
            "name": "测试规则3",
            "description": "最简规则"
        }
    ]
    
    for i, rule_data in enumerate(rule_attempts, 1):
        print(f"\n   3.{i+1} 尝试规则格式 {i}:")
        print(f"      参数: {json.dumps(rule_data, ensure_ascii=False)}")
        response = requests.post(
            f"{BASE_URL}/api/games/{GAME_ID}/rules",
            json=rule_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"      ✅ 创建成功!")
            break
        elif response.status_code == 422:
            error_detail = response.json()
            print(f"      ❌ 参数验证失败:")
            if 'detail' in error_detail:
                for error in error_detail['detail']:
                    print(f"         - {error.get('loc', [])}: {error.get('msg', '')}")
        else:
            print(f"      ❌ 失败: {response.status_code}")
            print(f"         {response.text[:200]}")
    
    # 4. AI状态和初始化
    print("\n4. AI功能测试...")
    
    # 检查AI状态
    response = requests.get(f"{BASE_URL}/api/games/{GAME_ID}/ai/status")
    if response.status_code == 200:
        ai_data = response.json()
        print(f"   AI启用: {ai_data['ai_enabled']}")
        print(f"   AI初始化: {ai_data['ai_initialized']}")
        
        if not ai_data['ai_initialized']:
            print("\n   尝试初始化AI...")
            init_response = requests.post(f"{BASE_URL}/api/games/{GAME_ID}/ai/init")
            if init_response.status_code == 200:
                print("   ✅ AI初始化成功")
            else:
                print(f"   ❌ AI初始化失败: {init_response.status_code}")
                print(f"      {init_response.text[:200]}")

if __name__ == "__main__":
    test_with_details()
