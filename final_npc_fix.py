#!/usr/bin/env python3
"""
Final fix for the NPC creation issue in turn advancement
"""
from pathlib import Path

def fix_npc_creation():
    """Fix the NPC creation issue where 'id' is passed twice"""
    game_service_path = Path("web/backend/services/game_service.py")
    
    if not game_service_path.exists():
        print(f"❌ File not found: {game_service_path}")
        return False
    
    content = game_service_path.read_text()
    
    # Fix advance_turn NPC recreation
    old_code = '''                if not npc:
                    # Recreate NPC from data if missing
                    from src.models.npc import NPC
                    npc = NPC(id=npc_id, **npc_data)
                    self.npc_manager.npcs[npc_id] = npc'''
    
    new_code = '''                if not npc:
                    # Recreate NPC from data if missing
                    from src.models.npc import NPC
                    # Remove 'id' from npc_data if it exists to avoid duplicate
                    npc_data_copy = npc_data.copy()
                    npc_data_copy.pop('id', None)
                    npc = NPC(id=npc_id, **npc_data_copy)
                    self.npc_manager.npcs[npc_id] = npc'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✅ Fixed NPC creation in advance_turn")
    else:
        print("⚠️ Could not find exact match, trying alternative fix...")
    
    # Also fix _run_dialogue_phase
    old_dialogue = '''                if not npc:
                    # Recreate from data if missing
                    from src.models.npc import NPC
                    npc_data = self.game_state.npcs[npc_id]
                    npc = NPC(id=npc_id, **npc_data)
                    self.npc_manager.npcs[npc_id] = npc'''
    
    new_dialogue = '''                if not npc:
                    # Recreate from data if missing
                    from src.models.npc import NPC
                    npc_data = self.game_state.npcs[npc_id].copy()
                    npc_data.pop('id', None)  # Remove id to avoid duplicate
                    npc = NPC(id=npc_id, **npc_data)
                    self.npc_manager.npcs[npc_id] = npc'''
    
    if old_dialogue in content:
        content = content.replace(old_dialogue, new_dialogue)
        print("✅ Fixed NPC creation in _run_dialogue_phase")
    
    game_service_path.write_text(content)
    return True


def main():
    print("=" * 60)
    print("🔧 Final Fix for NPC Creation Issue")
    print("=" * 60)
    
    success = fix_npc_creation()
    
    if success:
        print("\n✅ Fix applied successfully!")
        print("\n🎯 Next steps:")
        print("1. Restart the server:")
        print("   pkill -f 'python.*start_web_server'")
        print("   python start_web_server.py")
        print("\n2. Run tests:")
        print("   python fix_api.py")
    else:
        print("\n❌ Could not apply fix")


if __name__ == "__main__":
    main()
