#!/usr/bin/env python3
"""
Test script to identify specific API errors
"""
import requests
import json
import traceback

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("Testing RuleK API Errors")
    print("=" * 60)
    
    # 1. Create game
    print("\n1. Creating game...")
    response = requests.post(f"{BASE_URL}/api/games", json={"difficulty": "normal", "npc_count": 4})
    if response.status_code != 200:
        print(f"❌ Game creation failed: {response.status_code}")
        print(response.text)
        return
    
    game_data = response.json()
    game_id = game_data["game_id"]
    print(f"✅ Game created: {game_id}")
    
    # 2. Test rule creation
    print("\n2. Testing rule creation...")
    rule_data = {
        "name": "Test Rule",
        "description": "Test rule description",
        "requirements": {"time": "night"},
        "trigger": {"type": "time"},
        "effect": {"type": "damage", "value": 10},
        "cost": 100
    }
    
    response = requests.post(f"{BASE_URL}/api/games/{game_id}/rules", json=rule_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Rule creation failed")
        print(f"Response: {response.text[:500]}")
    else:
        print(f"✅ Rule created")
    
    # 3. Test turn advance
    print("\n3. Testing turn advance...")
    response = requests.post(f"{BASE_URL}/api/games/{game_id}/turn")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Turn advance failed")
        print(f"Response: {response.text[:500]}")
    else:
        print(f"✅ Turn advanced")
    
    # 4. Test AI turn (if available)
    print("\n4. Testing AI turn...")
    
    # First init AI
    response = requests.post(f"{BASE_URL}/api/games/{game_id}/ai/init")
    print(f"AI Init Status: {response.status_code}")
    
    if response.status_code == 200:
        # Try AI turn
        response = requests.post(f"{BASE_URL}/api/games/{game_id}/ai/turn", 
                               json={"force_dialogue": True})
        print(f"AI Turn Status: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ AI turn failed")
            print(f"Response: {response.text[:500]}")
        else:
            print(f"✅ AI turn completed")

if __name__ == "__main__":
    test_api()
