#!/usr/bin/env python3
"""
Verify that API fixes are working correctly
"""
import subprocess
import time
import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def check_server_running():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_server():
    """Start the server in background"""
    print("🚀 Starting server...")
    # Start server in background
    process = subprocess.Popen(
        [sys.executable, "start_web_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    for i in range(10):
        time.sleep(2)
        if check_server_running():
            print("✅ Server started successfully")
            return process
    
    print("❌ Failed to start server")
    process.terminate()
    return None


def test_game_creation():
    """Test game creation"""
    print("\n1️⃣ Testing game creation...")
    response = requests.post(
        f"{BASE_URL}/api/games",
        json={"difficulty": "normal", "npc_count": 4}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Game created: {data['game_id']}")
        print(f"   NPCs: {len(data.get('npcs', []))}")
        print(f"   Fear points: {data.get('fear_points', 0)}")
        return data['game_id']
    else:
        print(f"❌ Game creation failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return None


def test_rule_creation(game_id):
    """Test rule creation"""
    print("\n2️⃣ Testing rule creation...")
    
    test_rules = [
        {
            "name": "Midnight Mirror",
            "description": "Looking at mirrors at midnight causes death",
            "requirements": {"time": "night"},
            "trigger": {"type": "time", "action": "look_mirror"},
            "effect": {"type": "damage", "value": 100},
            "cost": 150
        },
        {
            "name": "Red Word Curse",
            "description": "Speaking words with 'red' causes sanity loss",
            "trigger": {"action": "speak"},
            "effect": {"type": "sanity", "value": 20},
            "cost": 100
        }
    ]
    
    for i, rule_data in enumerate(test_rules, 1):
        print(f"\n   Testing rule {i}: {rule_data['name']}")
        response = requests.post(
            f"{BASE_URL}/api/games/{game_id}/rules",
            json=rule_data
        )
        
        if response.status_code == 200:
            print(f"   ✅ Rule created successfully")
            data = response.json()
            print(f"      Rule ID: {data.get('rule_id', 'N/A')}")
        else:
            print(f"   ❌ Rule creation failed: {response.status_code}")
            print(f"      Error: {response.text[:200]}")
            return False
    
    return True


def test_turn_advance(game_id):
    """Test turn advancement"""
    print("\n3️⃣ Testing turn advancement...")
    
    response = requests.post(f"{BASE_URL}/api/games/{game_id}/turn")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Turn advanced successfully")
        print(f"   New turn: {data.get('turn', 'N/A')}")
        print(f"   Events: {len(data.get('events', []))}")
        print(f"   Fear gained: {data.get('fear_gained', 0)}")
        
        # Print some events
        for event in data.get('events', [])[:3]:
            print(f"   - {event.get('type', 'unknown')}: {event}")
        
        return True
    else:
        print(f"❌ Turn advance failed: {response.status_code}")
        print(f"   Error: {response.text[:500]}")
        return False


def test_ai_functionality(game_id):
    """Test AI functionality"""
    print("\n4️⃣ Testing AI functionality...")
    
    # Initialize AI
    print("   Initializing AI...")
    response = requests.post(f"{BASE_URL}/api/games/{game_id}/ai/init")
    
    if response.status_code != 200:
        print(f"   ⚠️ AI initialization failed: {response.status_code}")
        print(f"      This is expected if DEEPSEEK_API_KEY is not configured")
        return None
    
    print("   ✅ AI initialized")
    
    # Run AI turn
    print("   Running AI turn...")
    response = requests.post(
        f"{BASE_URL}/api/games/{game_id}/ai/turn",
        json={"force_dialogue": True}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ AI turn completed")
        print(f"      Dialogues: {len(data.get('dialogue', []))}")
        print(f"      Actions: {len(data.get('actions', []))}")
        
        # Print sample dialogue
        for d in data.get('dialogue', [])[:2]:
            print(f"      {d.get('speaker', 'Unknown')}: {d.get('text', '')[:50]}...")
        
        return True
    else:
        print(f"   ❌ AI turn failed: {response.status_code}")
        print(f"      Error: {response.text[:500]}")
        return False


def main():
    print("=" * 60)
    print("🔍 RuleK API Fix Verification")
    print("=" * 60)
    
    # Check if server is running
    server_process = None
    if not check_server_running():
        print("⚠️ Server not running, attempting to start...")
        server_process = start_server()
        if not server_process:
            print("❌ Could not start server. Please start it manually:")
            print("   python start_web_server.py")
            return 1
    else:
        print("✅ Server is already running")
    
    try:
        # Run tests
        game_id = test_game_creation()
        if not game_id:
            print("\n❌ Cannot proceed without game creation")
            return 1
        
        rule_success = test_rule_creation(game_id)
        if not rule_success:
            print("\n⚠️ Rule creation has issues")
        
        turn_success = test_turn_advance(game_id)
        if not turn_success:
            print("\n⚠️ Turn advancement has issues")
        
        ai_result = test_ai_functionality(game_id)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        all_passed = rule_success and turn_success
        
        if all_passed:
            print("✅ All critical tests passed!")
            print("🎉 The API fixes are working correctly!")
        else:
            print("⚠️ Some tests failed. Please review the errors above.")
            print("\nTo apply fixes, run:")
            print("   python apply_fixes.py")
            print("\nThen restart the server and run this test again.")
        
        if ai_result is None:
            print("\nℹ️ AI functionality requires DEEPSEEK_API_KEY in .env file")
        elif ai_result:
            print("✅ AI functionality is working!")
        
        return 0 if all_passed else 1
        
    finally:
        # Clean up server process if we started it
        if server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait(timeout=5)


if __name__ == "__main__":
    sys.exit(main())
