"""
叙事生成器
生成恐怖氛围的游戏叙事
"""
from typing import List, Dict, Any, Optional
import random


class Narrator:
    """叙事生成器"""
    
    def __init__(self, deepseek_client=None):
        self.deepseek_client = deepseek_client
        self.narrative_templates = {
            "npc_action": [
                "{npc}小心翼翼地{action}，空气中弥漫着不祥的气息。",
                "在昏暗的{location}中，{npc}{action}，似乎有什么在暗中窥视。",
                "{npc}的身影在{location}中{action}，留下了一串不安的回响。"
            ],
            "rule_triggered": [
                "规则的力量开始显现，{rule}被触发了，恐怖笼罩着整个空间。",
                "违背了禁忌，{rule}的诅咒降临，无人能够逃脱。",
                "古老的规则被打破，{rule}带来了不可名状的恐惧。"
            ],
            "dialogue": [
                "在压抑的氛围中，{participants}交换着不安的眼神。",
                "{participants}的对话在空荡的房间里回响，每个字都充满了恐惧。",
                "颤抖的声音中，{participants}试图寻找一丝希望。"
            ],
            "time_change": {
                "morning": "晨光透过破碎的窗户，却无法驱散笼罩的阴霾。",
                "afternoon": "午后的阳光显得格外苍白，仿佛被什么吸走了生机。",
                "evening": "夜幕降临，黑暗中潜伏着未知的恐怖。",
                "night": "深夜的寂静被诡异的声响打破，恐惧在每个角落蔓延。"
            }
        }
    
    async def generate_narrative(self, events: List[Dict[str, Any]], game_state: Any) -> str:
        """生成叙事文本"""
        if self.deepseek_client:
            # 使用AI生成叙事
            try:
                # 准备事件描述
                event_descriptions = []
                for event in events:
                    event_type = event.get("type", "unknown")
                    if event_type == "npc_action":
                        desc = f"{event.get('npc', '某人')}在{event.get('location', '某处')}{event.get('action', '做了什么')}"
                    elif event_type == "rule_triggered":
                        desc = f"规则'{event.get('rule', '未知规则')}'被触发，{event.get('result', {}).get('description', '产生了恐怖的后果')}"
                    elif event_type == "dialogue":
                        participants = event.get('participants', [])
                        desc = f"{' 和 '.join(participants)}进行了一段对话"
                    else:
                        desc = event.get('description', '发生了一些事情')
                    event_descriptions.append(desc)
                
                # 调用AI生成叙事
                narrative = await self.deepseek_client.generate_narrative_text(
                    events=event_descriptions,
                    time_of_day=game_state.time_of_day,
                    min_len=200,
                )
                return narrative
            except Exception as e:
                # 如果AI失败，使用模板生成
                pass
        
        # 使用模板生成叙事
        narrative_parts = []
        
        # 添加时间描述
        time_desc = self.narrative_templates["time_change"].get(
            game_state.time_of_day,
            "时间在恐惧中流逝。"
        )
        narrative_parts.append(time_desc)
        
        # 处理每个事件
        for event in events[-3:]:  # 只处理最近3个事件
            event_type = event.get("type", "unknown")
            
            if event_type == "npc_action":
                template = random.choice(self.narrative_templates["npc_action"])
                text = template.format(
                    npc=event.get("npc", "某人"),
                    action=event.get("action", "移动"),
                    location=event.get("location", "未知地点")
                )
                narrative_parts.append(text)
                
            elif event_type == "rule_triggered":
                template = random.choice(self.narrative_templates["rule_triggered"])
                text = template.format(
                    rule=event.get("rule", "未知规则")
                )
                narrative_parts.append(text)
                
            elif event_type == "dialogue":
                template = random.choice(self.narrative_templates["dialogue"])
                participants = event.get("participants", ["某些人"])
                text = template.format(
                    participants="和".join(participants)
                )
                narrative_parts.append(text)
        
        # 组合叙事
        narrative = " ".join(narrative_parts)
        
        # 添加氛围描述
        if game_state.fear_points > 500:
            narrative += " 恐惧已经达到了临界点，整个空间都在颤抖。"
        
        return narrative
