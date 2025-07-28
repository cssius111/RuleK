#!/usr/bin/env python3
"""
Sprint 2 功能测试 - 测试AI对话和叙事系统
"""
import pytest
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from src.api.deepseek_client import DeepSeekClient, APIConfig
from src.core.dialogue_system import DialogueSystem
from src.core.narrator import Narrator, GameEvent, EventSeverity, NarrativeStyle
from src.models.npc import generate_random_npc


@pytest.mark.asyncio
async def test_api_client():
    """测试API客户端"""
    # 创建Mock模式客户端
    config = APIConfig(mock_mode=True)
    client = DeepSeekClient(config)
    
    # 测试对话生成
    npc_states = [
        {"name": "小明", "fear": 60, "sanity": 70, "status": "frightened"},
        {"name": "小红", "fear": 40, "sanity": 85, "status": "normal"}
    ]
    
    scene_context = {
        "location": "废弃浴室",
        "time": "午夜",
        "recent_events": "刚才镜子里出现了诡异的影子"
    }
    
    dialogues = await client.generate_dialogue(npc_states, scene_context)
    assert isinstance(dialogues, list)
    assert len(dialogues) > 0
    assert all('speaker' in d and 'text' in d for d in dialogues)
    
    # 测试规则评估
    rule_draft = {
        "name": "回头杀",
        "trigger": {"action": "turn_around", "conditions": ["alone"]},
        "effect": {"type": "instant_death"}
    }
    
    evaluation = await client.evaluate_rule(rule_draft, {"rule_count": 3})
    assert 'cost_estimate' in evaluation
    assert 'difficulty' in evaluation
    
    # 测试叙事生成
    events = [
        {"type": "rule_triggered", "description": "小明触发了镜中恶魔规则"},
        {"type": "npc_death", "description": "小明被拖入镜中消失"}
    ]
    
    narration = await client.narrate_events(events)
    assert isinstance(narration, str)
    assert len(narration) > 0
    
    await client.close()


@pytest.mark.asyncio
async def test_dialogue_system():
    """测试对话系统"""
    # 创建测试NPC
    npcs = [
        generate_random_npc("测试员A"),
        generate_random_npc("测试员B"),
        generate_random_npc("测试员C")
    ]
    
    # 设置一些状态
    npcs[0].add_fear(70)
    npcs[1].memory.remember_rule("mirror_death")
    
    # 创建对话系统
    dialogue_system = DialogueSystem()
    
    # 测试早间对话
    context = DialogueContext(
        location="测试地点",
        time="测试时间",
        participants=[npc.id for npc in npcs],
        recent_events=[],
        mood="tense"
    )
    
    entry = await dialogue_system.generate_dialogue_round(
        npcs, context, DialogueType.MORNING, 1
    )
    
    assert entry is not None
    assert len(entry.dialogues) > 0
    assert entry.turn == 1
    assert entry.dialogue_type == DialogueType.MORNING
    
    await dialogue_system.api_client.close()


@pytest.mark.asyncio
async def test_narrator():
    """测试叙事生成器"""
    narrator = Narrator()
    
    # 创建测试事件
    events = [
        GameEvent(
            event_type="discovery",
            severity=EventSeverity.MODERATE,
            actors=["测试员A"],
            location="测试浴室",
            details={"item": "神秘的日记本"}
        ),
        GameEvent(
            event_type="npc_death",
            severity=EventSeverity.CRITICAL,
            actors=["测试员B"],
            location="测试浴室",
            details={"victim": "测试员B", "cause": "未知诅咒"}
        )
    ]
    
    chapter = await narrator.narrate_turn(
        events,
        {
            "current_turn": 1,
            "time_of_day": "night",
            "average_fear": 65
        }
    )
    
    assert chapter is not None
    assert hasattr(chapter, 'title')
    assert hasattr(chapter, 'content')
    assert len(chapter.content) > 0
    
    await narrator.api_client.close()


@pytest.mark.asyncio
async def test_integration():
    """集成测试：模拟一个简单的游戏场景"""
    # 初始化系统
    api_client = DeepSeekClient(APIConfig(mock_mode=True))
    dialogue_system = DialogueSystem(api_client)
    narrator = Narrator(api_client)
    
    # 创建NPC
    npcs = [
        generate_random_npc("张三"),
        generate_random_npc("李四"),
        generate_random_npc("王五")
    ]
    
    # 第一回合：早间对话
    context = DialogueContext(
        location="客厅",
        time="早晨",
        participants=[npc.id for npc in npcs],
        mood="nervous"
    )
    
    dialogue_entry = await dialogue_system.generate_dialogue_round(
        npcs, context, DialogueType.MORNING, 1
    )
    
    assert dialogue_entry is not None
    assert len(dialogue_entry.dialogues) > 0
    
    # 发生事件
    npcs[0].memory.remember_rule("mirror_death")
    npcs[0].add_fear(30)
    
    discovery_event = GameEvent(
        event_type="discovery",
        severity=EventSeverity.MAJOR,
        actors=["张三"],
        location="浴室",
        details={"item": "写着血字的镜子"}
    )
    
    # 生成发现对话
    context.discovered_clues = ["午夜不要照镜子"]
    discovery_dialogue = await dialogue_system.generate_dialogue_round(
        npcs, context, DialogueType.DISCOVERY, 2
    )
    
    assert discovery_dialogue is not None
    assert discovery_dialogue.dialogue_type == DialogueType.DISCOVERY
    
    # 死亡事件
    death_event = GameEvent(
        event_type="npc_death",
        severity=EventSeverity.CRITICAL,
        actors=["李四"],
        location="浴室",
        details={"victim": "李四", "cause": "镜中恶魔"}
    )
    
    # 生成叙述
    chapter = await narrator.narrate_turn(
        [discovery_event, death_event],
        {"current_turn": 3, "time_of_day": "midnight"}
    )
    
    assert chapter is not None
    assert len(chapter.content) > 0
    
    await api_client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
