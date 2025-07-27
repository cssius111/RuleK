"""
游戏叙事生成器
将游戏事件转化为小说化的叙述
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import random
import logging

from src.api.deepseek_client import DeepSeekClient, APIConfig

logger = logging.getLogger(__name__)


class NarrativeStyle(str, Enum):
    """叙事风格枚举"""
    HORROR = "horror"              # 恐怖
    SUSPENSE = "suspense"          # 悬疑
    DARK_HUMOR = "dark_humor"      # 黑色幽默
    PSYCHOLOGICAL = "psychological" # 心理惊悚
    GOTHIC = "gothic"              # 哥特式


class EventSeverity(str, Enum):
    """事件严重程度"""
    MINOR = "minor"        # 轻微（如物品移动）
    MODERATE = "moderate"  # 中等（如NPC受伤）
    MAJOR = "major"        # 重大（如触发规则）
    CRITICAL = "critical"  # 危急（如NPC死亡）


@dataclass
class GameEvent:
    """游戏事件"""
    event_type: str
    severity: EventSeverity
    actors: List[str]  # 涉及的NPC
    location: str
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_description(self) -> str:
        """转换为事件描述"""
        desc = f"{self.event_type}"
        
        if self.event_type == "npc_death":
            victim = self.details.get("victim", "某人")
            cause = self.details.get("cause", "未知原因")
            desc = f"{victim}因{cause}死亡"
            
        elif self.event_type == "rule_triggered":
            rule_name = self.details.get("rule_name", "未知规则")
            actor = self.actors[0] if self.actors else "某人"
            desc = f"{actor}触发了{rule_name}"
            
        elif self.event_type == "discovery":
            item = self.details.get("item", "某物")
            discoverer = self.actors[0] if self.actors else "某人"
            desc = f"{discoverer}发现了{item}"
            
        elif self.event_type == "fear_spike":
            desc = f"恐慌在{self.location}蔓延"
            
        return desc


@dataclass
class Chapter:
    """章节"""
    number: int
    title: str
    content: str
    events: List[GameEvent]
    style: NarrativeStyle
    word_count: int = 0
    
    def __post_init__(self):
        self.word_count = len(self.content)


class NarrativeTemplate:
    """叙事模板"""
    
    def __init__(self):
        self.templates = self._init_templates()
    
    def _init_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """初始化叙事模板"""
        return {
            NarrativeStyle.HORROR: {
                "opening": [
                    "夜幕如同黑色的帷幕缓缓降下，将整个{location}笼罩在不祥的阴影中。",
                    "寂静得可怕的{location}里，只有时钟的滴答声在提醒着时间的流逝。",
                    "空气中弥漫着一股难以名状的腐臭，仿佛死亡正在某个角落静静等待。"
                ],
                "death": [
                    "{victim}的惨叫声撕裂了夜空，随即一切归于死寂。",
                    "当其他人赶到时，只看到{victim}扭曲的尸体和墙上渗出的血迹。",
                    "没有人看清发生了什么，{victim}就这样永远地消失在了黑暗中。"
                ],
                "discovery": [
                    "{actor}颤抖着拿起{item}，上面沾满了已经干涸的血迹。",
                    "在{location}的角落里，{actor}发现了不应该存在的{item}。",
                    "{item}静静地躺在那里，仿佛在诉说着某个可怕的秘密。"
                ],
                "atmosphere": [
                    "温度骤然下降，每个人都能看到自己呼出的白雾。",
                    "墙壁上的影子似乎有了生命，在烛光中扭曲舞动。",
                    "一阵腐朽的气息从走廊深处飘来，让人作呕。"
                ]
            },
            NarrativeStyle.SUSPENSE: {
                "opening": [
                    "一切看似平静，但{location}里的每个人都感觉到了异常。",
                    "表面的宁静下，暗流涌动，危机一触即发。",
                    "他们还不知道，真正的恐怖才刚刚开始。"
                ],
                "death": [
                    "{victim}消失了，只留下一地的疑问和恐惧。",
                    "当{victim}的尸体被发现时，所有的线索都指向了一个可怕的真相。",
                    "没有人愿意相信{victim}已经死了，直到那个令人窒息的证据出现。"
                ],
                "discovery": [
                    "{actor}盯着手中的{item}，一个可怕的推理在脑海中成形。",
                    "这个{item}的出现，让整个谜团又增加了一层迷雾。",
                    "{actor}意识到，{item}可能是解开这一切的关键。"
                ]
            },
            NarrativeStyle.DARK_HUMOR: {
                "opening": [
                    "又是一个'美好'的夜晚，至少对于还活着的人来说是这样。",
                    "在这个{location}里，死亡变成了一种黑色的玩笑。",
                    "如果这是一场游戏，那么规则制定者一定有着扭曲的幽默感。"
                ],
                "death": [
                    "{victim}以一种极其荒诞的方式告别了这个世界。",
                    "讽刺的是，{victim}刚刚还在说'这里很安全'。",
                    "死神今天的收获是{victim}，明天的菜单上又会是谁呢？"
                ]
            }
        }
    
    def get_template(self, style: NarrativeStyle, template_type: str) -> str:
        """获取模板"""
        templates = self.templates.get(style, {}).get(template_type, [""])
        return random.choice(templates) if templates else ""


class Narrator:
    """叙事生成器"""
    
    def __init__(self, api_client: Optional[DeepSeekClient] = None):
        self.api_client = api_client or DeepSeekClient(APIConfig(mock_mode=True))
        self.templates = NarrativeTemplate()
        self.chapter_count = 0
        self.current_style = NarrativeStyle.HORROR
        
    async def narrate_turn(
        self,
        events: List[GameEvent],
        game_state: Dict[str, Any],
        style: Optional[NarrativeStyle] = None
    ) -> Chapter:
        """
        为一个回合生成叙述
        
        Args:
            events: 本回合发生的事件列表
            game_state: 游戏状态
            style: 叙事风格（可选）
            
        Returns:
            章节对象
        """
        if style:
            self.current_style = style
        
        self.chapter_count += 1
        
        # 生成章节标题
        title = self._generate_chapter_title(events, self.chapter_count)
        
        # 根据事件严重程度决定叙述详细度
        if not events:
            # 没有事件时的过渡叙述
            content = await self._generate_transition_narrative(game_state)
        else:
            # 对事件进行排序和分组
            grouped_events = self._group_events(events)
            
            # 生成叙述
            if self._should_use_api(grouped_events):
                content = await self._generate_api_narrative(grouped_events, game_state)
            else:
                content = self._generate_template_narrative(grouped_events, game_state)
        
        return Chapter(
            number=self.chapter_count,
            title=title,
            content=content,
            events=events,
            style=self.current_style
        )
    
    def _generate_chapter_title(self, events: List[GameEvent], chapter_num: int) -> str:
        """生成章节标题"""
        if not events:
            return f"第{chapter_num}章：暴风雨前的宁静"
        
        # 根据最重要的事件生成标题
        critical_events = [e for e in events if e.severity == EventSeverity.CRITICAL]
        if critical_events:
            event = critical_events[0]
            if event.event_type == "npc_death":
                victim = event.details.get("victim", "某人")
                return f"第{chapter_num}章：{victim}的终章"
            elif event.event_type == "rule_triggered":
                return f"第{chapter_num}章：规则的制裁"
        
        major_events = [e for e in events if e.severity == EventSeverity.MAJOR]
        if major_events:
            return f"第{chapter_num}章：真相渐显"
        
        return f"第{chapter_num}章：暗流涌动"
    
    def _group_events(self, events: List[GameEvent]) -> Dict[str, List[GameEvent]]:
        """将事件按类型和地点分组"""
        grouped = {}
        
        for event in events:
            key = f"{event.location}_{event.event_type}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(event)
        
        return grouped
    
    def _should_use_api(self, grouped_events: Dict[str, List[GameEvent]]) -> bool:
        """判断是否需要使用API生成"""
        # 如果有重大事件或事件较复杂，使用API
        total_events = sum(len(events) for events in grouped_events.values())
        has_critical = any(
            event.severity == EventSeverity.CRITICAL 
            for events in grouped_events.values() 
            for event in events
        )
        
        return has_critical or total_events > 3
    
    async def _generate_api_narrative(
        self,
        grouped_events: Dict[str, List[GameEvent]],
        game_state: Dict[str, Any]
    ) -> str:
        """使用API生成叙述"""
        # 准备事件描述
        events_data = []
        for location_type, events in grouped_events.items():
            for event in events:
                events_data.append({
                    "type": event.event_type,
                    "description": event.to_description(),
                    "location": event.location,
                    "severity": event.severity.value
                })
        
        try:
            narrative = await self.api_client.narrate_events(
                events_data,
                self.current_style.value
            )
            
            # 添加章节过渡
            time_of_day = game_state.get("time_of_day", "night")
            if time_of_day == "night":
                narrative = self._add_night_atmosphere(narrative)
            
            return narrative
            
        except Exception as e:
            logger.error(f"Failed to generate narrative via API: {e}")
            # 降级到模板生成
            return self._generate_template_narrative(grouped_events, game_state)
    
    def _generate_template_narrative(
        self,
        grouped_events: Dict[str, List[GameEvent]],
        game_state: Dict[str, Any]
    ) -> str:
        """使用模板生成叙述"""
        paragraphs = []
        
        # 开场描述
        if grouped_events:
            first_location = list(grouped_events.values())[0][0].location
            opening = self.templates.get_template(self.current_style, "opening")
            if opening:
                paragraphs.append(opening.format(location=first_location))
        
        # 按严重程度排序事件
        all_events = []
        for events in grouped_events.values():
            all_events.extend(events)
        all_events.sort(key=lambda e: ["minor", "moderate", "major", "critical"].index(e.severity.value))
        
        # 为每个事件生成叙述
        for event in all_events:
            if event.event_type == "npc_death":
                template = self.templates.get_template(self.current_style, "death")
                if template:
                    text = template.format(
                        victim=event.details.get("victim", "某人"),
                        location=event.location
                    )
                    paragraphs.append(text)
            
            elif event.event_type == "discovery":
                template = self.templates.get_template(self.current_style, "discovery")
                if template:
                    text = template.format(
                        actor=event.actors[0] if event.actors else "某人",
                        item=event.details.get("item", "某物"),
                        location=event.location
                    )
                    paragraphs.append(text)
        
        # 添加氛围描述
        if len(paragraphs) < 3 and self.current_style == NarrativeStyle.HORROR:
            atmosphere = self.templates.get_template(self.current_style, "atmosphere")
            if atmosphere:
                paragraphs.append(atmosphere)
        
        return "\n\n".join(paragraphs)
    
    async def _generate_transition_narrative(self, game_state: Dict[str, Any]) -> str:
        """生成过渡叙述（无事件时）"""
        time_of_day = game_state.get("time_of_day", "night")
        fear_level = game_state.get("average_fear", 0)
        
        if time_of_day == "morning":
            if fear_level < 30:
                return "清晨的阳光透过破碎的窗户洒进来，给这个诡异的地方带来了一丝虚假的安全感。幸存者们开始新一天的挣扎。"
            else:
                return "又一个不眠之夜过去了。疲惫的幸存者们面面相觑，每个人眼中都写满了恐惧和不信任。"
        
        elif time_of_day == "night":
            if fear_level < 50:
                return "夜幕降临，阴影开始在角落里聚集。虽然暂时平静，但每个人都知道，真正的考验即将开始。"
            else:
                return "黑暗如潮水般涌来，吞噬了最后一丝光明。在这个充满恶意的夜晚，没有人敢独自行动。"
        
        return "时间在恐惧中缓慢流逝，每一秒都可能是某人生命的最后时刻。"
    
    def _add_night_atmosphere(self, narrative: str) -> str:
        """添加夜晚氛围"""
        night_elements = [
            "月光透过破碎的窗户洒下诡异的光影。",
            "远处传来不明的声响，像是某种生物在暗中窥视。",
            "寒意渗透进每个人的骨髓，这不仅仅是因为温度。"
        ]
        
        # 随机选择一个元素添加到叙述中
        element = random.choice(night_elements)
        return f"{narrative}\n\n{element}"
    
    def set_style(self, style: NarrativeStyle):
        """设置叙事风格"""
        self.current_style = style
        logger.info(f"Narrative style changed to: {style.value}")
    
    async def generate_summary(
        self,
        chapters: List[Chapter],
        max_words: int = 500
    ) -> str:
        """生成游戏总结"""
        if not chapters:
            return "这是一个还未开始的故事..."
        
        # 统计信息
        total_deaths = sum(
            1 for chapter in chapters 
            for event in chapter.events 
            if event.event_type == "npc_death"
        )
        
        total_discoveries = sum(
            1 for chapter in chapters 
            for event in chapter.events 
            if event.event_type == "discovery"
        )
        
        # 生成总结
        summary = f"""经过{len(chapters)}个章节的惊心动魄，这个恐怖故事暂时告一段落。

在这场噩梦中：
- {total_deaths}人失去了生命
- {total_discoveries}个重要线索被发现
- 幸存者们经历了难以想象的恐惧

最终，{"没有人能够逃脱" if total_deaths > 3 else "一些人幸运地活了下来"}。

但这真的是结束吗？还是另一个开始？"""
        
        return summary


# 测试代码
if __name__ == "__main__":
    async def test_narrator():
        # 创建叙事器
        narrator = Narrator()
        
        # 创建测试事件
        events = [
            GameEvent(
                event_type="discovery",
                severity=EventSeverity.MODERATE,
                actors=["小明"],
                location="废弃浴室",
                details={"item": "沾血的镜子碎片"}
            ),
            GameEvent(
                event_type="rule_triggered",
                severity=EventSeverity.MAJOR,
                actors=["小红"],
                location="浴室",
                details={"rule_name": "镜中恶魔", "result": "escape"}
            ),
            GameEvent(
                event_type="npc_death",
                severity=EventSeverity.CRITICAL,
                actors=["张三"],
                location="浴室",
                details={"victim": "张三", "cause": "镜中恶魔规则"}
            )
        ]
        
        # 游戏状态
        game_state = {
            "current_turn": 5,
            "time_of_day": "night",
            "average_fear": 65
        }
        
        # 生成叙述
        print("=== 恐怖风格叙述 ===")
        chapter1 = await narrator.narrate_turn(events, game_state, NarrativeStyle.HORROR)
        print(f"{chapter1.title}")
        print(chapter1.content)
        
        # 切换风格
        print("\n=== 悬疑风格叙述 ===")
        chapter2 = await narrator.narrate_turn(events[:-1], game_state, NarrativeStyle.SUSPENSE)
        print(f"{chapter2.title}")
        print(chapter2.content)
        
        # 生成过渡叙述
        print("\n=== 过渡叙述 ===")
        chapter3 = await narrator.narrate_turn([], game_state)
        print(f"{chapter3.title}")
        print(chapter3.content)
        
        # 生成总结
        print("\n=== 游戏总结 ===")
        summary = await narrator.generate_summary([chapter1, chapter2, chapter3])
        print(summary)
        
        # 关闭API客户端
        await narrator.api_client.close()
    
    # 运行测试
    asyncio.run(test_narrator())
