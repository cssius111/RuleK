"""
AI Prompt 模板管理
支持中英文切换和动态参数注入
"""
from jinja2 import Environment, BaseLoader
from typing import List, Dict, Any, Tuple, Optional


# ========== System Prompts ==========

TURN_PLAN_SYSTEM = """你是一个恐怖生存游戏的"导演兼规则仲裁者"。你的任务是：
1. 根据NPC的性格、状态和当前场景，用中文生成他们之间的真实对话（每人1~2句话）。
2. 对话应该反映每个NPC的恐惧程度、理智值、性格特征和最近发生的事件。
3. 在对话结束后，为每个NPC制定本回合的行动计划。
4. 行动计划要考虑：性格驱动、生存本能、规则约束、团队协作。
5. 严格按照指定的JSON Schema格式输出，不要输出其他内容。
6. 如果无法满足要求，返回包含 "error" 字段的JSON说明问题。

记住：
- 营造恐怖紧张的氛围
- 让NPC的行为符合其性格设定
- 考虑已激活规则的影响
- 平衡生存与探索的需求"""

NARRATIVE_SYSTEM = """你是一位恐怖小说作家，擅长将游戏事件转化为引人入胜的恐怖叙事。要求：
1. 使用第三人称视角，写出200-300字的中文叙事段落。
2. 保持恐怖/悬疑的氛围，运用环境描写和心理描写增强紧张感。
3. 确保叙事逻辑连贯，事件之间有合理的因果关系。
4. 避免提及"游戏"、"规则"、"系统"等破坏沉浸感的元词汇。
5. 如果输入信息不足，返回包含 "error" 字段的响应。

风格要点：
- 使用感官描写增强代入感
- 适当留白，让读者自行想象
- 节奏张弛有度
- 结尾留有悬念"""

RULE_EVAL_SYSTEM = """你是恐怖游戏的规则设计专家。你需要：
1. 将玩家的自然语言规则描述解析为结构化的游戏规则。
2. 评估规则的平衡性，估算合理的消耗成本（50-500恐惧点）。
3. 设定适当的难度等级（1-10）。
4. 找出规则可能的漏洞或破解方法（至少2个）。
5. 提供改进建议，让规则更有趣、更平衡。
6. 严格遵守JSON Schema格式输出。

评估原则：
- 有趣性：规则是否能创造紧张刺激的游戏体验
- 平衡性：成本与效果是否匹配
- 可破解性：是否存在合理的应对策略
- 主题契合：是否符合恐怖游戏的氛围"""


# ========== User Prompt Templates ==========

TURN_PLAN_USER = """【当前场景信息】
时间：{{ time_of_day }}
地点：{{ location }}
环境恐惧等级：{{ ambient_fear }}/100

【最近发生的事件】（按时间顺序，最多显示3条）
{% for event in recent_events %}
- {{ event }}
{% endfor %}

【存活NPC状态】
{% for npc in npcs %}
{{ loop.index }}. {{ npc.name }}
   - 恐惧值：{{ npc.fear }}/100 | 理智值：{{ npc.sanity }}/100 | 生命值：{{ npc.hp }}/100
   - 性格特征：{{ npc.traits|join("、") }}
   - 当前状态：{{ npc.status }}
   - 所在位置：{{ npc.location }}
   {% if npc.inventory %}
   - 持有物品：{{ npc.inventory|join("、") }}
   {% endif %}
{% endfor %}

【可用地点】
{{ available_places|join("、") }}

【当前激活的规则】（影响NPC行为决策）
{% for rule in active_rules %}
- {{ rule }}
{% endfor %}

【特殊条件】
{% for condition in special_conditions %}
- {{ condition }}
{% endfor %}

【输出要求】
请生成本回合的对话和行动计划，严格按照以下JSON格式输出：

```json
{
  "dialogue": [
    {
      "speaker": "NPC名字",
      "text": "对话内容",
      "emotion": "fear/calm/panic/suspicious/angry"
    }
  ],
  "actions": [
    {
      "npc": "NPC名字",
      "action": "move/search/talk/use_item/wait/defend/investigate/hide/run/custom",
      "target": "目标地点或对象（可选）",
      "reason": "选择该行动的理由",
      "risk": "可能面临的风险（可选）",
      "priority": "high/medium/low"
    }
  ],
  "atmosphere": "本回合的整体氛围描述（可选）"
}
```

注意事项：
- 每个NPC本回合只能执行一个主要行动
- 对话要体现NPC的性格和当前心理状态
- 行动选择要合理，考虑生存和探索的平衡
- 不要让所有NPC都选择相同的行动"""

NARRATIVE_USER = """【时间段】{{ time_of_day }}

【本回合发生的事件】（按时间顺序）
{% for event in events %}
{{ loop.index }}. {{ event }}
{% endfor %}

【当前场景氛围】
- 环境恐惧等级：{{ ambient_fear }}/100
- 存活人数：{{ survivor_count }}
- 特殊状况：{{ special_conditions|join("、") if special_conditions else "无" }}

【写作要求】
1. 将上述事件编织成一段200-300字的恐怖叙事
2. 使用第三人称视角
3. 注重氛围营造和心理描写
4. 保持叙事的连贯性和逻辑性
5. 结尾留有悬念或不安感

请直接输出叙事文本，不要有任何其他说明。"""

RULE_EVAL_USER = """【玩家提出的规则】
"{{ rule_nl }}"

【当前游戏状态】
- 已有规则数量：{{ rule_count }}
- 平均恐惧值：{{ avg_fear }}/100
- 可用地点：{{ places|join("、") }}
- 游戏难度：{{ difficulty }}

【评估要求】
请将上述自然语言规则解析并评估，输出以下JSON格式：

```json
{
  "name": "规则名称（简洁有力）",
  "trigger": {
    "type": "action/time/location/dialogue/event/compound",
    "conditions": ["触发条件1", "触发条件2"],
    "probability": 0.8
  },
  "effect": {
    "type": "instant_death/damage/fear_gain/teleport/transform/summon/custom",
    "params": {
      "参数名": "参数值"
    },
    "description": "效果的详细描述"
  },
  "cooldown": 0,
  "cost": 100,
  "difficulty": 5,
  "loopholes": ["破解方法1", "破解方法2"],
  "suggestion": "如何改进这个规则的建议"
}
```

评估标准：
- cost: 50-500之间，根据规则威力评估
- difficulty: 1-10，表示规则的复杂度和破解难度
- loopholes: 至少提供2个合理的破解方法
- 确保规则有趣且平衡"""


# ========== Prompt Manager ==========

class PromptManager:
    """Prompt模板管理器"""
    
    def __init__(self, language: str = "zh"):
        """
        初始化Prompt管理器
        
        Args:
            language: 语言设置，目前支持 "zh"（中文）
        """
        self.language = language
        self.env = Environment(loader=BaseLoader())

    def validate_json_response(self, text: str, schema_name: str):
        """Basic JSON response validator used in tests."""
        import json
        try:
            return True, json.loads(text), None
        except Exception as e:
            return False, None, str(e)
        
    def build_turn_plan_prompt(
        self,
        npcs: List[Dict[str, Any]],
        time_of_day: str,
        location: str,
        recent_events: List[str],
        available_places: List[str],
        active_rules: Optional[List[str]] = None,
        special_conditions: Optional[List[str]] = None,
        ambient_fear: int = 50
    ) -> Tuple[str, str]:
        """
        构建回合计划的prompt
        
        Returns:
            (system_prompt, user_prompt) 元组
        """
        # 时间映射
        time_map = {
            "morning": "清晨",
            "afternoon": "下午", 
            "evening": "傍晚",
            "night": "深夜"
        }
        
        template = self.env.from_string(TURN_PLAN_USER)
        user_prompt = template.render(
            npcs=npcs,
            time_of_day=time_map.get(time_of_day, time_of_day),
            location=location,
            recent_events=recent_events[-3:] if recent_events else [],  # 只取最近3条
            available_places=available_places,
            active_rules=active_rules or [],
            special_conditions=special_conditions or [],
            ambient_fear=ambient_fear
        )
        
        return TURN_PLAN_SYSTEM, user_prompt
    
    def build_narrative_prompt(
        self,
        events: List[str],
        time_of_day: str,
        survivor_count: int,
        ambient_fear: int = 50,
        special_conditions: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """
        构建叙事生成的prompt
        
        Returns:
            (system_prompt, user_prompt) 元组
        """
        time_map = {
            "morning": "清晨",
            "afternoon": "下午",
            "evening": "傍晚", 
            "night": "深夜"
        }
        
        template = self.env.from_string(NARRATIVE_USER)
        user_prompt = template.render(
            events=events,
            time_of_day=time_map.get(time_of_day, time_of_day),
            survivor_count=survivor_count,
            ambient_fear=ambient_fear,
            special_conditions=special_conditions or []
        )
        
        return NARRATIVE_SYSTEM, user_prompt
    
    def build_rule_eval_prompt(
        self,
        rule_draft: Dict[str, Any],
        world_ctx: Dict[str, Any],
        *,
        difficulty_level: str | None = None,
    ) -> str:
        """构建规则评估的用户提示字符串"""

        template = self.env.from_string(RULE_EVAL_USER)
        user_prompt = template.render(
            rule_nl=rule_draft.get("description", str(rule_draft)),
            rule_count=world_ctx.get("rule_count", 0),
            avg_fear=round(world_ctx.get("avg_fear", 50)),
            places=world_ctx.get("places", []),
            difficulty=difficulty_level
            or world_ctx.get("difficulty_level")
            or world_ctx.get("difficulty", "normal"),
        )

        return user_prompt

    def format_event_for_narrative(self, event: Dict[str, Any]) -> str:
        """简单格式化事件描述"""
        if isinstance(event, dict):
            return event.get("description", str(event))
        if hasattr(event, "description"):
            return getattr(event, "description")
        return str(event)
    
    def format_time_chinese(self, time_of_day: str) -> str:
        """将英文时间段转换为中文"""
        time_map = {
            "morning": "清晨",
            "afternoon": "下午",
            "evening": "傍晚",
            "night": "深夜"
        }
        return time_map.get(time_of_day, time_of_day)


# ========== 工具函数 ==========

def create_mock_turn_plan() -> Dict[str, Any]:
    """创建模拟的回合计划（用于测试或降级）"""
    return {
        "dialogue": [
            {
                "speaker": "张三",
                "text": "这地方越来越诡异了，我们得想办法离开。",
                "emotion": "fear"
            },
            {
                "speaker": "李四",
                "text": "先别慌，我们分头找找有没有其他出路。",
                "emotion": "calm"
            }
        ],
        "actions": [
            {
                "npc": "张三",
                "action": "search",
                "target": "客厅的柜子",
                "reason": "寻找可能的线索或工具",
                "priority": "high"
            },
            {
                "npc": "李四",
                "action": "investigate",
                "target": "奇怪的声音来源",
                "reason": "确认潜在威胁",
                "risk": "可能遭遇危险",
                "priority": "medium"
            }
        ],
        "atmosphere": "空气中弥漫着不安的气息，每个人都能感受到潜伏的危险。"
    }


def create_mock_narrative() -> str:
    """创建模拟的叙事文本（用于测试或降级）"""
    return """夜色如墨，将整个房间笼罩在无边的黑暗中。张三颤抖着伸手摸索着墙壁，
指尖触及的冰冷让他不由得打了个寒颤。不远处传来李四急促的呼吸声，
在死寂的环境中显得格外刺耳。

突然，楼上传来一阵诡异的脚步声——缓慢、沉重，仿佛有什么东西在拖行。
两人对视一眼，眼中都流露出深深的恐惧。他们知道，真正的噩梦才刚刚开始……"""


def create_mock_rule_eval() -> Dict[str, Any]:
    """创建模拟的规则评估结果（用于测试或降级）"""
    return {
        "name": "禁忌之镜",
        "trigger": {
            "type": "compound",
            "conditions": ["时间是午夜", "照镜子超过3秒"],
            "probability": 0.7
        },
        "effect": {
            "type": "custom",
            "params": {
                "sanity_loss": 30,
                "fear_gain": 50,
                "special": "镜像替换"
            },
            "description": "被镜中的邪恶分身替换"
        },
        "cooldown": 3,
        "cost": 150,
        "difficulty": 6,
        "loopholes": ["闭着眼睛经过镜子", "用布遮住所有镜子"],
        "suggestion": "可以增加更多触发条件，比如需要说出特定词语，增加规则的策略深度"
    }
