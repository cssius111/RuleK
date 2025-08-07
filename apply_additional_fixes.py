#!/usr/bin/env python3
"""
Apply additional fixes for remaining RuleK API errors
"""
import sys
from pathlib import Path

def fix_rule_to_dict_issue():
    """Fix the to_dict() issue in game_service.py"""
    game_service_path = Path("web/backend/services/game_service.py")
    
    if not game_service_path.exists():
        print(f"❌ File not found: {game_service_path}")
        return False
    
    content = game_service_path.read_text()
    
    # Replace rule.to_dict() with rule.model_dump()
    content = content.replace('rule.to_dict()', 'rule.model_dump()')
    
    # Also ensure the broadcast_update uses model_dump instead of to_dict
    old_broadcast = '''        await self.broadcast_update({
            "update_type": "rule",
            "data": {
                "action": "created",
                "rule": rule.to_dict()
            }
        })'''
    
    new_broadcast = '''        await self.broadcast_update({
            "update_type": "rule",
            "data": {
                "action": "created",
                "rule": rule.model_dump()
            }
        })'''
    
    if old_broadcast in content:
        content = content.replace(old_broadcast, new_broadcast)
        print("✅ Fixed rule.to_dict() in broadcast_update")
    
    # Also fix get_rules method if it uses to_dict
    content = content.replace('rule.to_dict()', 'rule.model_dump()')
    
    game_service_path.write_text(content)
    print("✅ Fixed all to_dict() calls for Rule model")
    return True


def fix_ai_action_response_priority():
    """Fix the AIActionResponse priority field to handle string/int conversion"""
    models_path = Path("web/backend/models.py")
    
    if not models_path.exists():
        print(f"❌ File not found: {models_path}")
        return False
    
    content = models_path.read_text()
    
    # Find and replace the AIActionResponse class
    old_ai_action = '''class AIActionResponse(BaseModel):
    """AI行动响应"""
    npc: str
    action: str
    target: Optional[str] = None
    reason: Optional[str] = None
    risk: Optional[str] = None
    priority: int = 1'''
    
    new_ai_action = '''class AIActionResponse(BaseModel):
    """AI行动响应"""
    npc: str
    action: str
    target: Optional[str] = None
    reason: Optional[str] = None
    risk: Optional[str] = None
    priority: Optional[Any] = 1
    
    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, v):
        """Normalize priority to integer"""
        if isinstance(v, int):
            return max(1, min(5, v))
        elif isinstance(v, str):
            # Try to parse as int
            try:
                return max(1, min(5, int(v)))
            except:
                # Map string priorities to integers
                priority_map = {
                    "low": 1,
                    "medium": 3,
                    "high": 5,
                    "hh": 5,  # Handle typo
                    "ll": 1,  # Handle typo
                    "mm": 3,  # Handle typo
                }
                return priority_map.get(v.lower(), 3)
        return 3  # Default to medium'''
    
    if old_ai_action in content:
        content = content.replace(old_ai_action, new_ai_action)
        print("✅ Fixed AIActionResponse priority field")
    else:
        print("⚠️ Could not find exact match for AIActionResponse, attempting manual fix...")
        # Try more flexible replacement
        import re
        pattern = r'class AIActionResponse\(BaseModel\):.*?priority: int = 1'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_ai_action, content, count=1, flags=re.DOTALL)
            print("✅ Applied manual fix for AIActionResponse")
    
    # Make sure field_validator is imported
    if "field_validator" not in content:
        content = content.replace(
            "from pydantic import BaseModel, Field, ConfigDict",
            "from pydantic import BaseModel, Field, ConfigDict, field_validator"
        )
        print("✅ Added field_validator import")
    
    models_path.write_text(content)
    return True


def fix_npc_tracking_more():
    """Additional fix for NPC tracking"""
    game_service_path = Path("web/backend/services/game_service.py")
    
    if not game_service_path.exists():
        print(f"❌ File not found: {game_service_path}")
        return False
    
    content = game_service_path.read_text()
    
    # Fix _run_dialogue_phase to handle None NPCs
    old_dialogue = '''        npcs = [self.npc_manager.get_npc(npc_id) 
                for npc_id in self.game_state.npcs 
                if self.game_state.npcs[npc_id].get("hp", 0) > 0]'''
    
    new_dialogue = '''        npcs = []
        for npc_id in self.game_state.npcs:
            if self.game_state.npcs[npc_id].get("hp", 0) > 0:
                npc = self.npc_manager.get_npc(npc_id)
                if not npc:
                    # Recreate from data if missing
                    from src.models.npc import NPC
                    npc_data = self.game_state.npcs[npc_id]
                    npc = NPC(id=npc_id, **npc_data)
                    self.npc_manager.npcs[npc_id] = npc
                if npc:
                    npcs.append(npc)'''
    
    if old_dialogue in content:
        content = content.replace(old_dialogue, new_dialogue)
        print("✅ Fixed NPC retrieval in _run_dialogue_phase")
    
    game_service_path.write_text(content)
    return True


def fix_rule_executor():
    """Fix RuleExecutor to return proper results"""
    executor_path = Path("src/core/rule_executor.py")
    
    if executor_path.exists():
        content = executor_path.read_text()
        
        # Make sure execute method returns at least an empty dict
        if "def execute(" in content and "return None" in content:
            content = content.replace("return None", "return {}")
            executor_path.write_text(content)
            print("✅ Fixed RuleExecutor to return dict instead of None")
            return True
    
    return False


def fix_rule_manager():
    """Fix RuleManager to handle rules properly"""
    manager_path = Path("src/models/rule_manager.py")
    
    if manager_path.exists():
        content = manager_path.read_text()
        
        # Make sure active_rules is always a list
        if "__init__" in content and "self.active_rules = " not in content:
            # Add initialization of active_rules
            content = content.replace(
                "def __init__(self):",
                "def __init__(self):\n        self.active_rules = []"
            )
            manager_path.write_text(content)
            print("✅ Fixed RuleManager initialization")
            return True
    
    return False


def main():
    print("=" * 60)
    print("🔧 Applying Additional RuleK API Fixes")
    print("=" * 60)
    
    # Change to project root
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)
    
    print("\n📝 Fixing Rule.to_dict() issue...")
    success1 = fix_rule_to_dict_issue()
    
    print("\n📝 Fixing AIActionResponse priority...")
    success2 = fix_ai_action_response_priority()
    
    print("\n📝 Fixing NPC tracking in dialogue phase...")
    success3 = fix_npc_tracking_more()
    
    print("\n📝 Fixing RuleExecutor...")
    success4 = fix_rule_executor()
    
    print("\n📝 Fixing RuleManager...")
    success5 = fix_rule_manager()
    
    if success1 and success2 and success3:
        print("\n✅ All critical fixes applied successfully!")
        print("\n🎯 Next steps:")
        print("1. Restart the server:")
        print("   pkill -f 'python.*start_web_server'  # Stop old server")
        print("   python start_web_server.py")
        print("")
        print("2. Run tests:")
        print("   python verify_fixes.py")
        print("   python fix_api.py")
    else:
        print("\n⚠️ Some fixes may not have been applied")
        print("Please review the changes manually")


if __name__ == "__main__":
    main()
