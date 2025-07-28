"""
实现简单的自定义规则创建功能
"""
from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType, LocationType
import uuid

async def create_custom_rule_enhanced():
    """增强版自定义规则创建"""
    print("\n🔧 自定义规则创建向导")
    print("="*50)
    
    # 1. 规则名称
    name = input("\n规则名称: ").strip()
    if not name:
        print("❌ 名称不能为空")
        return None
        
    # 2. 规则描述
    description = input("规则描述: ").strip()
    
    # 3. 触发条件
    print("\n触发条件类型:")
    print("1. 动作触发 (如：开灯、照镜子)")
    print("2. 时间触发 (如：午夜、深夜)")
    print("3. 地点触发 (如：进入某个房间)")
    print("4. 物品触发 (如：使用某个物品)")
    
    trigger_type = input("选择触发类型 (1-4): ").strip()
    
    trigger = TriggerCondition()
    
    if trigger_type == "1":
        print("\n可选动作: move, search, look_mirror, open_door, turn_around, use_item")
        action = input("触发动作: ").strip()
        trigger.action = action
        
    elif trigger_type == "2":
        print("\n时间段: morning, afternoon, evening, night, midnight")
        time = input("触发时间: ").strip()
        trigger.time_range = time
        
    elif trigger_type == "3":
        print("\n地点类型: bedroom, bathroom, kitchen, corridor, basement")
        location = input("触发地点: ").strip()
        trigger.location_type = location
        
    elif trigger_type == "4":
        item = input("触发物品名称: ").strip()
        trigger.item = item
    else:
        print("❌ 无效选择")
        return None
        
    # 4. 触发概率
    try:
        probability = float(input("\n触发概率 (0.0-1.0, 默认0.8): ").strip() or "0.8")
        trigger.probability = max(0.0, min(1.0, probability))
    except ValueError:
        trigger.probability = 0.8
        
    # 5. 效果类型
    print("\n效果类型:")
    print("1. 立即死亡")
    print("2. 增加恐惧")
    print("3. 降低理智")
    print("4. 传送到其他地点")
    print("5. 获得物品")
    
    effect_type = input("选择效果 (1-5): ").strip()
    
    effect = RuleEffect()
    
    if effect_type == "1":
        effect.type = EffectType.INSTANT_DEATH
        effect.death_description = input("死亡描述: ").strip() or "违反了规则，付出了代价"
        
    elif effect_type == "2":
        effect.type = EffectType.FEAR_GAIN
        try:
            fear = int(input("恐惧增加量 (10-50): ").strip() or "20")
            effect.fear_gain = max(10, min(50, fear))
        except ValueError:
            effect.fear_gain = 20
            
    elif effect_type == "3":
        effect.type = EffectType.SANITY_LOSS
        try:
            sanity = int(input("理智减少量 (10-50): ").strip() or "20")
            effect.sanity_loss = max(10, min(50, sanity))
        except ValueError:
            effect.sanity_loss = 20
            
    elif effect_type == "4":
        effect.type = EffectType.TELEPORT
        effect.teleport_location = input("传送目标地点: ").strip() or "basement"
        
    elif effect_type == "5":
        effect.type = EffectType.ITEM_GAIN
        effect.item_name = input("获得物品名称: ").strip() or "神秘钥匙"
    else:
        print("❌ 无效选择")
        return None
        
    # 6. 破绽（可选）
    has_loophole = input("\n是否设置破绽？(y/n): ").strip().lower()
    loopholes = []
    if has_loophole == 'y':
        print("破绽类型:")
        print("1. 携带特定物品可免疫")
        print("2. 特定时间段无效")
        print("3. 特定地点无效")
        
        loophole_type = input("选择破绽类型 (1-3): ").strip()
        
        if loophole_type == "1":
            item = input("免疫物品: ").strip()
            loopholes.append({"type": "item_immunity", "item": item})
        elif loophole_type == "2":
            time = input("无效时间段: ").strip()
            loopholes.append({"type": "time_immunity", "time": time})
        elif loophole_type == "3":
            location = input("无效地点: ").strip()
            loopholes.append({"type": "location_immunity", "location": location})
            
    # 7. 冷却时间
    try:
        cooldown = int(input("\n冷却回合数 (0-5, 默认0): ").strip() or "0")
        cooldown = max(0, min(5, cooldown))
    except ValueError:
        cooldown = 0
        
    # 8. 成本计算
    base_cost = 100
    
    # 效果成本
    effect_costs = {
        EffectType.INSTANT_DEATH: 300,
        EffectType.FEAR_GAIN: 50,
        EffectType.SANITY_LOSS: 50,
        EffectType.TELEPORT: 100,
        EffectType.ITEM_GAIN: 80
    }
    base_cost += effect_costs.get(effect.type, 100)
    
    # 概率调整
    if trigger.probability >= 0.9:
        base_cost += 50
    elif trigger.probability <= 0.3:
        base_cost -= 30
        
    # 破绽减少成本
    base_cost -= len(loopholes) * 50
    
    # 冷却减少成本
    base_cost -= cooldown * 10
    
    base_cost = max(50, base_cost)  # 最低50点
    
    # 创建规则
    rule = Rule(
        id=f"custom_{uuid.uuid4().hex[:8]}",
        name=name,
        description=description,
        trigger=trigger,
        effect=effect,
        loopholes=loopholes,
        cooldown=cooldown,
        base_cost=base_cost,
        level=1
    )
    
    # 显示创建的规则
    print("\n" + "="*50)
    print("📜 规则预览")
    print(f"名称: {rule.name}")
    print(f"描述: {rule.description}")
    print(f"触发条件: {trigger}")
    print(f"效果: {effect.type.value}")
    print(f"成本: {rule.calculate_total_cost()} 恐惧积分")
    if loopholes:
        print(f"破绽: {len(loopholes)}个")
    print("="*50)
    
    return rule

# 集成到CLI游戏中的修改
def integrate_custom_rule_creation():
    """
    将此功能集成到 cli_game.py 中
    替换原有的 create_custom_rule 方法
    """
    code = '''
    async def create_custom_rule(self):
        """创建自定义规则"""
        from custom_rule_creator import create_custom_rule_enhanced
        
        rule = await create_custom_rule_enhanced()
        if rule:
            # 检查积分
            cost = rule.calculate_total_cost()
            if self.game_manager.state.fear_points >= cost:
                confirm = input(f"\\n确认花费 {cost} 恐惧积分创建此规则? (y/n): ").strip().lower()
                if confirm == 'y':
                    if self.game_manager.add_rule(rule):
                        self.game_manager.spend_fear_points(cost)
                        print("✅ 规则创建成功！")
                    else:
                        print("❌ 规则创建失败！")
            else:
                print(f"❌ 恐惧积分不足！需要 {cost}，当前只有 {self.game_manager.state.fear_points}")
        
        await asyncio.sleep(2)
    '''
    return code

if __name__ == "__main__":
    # 测试
    import asyncio
    
    async def test():
        rule = await create_custom_rule_enhanced()
        if rule:
            print(f"\n创建的规则对象: {rule}")
    
    asyncio.run(test())
