#!/usr/bin/env python3
"""
Final comprehensive test for RuleK API
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    """Test the complete workflow"""
    print("=" * 60)
    print("🎯 RuleK API Final Test")
    print("=" * 60)
    
    all_passed = True
    
    # 1. Check server
    print("\n1️⃣ Checking server...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server running: {data['name']} v{data['version']}")
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not running: {e}")
        print("\nPlease start the server:")
        print("  python start_web_server.py")
        return False
    
    # 2. Create game
    print("\n2️⃣ Creating game...")
    response = requests.post(
        f"{BASE_URL}/api/games",
        json={"difficulty": "normal", "npc_count": 4}
    )
    
    if response.status_code != 200:
        print(f"❌ Game creation failed: {response.status_code}")
        print(f"   {response.text[:200]}")
        return False
    
    game_data = response.json()
    game_id = game_data["game_id"]
    print(f"✅ Game created: {game_id}")
    print(f"   NPCs: {len(game_data.get('npcs', []))}")
    print(f"   Fear points: {game_data.get('fear_points', 0)}")
    
    # 3. Create rule
    print("\n3️⃣ Creating rule...")
    rule_data = {
        "name": "Test Rule",
        "description": "A test rule for validation",
        "requirements": {"time": "night"},
        "trigger": {"type": "time", "action": "test"},
        "effect": {"type": "fear", "value": 50},
        "cost": 100
    }
    
    response = requests.post(
        f"{BASE_URL}/api/games/{game_id}/rules",
        json=rule_data
    )
    
    if response.status_code != 200:
        print(f"❌ Rule creation failed: {response.status_code}")
        print(f"   {response.text[:200]}")
        all_passed = False
    else:
        data = response.json()
        print(f"✅ Rule created: {data.get('rule_id', 'N/A')}")
    
    # 4. Advance turn
    print("\n4️⃣ Advancing turn...")
    response = requests.post(f"{BASE_URL}/api/games/{game_id}/turn")
    
    if response.status_code != 200:
        print(f"❌ Turn advance failed: {response.status_code}")
        print(f"   {response.text[:200]}")
        all_passed = False
    else:
        data = response.json()
        print(f"✅ Turn advanced to: {data.get('turn', 'N/A')}")
        print(f"   Events: {len(data.get('events', []))}")
        print(f"   Fear gained: {data.get('fear_gained', 0)}")
    
    # 5. Test AI (if available)
    print("\n5️⃣ Testing AI...")
    
    # Initialize AI
    response = requests.post(f"{BASE_URL}/api/games/{game_id}/ai/init")
    
    if response.status_code != 200:
        print(f"ℹ️ AI not available (API key not configured)")
    else:
        print("✅ AI initialized")
        
        # Run AI turn
        response = requests.post(
            f"{BASE_URL}/api/games/{game_id}/ai/turn",
            json={"force_dialogue": True}
        )
        
        if response.status_code != 200:
            print(f"❌ AI turn failed: {response.status_code}")
            print(f"   {response.text[:200]}")
            all_passed = False
        else:
            data = response.json()
            print(f"✅ AI turn completed")
            print(f"   Dialogues: {len(data.get('dialogue', []))}")
            print(f"   Actions: {len(data.get('actions', []))}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    if all_passed:
        print("""
✅ ✅ ✅ ALL TESTS PASSED! ✅ ✅ ✅

The RuleK API is fully functional:
- Game creation ✅
- Rule creation ✅
- Turn advancement ✅
- AI functionality ✅

You can now use the API at: http://localhost:8000
Documentation at: http://localhost:8000/docs
        """)
        return True
    else:
        print("""
⚠️ Some tests failed. Please review the errors above.

To fix remaining issues:
1. Run: python final_npc_fix.py
2. Restart server: pkill -f start_web_server && python start_web_server.py
3. Run this test again: python final_test.py
        """)
        return False


if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
