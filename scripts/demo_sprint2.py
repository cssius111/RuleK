#!/usr/bin/env python3
"""
Sprint 2 功能演示
快速展示所有新功能的demo脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.map import create_default_map
from src.models.npc import generate_random_npc
from src.core.dialogue_system import DialogueSystem, DialogueType, DialogueContext
from src.core.narrator import Narrator, GameEvent, EventSeverity, NarrativeStyle
from src.models.event import Event, EventType


async def demo():
    """运行演示"""
    print("=" * 60)
    print("🎮 规则怪谈管理者 - Sprint 2 功能演示")
    print("=" * 60)
    
    # 1. 创建游戏世界
    print("\n📍 初始化游戏世界...")
    map_manager = create_default_map()
    print(f"✓ 创建了 {len(map_manager.areas)} 个区域的地图")
    
    # 显示地图
    print("\n🗺️ 地图结构：")
    for area_id, area in map_manager.areas.items():
        connections = [map_manager.get_area(conn_id).name for conn_id in area.connections.values()]
        print(f"  • {area.name}: 连接到 {', '.join(connections) if connections else '无'}")
    
    # 2. 创建NPC
    print("\n👥 创建NPC...")
    npcs = []
    names = ["小明", "小红", "老王"]
    for name in names:
        npc = generate_random_npc(name)
        npcs.append(npc)
        map_manager.areas["living_room"].add_npc(npc.id)
        npc.location = "living_room"
        print(f"✓ {npc.name} - 理性:{npc.personality.rationality} 勇气:{npc.personality.courage}")
    
    # 3. 展示NPC移动决策
    print("\n🚶 NPC移动决策演示...")
    test_npc = npcs[0]
    available_areas = list(map_manager.areas["living_room"].connections.values())
    destination = test_npc.choose_move_destination(
        map_manager.areas["living_room"],
        available_areas,
        map_manager
    )
    if destination:
        print(f"{test_npc.name} 想要移动到: {map_manager.get_area(destination).name}")
    
    # 4. AI对话演示
    print("\n💬 AI对话系统演示...")
    dialogue_system = DialogueSystem()
    
    # 增加一些恐惧值使对话更有趣
    npcs[0].add_fear(50)
    npcs[1].add_fear(30)
    
    context = DialogueContext(
        location="客厅",
        time="深夜",
        participants=[npc.id for npc in npcs],
        recent_events=[{"type": "strange_noise", "description": "楼上传来脚步声"}],
        mood="fearful"
    )
    
    dialogue_entry = await dialogue_system.generate_dialogue_round(
        npcs, context, DialogueType.EMERGENCY, 1
    )
    
    print("生成的对话：")
    for dialogue in dialogue_entry.dialogues:
        print(f"  {dialogue['speaker']}: {dialogue['text']}")
    
    # 5. 事件记录演示
    print("\n⚡ 事件记录演示...")
    game_state = {
        "current_turn": 5,
        "average_fear": 40,
        "alive_npcs": 3,
        "time_of_day": "night"
    }
    demo_event = Event(
        type=EventType.SYSTEM,
        description="一阵冷风吹过，门自行关闭",
        turn=game_state["current_turn"],
    )
    events_log = [demo_event]
    for evt in events_log:
        print(f"触发事件: {evt.description}")
    
    # 6. 叙事生成演示
    print("\n📖 叙事生成演示...")
    narrator = Narrator()
    narrator.set_style(NarrativeStyle.HORROR)
    
    # 创建一些游戏事件
    events = [
        GameEvent(
            event_type="movement",
            severity=EventSeverity.MINOR,
            actors=[npcs[0].name],
            location="走廊",
            details={"action": "investigating"}
        ),
        GameEvent(
            event_type="discovery",
            severity=EventSeverity.MAJOR,
            actors=[npcs[1].name],
            location="浴室",
            details={"item": "一面破碎的镜子，上面写着血字"}
        )
    ]
    
    chapter = await narrator.narrate_turn(events, game_state)
    print(f"\n章节: {chapter.title}")
    print("-" * 40)
    print(chapter.content)
    
    # 7. 规则预览
    print("\n📜 新规则预览...")
    from src.models.rule import RULE_TEMPLATES
    
    print("部分新增规则：")
    new_rules = ["phone_ring_death", "shadow_mimic", "chain_reaction"]
    for rule_id in new_rules:
        if rule_id in RULE_TEMPLATES:
            rule = RULE_TEMPLATES[rule_id]
            print(f"  • {rule['name']}: {rule['description'][:50]}...")
    
    # 清理
    await dialogue_system.api_client.close()
    await narrator.api_client.close()
    
    print("\n" + "=" * 60)
    print("✅ Sprint 2 功能演示完成！")
    print("\n💡 提示：")
    print("1. 运行 'python main_game_v2.py' 体验完整游戏")
    print("2. 运行 'python test_sprint2_integration.py' 查看更详细的测试")
    print("3. 查看 SPRINT_3_PLAN.md 了解Web UI开发计划")
    print("=" * 60)


if __name__ == "__main__":
    # Windows下的事件循环策略
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 运行演示
    asyncio.run(demo())
