#!/usr/bin/env python3
"""
Apply fixes for RuleK API errors
"""
import sys
from pathlib import Path

def fix_game_service():
    """Fix the create_rule method in game_service.py"""
    game_service_path = Path("web/backend/services/game_service.py")
    
    if not game_service_path.exists():
        print(f"❌ File not found: {game_service_path}")
        return False
    
    content = game_service_path.read_text()
    
    # Find and replace the create_rule method
    old_create_rule = '''    async def create_rule(self, rule_data: Dict) -> str:
        """创建新规则"""
        self.update_last_accessed()
        
        # 检查积分是否足够
        if self.game_state.fear_points < rule_data["cost"]:
            raise ValueError("Not enough fear points")
        
        # 创建规则
        rule = Rule(**rule_data)
        self.rule_manager.add_rule(rule)'''
    
    new_create_rule = '''    async def create_rule(self, rule_data: Dict) -> str:
        """创建新规则"""
        import uuid
        from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType, RuleRequirement
        
        self.update_last_accessed()
        
        # 检查积分是否足够
        if self.game_state.fear_points < rule_data["cost"]:
            raise ValueError("Not enough fear points")
        
        # Generate ID if not provided
        rule_id = rule_data.get("id") or f"rule_{uuid.uuid4().hex[:8]}"
        
        # Create trigger condition
        trigger_data = rule_data.get("trigger", {})
        trigger = TriggerCondition(
            action=trigger_data.get("action", trigger_data.get("type", "manual")),
            time_range=trigger_data.get("time_range"),
            location=trigger_data.get("location"),
            probability=trigger_data.get("probability", 0.8)
        )
        
        # Handle requirements time conversion
        requirements_data = rule_data.get("requirements", {})
        if requirements_data and "time" in requirements_data:
            time = requirements_data["time"]
            if isinstance(time, str):
                if time == "night":
                    trigger.time_range = {"from": "20:00", "to": "04:00"}
                elif time == "day":
                    trigger.time_range = {"from": "06:00", "to": "18:00"}
        
        # Create effect
        effect_data = rule_data.get("effect", {})
        effect_type = effect_data.get("type", "fear_gain")
        
        # Map common types to enum values
        type_mapping = {
            "damage": EffectType.FEAR_GAIN,
            "death": EffectType.INSTANT_DEATH,
            "fear": EffectType.FEAR_GAIN,
            "sanity": EffectType.SANITY_LOSS,
            "teleport": EffectType.TELEPORT,
            "transform": EffectType.TRANSFORM,
            "spawn": EffectType.SPAWN_SPIRIT,
            "event": EffectType.TRIGGER_EVENT
        }
        
        if effect_type in type_mapping:
            effect_type = type_mapping[effect_type]
        elif effect_type not in [e.value for e in EffectType]:
            effect_type = EffectType.FEAR_GAIN
            
        effect = RuleEffect(
            type=effect_type,
            params={"value": effect_data.get("value", 10)},
            fear_gain=effect_data.get("value", 50)
        )
        
        # Create requirements
        requirements = RuleRequirement()
        if requirements_data:
            if "areas" in requirements_data:
                requirements.areas = requirements_data["areas"]
            if "items" in requirements_data:
                requirements.items = requirements_data["items"]
        
        # Create rule with all required fields
        rule = Rule(
            id=rule_id,
            name=rule_data["name"],
            description=rule_data.get("description", ""),
            trigger=trigger,
            effect=effect,
            requirements=requirements,
            base_cost=rule_data.get("cost", 100)
        )
        
        self.rule_manager.add_rule(rule)'''
    
    if old_create_rule in content:
        content = content.replace(old_create_rule, new_create_rule)
        print("✅ Fixed create_rule method")
    else:
        print("⚠️ Could not find exact match for create_rule, attempting partial fix...")
        # Try a more general replacement
        import re
        pattern = r'async def create_rule\(self, rule_data: Dict\) -> str:.*?self\.rule_manager\.add_rule\(rule\)'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_create_rule, content, count=1, flags=re.DOTALL)
            print("✅ Applied partial fix for create_rule")
    
    # Fix NPC initialization in _create_npcs
    old_npcs = '''            # 添加到游戏状态
            self.game_state.npcs[npc.id] = npc.to_dict()'''
    
    new_npcs = '''            # 添加到游戏状态
            self.game_state.npcs[npc.id] = npc.to_dict()
            # Also add to npc_manager tracking
            self.npc_manager.npcs[npc.id] = npc'''
    
    if old_npcs in content:
        content = content.replace(old_npcs, new_npcs)
        print("✅ Fixed NPC tracking in _create_npcs")
    
    # Fix NPC retrieval in advance_turn
    old_advance = '''                npc = self.npc_manager.get_npc(npc_id)
                if npc:
                    action = self.npc_behavior.decide_action(npc, self.game_state)
                    if action:
                        events.append({
                            "type": "npc_action",
                            "npc": npc.name,
                            "action": action
                        })'''
    
    new_advance = '''                npc = self.npc_manager.get_npc(npc_id)
                if not npc:
                    # Recreate NPC from data if missing
                    from src.models.npc import NPC
                    npc = NPC(id=npc_id, **npc_data)
                    self.npc_manager.npcs[npc_id] = npc
                if npc:
                    action = self.npc_behavior.decide_action(npc, self.game_state)
                    if action:
                        events.append({
                            "type": "npc_action",
                            "npc": npc.name if hasattr(npc, 'name') else npc_data.get('name', 'Unknown'),
                            "action": action
                        })'''
    
    if old_advance in content:
        content = content.replace(old_advance, new_advance)
        print("✅ Fixed NPC retrieval in advance_turn")
    
    # Write back
    game_service_path.write_text(content)
    return True


def fix_planned_action_priority():
    """Fix the priority field in PlannedAction schema"""
    schemas_path = Path("src/api/schemas.py")
    
    if not schemas_path.exists():
        print(f"❌ File not found: {schemas_path}")
        return False
    
    content = schemas_path.read_text()
    
    # Fix PlannedAction priority field to accept both string and int
    old_priority = '''    priority: Literal["high", "medium", "low"] = Field(
        default="medium", description="优先级"
    )'''
    
    new_priority = '''    priority: Optional[Any] = Field(
        default="medium", description="优先级"
    )
    
    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, v):
        """Normalize priority to string format"""
        if isinstance(v, int):
            # Convert int 1-5 to high/medium/low
            if v >= 4:
                return "high"
            elif v >= 2:
                return "medium"
            else:
                return "low"
        elif isinstance(v, str):
            if v in ["high", "medium", "low"]:
                return v
            # Try to parse as int
            try:
                int_val = int(v)
                if int_val >= 4:
                    return "high"
                elif int_val >= 2:
                    return "medium"
                else:
                    return "low"
            except:
                return "medium"
        return "medium"'''
    
    if old_priority in content:
        content = content.replace(old_priority, new_priority)
        print("✅ Fixed PlannedAction priority field")
    else:
        print("⚠️ Could not find exact match for priority field")
    
    # Write back
    schemas_path.write_text(content)
    return True


def main():
    print("=" * 60)
    print("🔧 Applying RuleK API Fixes")
    print("=" * 60)
    
    # Change to project root
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)
    
    print("\n📝 Fixing game_service.py...")
    success1 = fix_game_service()
    
    print("\n📝 Fixing schemas.py...")
    success2 = fix_planned_action_priority()
    
    if success1 and success2:
        print("\n✅ All fixes applied successfully!")
        print("\n🎯 Next steps:")
        print("1. Restart the server: python start_web_server.py")
        print("2. Run tests: python fix_api.py")
    else:
        print("\n⚠️ Some fixes may not have been applied completely")
        print("Please review the changes manually")


if __name__ == "__main__":
    main()
