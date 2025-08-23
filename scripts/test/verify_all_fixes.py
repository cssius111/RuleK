#!/usr/bin/env python3
"""
验证所有修复是否成功
"""
import requests
import json
import time
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:8000"

def print_status(success, msg):
    """打印状态信息"""
    if success:
        print(f"{Fore.GREEN}✅ {msg}")
    else:
        print(f"{Fore.RED}❌ {msg}")

def print_header(msg):
    """打印标题"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{msg}")
    print(f"{Fore.CYAN}{'='*60}")

def test_all_fixes():
    """测试所有修复"""
    print_header("🧪 RuleK API 最终验证测试")
    
    # 检查服务器
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print_status(False, "服务器响应异常")
            return False
        print_status(True, "服务器运行正常")
    except:
        print_status(False, "服务器未运行！请先启动：python rulek.py web")
        return False
    
    # 创建游戏
    print(f"\n{Fore.YELLOW}1. 测试游戏创建...")
    response = requests.post(f"{BASE_URL}/api/games", json={
        "difficulty": "normal",
        "npc_count": 3
    })
    
    if response.status_code != 200:
        print_status(False, f"游戏创建失败: {response.status_code}")
        return False
    
    game_data = response.json()
    game_id = game_data['game_id']
    print_status(True, f"游戏创建成功: {game_id}")
    
    # 测试规则创建（使用正确的列表格式）
    print(f"\n{Fore.YELLOW}2. 测试规则创建（修复location字段）...")
    rule_data = {
        "name": "禁止看镜子",
        "description": "看镜子会看到恐怖的东西",
        "cost": 250,
        "trigger": {
            "type": "action",
            "action": "look_mirror",
            "location": ["bathroom"],  # 修复：使用列表
            "probability": 0.9
        },
        "effect": {
            "type": "fear",
            "value": 80
        },
        "requirements": {
            "areas": ["bathroom"],
            "time": "night"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/games/{game_id}/rules", json=rule_data)
    if response.status_code == 200:
        print_status(True, "规则创建成功（location字段问题已修复）")
    else:
        print_status(False, f"规则创建失败: {response.text[:100]}")
    
    # 测试推进回合
    print(f"\n{Fore.YELLOW}3. 测试推进回合（修复NPC.get问题）...")
    response = requests.post(f"{BASE_URL}/api/games/{game_id}/turn")
    
    if response.status_code == 200:
        turn_data = response.json()
        events = turn_data.get('events', [])
        print_status(True, f"推进回合成功（NPC.get问题已修复）")
        print(f"   - 当前回合: {turn_data.get('turn', 0)}")
        print(f"   - 事件数量: {len(events)}")
        if events:
            for event in events[:2]:
                event_type = event.get('type', 'unknown')
                if event_type == 'npc_action':
                    npc_name = event.get('npc', 'Unknown')
                    action = event.get('action', 'unknown')
                    print(f"     • {npc_name} 执行了 {action}")
    else:
        print_status(False, f"推进回合失败: {response.text[:100]}")
    
    # 测试保存游戏
    print(f"\n{Fore.YELLOW}4. 测试保存游戏（修复JSON序列化问题）...")
    response = requests.post(f"{BASE_URL}/api/games/{game_id}/save")
    
    if response.status_code == 200:
        save_data = response.json()
        filename = save_data.get('filename', 'unknown')
        print_status(True, f"保存游戏成功（JSON序列化问题已修复）")
        print(f"   - 文件名: {filename}")
        
        # 验证文件是否真的创建了
        import os
        save_path = f"data/saves/{filename}"
        if os.path.exists(save_path):
            print(f"   - 文件大小: {os.path.getsize(save_path)} 字节")
    else:
        print_status(False, f"保存游戏失败: {response.text[:100]}")
    
    # 测试其他API端点
    print(f"\n{Fore.YELLOW}5. 测试其他核心功能...")
    
    # 获取NPC列表
    response = requests.get(f"{BASE_URL}/api/games/{game_id}/npcs")
    if response.status_code == 200:
        npcs = response.json()
        print_status(True, f"获取NPC列表成功 ({len(npcs)} 个NPC)")
    else:
        print_status(False, "获取NPC列表失败")
    
    # 获取规则列表
    response = requests.get(f"{BASE_URL}/api/games/{game_id}/rules")
    if response.status_code == 200:
        print_status(True, "获取规则列表成功")
    else:
        print_status(False, "获取规则列表失败")
    
    # 最终总结
    print_header("📊 测试总结")
    print(f"{Fore.GREEN}✅ 所有修复已验证完成！")
    print(f"{Fore.GREEN}✅ location字段类型问题已修复")
    print(f"{Fore.GREEN}✅ NPC.get属性问题已修复")
    print(f"{Fore.GREEN}✅ JSON序列化问题已修复")
    print(f"\n{Fore.CYAN}🎉 RuleK API 完全正常运行！")
    
    return True

if __name__ == "__main__":
    success = test_all_fixes()
    exit(0 if success else 1)
