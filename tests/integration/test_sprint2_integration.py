#!/usr/bin/env python3
"""
Sprint 2 集成测试
测试地图系统、NPC移动、规则扩展和事件系统的集成
"""
import asyncio
import sys
import os
from typing import List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.map import MapManager, create_default_map, Area
from src.models.npc import NPC, generate_random_npc, NPCAction
from src.models.rule import Rule, RULE_TEMPLATES, TriggerCondition, RuleEffect, EffectType
from src.core.event_system import EventSystem, GameEvent, EventType
from src.core.dialogue_system import DialogueSystem, DialogueType, DialogueContext
from src.core.narrator import Narrator, GameEvent as NarrativeEvent, EventSeverity, NarrativeStyle


class Sprint2IntegrationTest:
    """Sprint 2 集成测试类"""
    
    def __init__(self):
        self.map_manager = None
        self.npcs = []
        self.rules = []
        self.event_system = None
        self.dialogue_system = None
        self.narrator = None
        self.current_turn = 0
        
    async def setup(self):
        """设置测试环境"""
        print("=== Sprint 2 集成测试 ===\n")
        print("初始化游戏系统...")
        
        # 创建地图
        self.map_manager = create_default_map()
        print(f"✓ 地图系统: {len(self.map_manager.areas)} 个区域")
        
        # 创建NPC
        npc_names = ["张三", "李四", "王五", "赵六"]
        for name in npc_names:
            npc = generate_random_npc(name)
            self.npcs.append(npc)
            # 将NPC放置在客厅
            self.map_manager.areas["living_room"].add_npc(npc.id)
            npc.location = "living_room"
        print(f"✓ NPC系统: {len(self.npcs)} 个NPC")
        
        # 加载规则模板
        for template_id, template in list(RULE_TEMPLATES.items())[:5]:  # 只加载前5个
            rule = Rule(
                id=template_id,
                name=template["name"],
                description=template["description"],
                trigger=TriggerCondition(**template["trigger"]),
                effect=RuleEffect(**template["effect"]),
                base_cost=template.get("base_cost", 100)
            )
            self.rules.append(rule)
        print(f"✓ 规则系统: {len(self.rules)} 条规则")
        
        # 初始化事件系统
        self.event_system = EventSystem()
        print(f"✓ 事件系统: {len(self.event_system.events)} 个事件")
        
        # 初始化AI系统
        self.dialogue_system = DialogueSystem()
        self.narrator = Narrator()
        print("✓ AI系统: 对话和叙事系统就绪")
        
        print("\n系统初始化完成！\n")
        
    async def test_map_and_movement(self):
        """测试地图和NPC移动"""
        print("【测试1: 地图和NPC移动】")
        
        # 显示初始状态
        living_room = self.map_manager.get_area("living_room")
        print(f"客厅中的NPC: {len(living_room.current_npcs)} 个")
        
        # 测试NPC移动决策
        test_npc = self.npcs[0]
        print(f"\n{test_npc.name} 正在决定移动...")
        
        # 获取可用区域
        available_areas = list(living_room.connections.values())
        destination = test_npc.choose_move_destination(
            living_room,
            available_areas,
            self.map_manager
        )
        
        if destination:
            print(f"{test_npc.name} 决定移动到: {self.map_manager.get_area(destination).name}")
            
            # 执行移动
            if self.map_manager.move_npc(test_npc.id, "living_room", destination):
                test_npc.perform_move()
                test_npc.location = destination
                print(f"✓ 移动成功! 体力消耗后: {test_npc.stamina}/100")
                
                # 进入新区域的反应
                new_area = self.map_manager.get_area(destination)
                area_properties = [p.value for p in new_area.properties]
                test_npc.enter_area(destination, area_properties)
                print(f"进入{new_area.name}后的状态: 恐惧{test_npc.fear}/100")
            else:
                print("✗ 移动失败!")
        
        # 测试寻路
        print("\n测试寻路系统:")
        path = self.map_manager.find_path("bedroom_a", "kitchen")
        if path:
            path_names = [self.map_manager.get_area(area_id).name for area_id in path]
            print(f"从卧室A到厨房的路径: {' -> '.join(path_names)}")
        
        print("\n✅ 地图和移动测试完成\n")
        
    async def test_dialogue_system(self):
        """测试对话系统"""
        print("【测试2: AI对话系统】")
        
        # 选择参与对话的NPC
        participants = self.npcs[:3]
        
        # 创建对话上下文
        context = DialogueContext(
            location="客厅",
            time="深夜",
            participants=[npc.id for npc in participants],
            recent_events=[],
            mood="tense"
        )
        
        # 生成早间对话
        print("生成早间对话...")
        dialogue_entry = await self.dialogue_system.generate_dialogue_round(
            participants,
            context,
            DialogueType.MORNING,
            self.current_turn
        )
        
        print("\n对话内容:")
        for dialogue in dialogue_entry.dialogues:
            print(f"{dialogue['speaker']}: {dialogue['text']}")
        
        # 模拟恐怖事件后的对话
        print("\n\n模拟恐怖事件后的紧急对话...")
        
        # 增加NPC恐惧
        for npc in participants:
            npc.add_fear(40)
        
        context.recent_events = [{
            "type": "strange_noise",
            "description": "浴室传来玻璃破碎的声音"
        }]
        
        emergency_dialogue = await self.dialogue_system.generate_dialogue_round(
            participants,
            context,
            DialogueType.EMERGENCY,
            self.current_turn + 1
        )
        
        print("\n紧急对话:")
        for dialogue in emergency_dialogue.dialogues:
            print(f"{dialogue['speaker']}: {dialogue['text']}")
        
        print("\n✅ 对话系统测试完成\n")
        
    async def test_event_system(self):
        """测试事件系统"""
        print("【测试3: 随机事件系统】")
        
        # 准备游戏状态
        game_state = {
            "current_turn": 8,
            "average_fear": sum(npc.fear for npc in self.npcs) / len(self.npcs),
            "alive_npcs": len([npc for npc in self.npcs if npc.hp > 0]),
            "time_of_day": "night"
        }
        
        print(f"当前游戏状态:")
        print(f"- 回合: {game_state['current_turn']}")
        print(f"- 平均恐惧: {game_state['average_fear']:.1f}")
        print(f"- 存活NPC: {game_state['alive_npcs']}")
        
        # 触发事件
        print("\n检查可能触发的事件...")
        triggered_events = self.event_system.check_and_trigger_events(game_state)
        
        if triggered_events:
            print(f"\n触发了 {len(triggered_events)} 个事件:")
            for event_result in triggered_events:
                print(f"\n事件: {event_result['event_name']}")
                if event_result['messages']:
                    print(f"描述: {event_result['messages'][0]}")
                print("效果:")
                for effect in event_result['effects_applied']:
                    print(f"  - {effect.get('description', effect['type'])}")
        else:
            print("\n没有事件被触发")
        
        print("\n✅ 事件系统测试完成\n")
        
    async def test_narrator(self):
        """测试叙事系统"""
        print("【测试4: 叙事生成系统】")
        
        # 创建一系列游戏事件
        events = []
        
        # NPC移动事件
        if len(self.npcs) > 0 and self.npcs[0].location != "living_room":
            events.append(NarrativeEvent(
                event_type="movement",
                severity=EventSeverity.MINOR,
                actors=[self.npcs[0].name],
                location=self.npcs[0].location,
                details={"from": "客厅", "to": self.npcs[0].location}
            ))
        
        # 恐惧事件
        events.append(NarrativeEvent(
            event_type="fear_spike",
            severity=EventSeverity.MODERATE,
            actors=[npc.name for npc in self.npcs if npc.fear > 50],
            location="整栋建筑",
            details={"cause": "未知的恐惧"}
        ))
        
        # 如果有触发的规则，添加规则事件
        if self.rules:
            events.append(NarrativeEvent(
                event_type="rule_created",
                severity=EventSeverity.MAJOR,
                actors=["管理者"],
                location="系统空间",
                details={"rule_name": self.rules[0].name}
            ))
        
        # 生成叙述
        print("生成本回合叙述...")
        chapter = await self.narrator.narrate_turn(
            events,
            {
                "current_turn": self.current_turn,
                "time_of_day": "night",
                "average_fear": sum(npc.fear for npc in self.npcs) / len(self.npcs)
            }
        )
        
        print(f"\n{chapter.title}")
        print("-" * 40)
        print(chapter.content)
        
        print("\n✅ 叙事系统测试完成\n")
        
    async def test_rule_integration(self):
        """测试规则系统集成"""
        print("【测试5: 规则系统集成】")
        
        # 显示已加载的规则
        print("已加载的规则:")
        for i, rule in enumerate(self.rules, 1):
            print(f"{i}. {rule.name}")
            print(f"   触发: {rule.trigger.action}")
            print(f"   效果: {rule.effect.type.value}")
        
        # 模拟规则触发
        print("\n模拟规则触发...")
        
        # 选择一个NPC和规则
        if self.npcs and self.rules:
            test_npc = self.npcs[0]
            mirror_rule = next((r for r in self.rules if r.id == "mirror_death"), None)
            
            if mirror_rule:
                print(f"\n{test_npc.name} 正在浴室...")
                
                # 检查规则是否可以触发
                context = {
                    "current_time": "01:00",
                    "actor_location": "bathroom",
                    "actor_items": ["mirror"]
                }
                
                if mirror_rule.can_trigger(context):
                    print("⚡ 规则可以触发!")
                    
                    # 应用效果
                    result = mirror_rule.apply_effect({"name": test_npc.name})
                    print(f"效果: {result}")
                    
                    # 其他NPC的反应
                    for other_npc in self.npcs[1:]:
                        other_npc.observe_event("rule_triggered", {
                            "rule_id": mirror_rule.id,
                            "victim": test_npc.name,
                            "turn": self.current_turn
                        })
                    
                    print(f"\n其他NPC的反应:")
                    for other_npc in self.npcs[1:]:
                        print(f"- {other_npc.name}: 恐惧 {other_npc.fear}/100")
                else:
                    print("规则条件不满足")
        
        print("\n✅ 规则系统集成测试完成\n")
        
    async def run_simulation(self):
        """运行一个完整的模拟回合"""
        print("【测试6: 完整回合模拟】")
        print("=" * 50)
        
        self.current_turn += 1
        print(f"\n第 {self.current_turn} 回合开始")
        
        # 1. NPC行动阶段
        print("\n[NPC行动阶段]")
        for npc in self.npcs:
            if npc.hp <= 0:
                continue
                
            # 决定行动
            current_area = self.map_manager.get_area(npc.location)
            context = {
                "nearby_npcs": [
                    other.id for other in self.npcs 
                    if other.id != npc.id and other.location == npc.location
                ],
                "current_location": npc.location
            }
            
            action = npc.decide_action(context)
            print(f"\n{npc.name} ({npc.location}) 决定: {action.value}")
            
            # 执行行动
            if action == NPCAction.MOVE:
                available_areas = list(current_area.connections.values())
                destination = npc.choose_move_destination(
                    current_area,
                    available_areas,
                    self.map_manager
                )
                if destination and self.map_manager.move_npc(npc.id, npc.location, destination):
                    npc.perform_move()
                    npc.location = destination
                    print(f"  → 移动到 {self.map_manager.get_area(destination).name}")
        
        # 2. 事件触发
        print("\n[事件阶段]")
        game_state = {
            "current_turn": self.current_turn,
            "average_fear": sum(npc.fear for npc in self.npcs) / len(self.npcs),
            "alive_npcs": len([npc for npc in self.npcs if npc.hp > 0]),
            "time_of_day": "night" if self.current_turn % 4 == 0 else "day"
        }
        
        triggered_events = self.event_system.check_and_trigger_events(game_state)
        if triggered_events:
            for event in triggered_events:
                print(f"! 触发事件: {event['event_name']}")
        
        # 3. 对话阶段（如果是固定时间）
        if self.current_turn % 4 in [1, 3]:  # 早晚对话
            print("\n[对话阶段]")
            dialogue_type = DialogueType.MORNING if self.current_turn % 4 == 1 else DialogueType.NIGHT
            
            # 按地点分组NPC
            location_groups = {}
            for npc in self.npcs:
                if npc.hp > 0:
                    if npc.location not in location_groups:
                        location_groups[npc.location] = []
                    location_groups[npc.location].append(npc)
            
            # 每个地点的NPC对话
            for location, npcs_in_location in location_groups.items():
                if len(npcs_in_location) >= 2:
                    print(f"\n在{self.map_manager.get_area(location).name}的对话:")
                    context = DialogueContext(
                        location=location,
                        time="早晨" if dialogue_type == DialogueType.MORNING else "夜晚",
                        participants=[npc.id for npc in npcs_in_location[:3]],  # 最多3人
                        recent_events=[],
                        mood="tense"
                    )
                    
                    dialogue_entry = await self.dialogue_system.generate_dialogue_round(
                        npcs_in_location[:3],
                        context,
                        dialogue_type,
                        self.current_turn
                    )
                    
                    for dialogue in dialogue_entry.dialogues[:2]:  # 只显示前2句
                        print(f"  {dialogue['speaker']}: {dialogue['text']}")
        
        # 4. 回合总结
        print("\n[回合总结]")
        print(f"存活NPC: {len([npc for npc in self.npcs if npc.hp > 0])}/{len(self.npcs)}")
        print(f"平均恐惧: {game_state['average_fear']:.1f}")
        
        # 显示每个区域的NPC分布
        print("\n区域分布:")
        for area_id, area in self.map_manager.areas.items():
            if area.current_npcs:
                npc_names = [
                    npc.name for npc in self.npcs 
                    if npc.id in area.current_npcs
                ]
                print(f"- {area.name}: {', '.join(npc_names)}")
        
        print("\n✅ 回合模拟完成\n")
        
    async def cleanup(self):
        """清理资源"""
        if self.dialogue_system:
            await self.dialogue_system.api_client.close()
        if self.narrator:
            await self.narrator.api_client.close()
        print("资源清理完成")
        
    async def run_all_tests(self):
        """运行所有测试"""
        try:
            await self.setup()
            
            # 运行各项测试
            await self.test_map_and_movement()
            await asyncio.sleep(1)
            
            await self.test_dialogue_system()
            await asyncio.sleep(1)
            
            await self.test_event_system()
            await asyncio.sleep(1)
            
            await self.test_narrator()
            await asyncio.sleep(1)
            
            await self.test_rule_integration()
            await asyncio.sleep(1)
            
            await self.run_simulation()
            
            print("\n" + "=" * 50)
            print("🎉 所有Sprint 2功能测试完成！")
            print("=" * 50)
            
        finally:
            await self.cleanup()


async def main():
    """主函数"""
    test = Sprint2IntegrationTest()
    await test.run_all_tests()


if __name__ == "__main__":
    # Windows下的事件循环策略
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
