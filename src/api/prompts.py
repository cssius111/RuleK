# -*- coding: utf-8 -*-
"""
Prompt模板管理模块
使用Jinja2管理和渲染各种AI调用的prompt模板
"""
from jinja2 import Environment, BaseLoader, Template
from typing import List, Dict, Any, Optional, Tuple
import json

# ========== System Prompts ==========

TURN_PLAN_SYSTEM = """你是一个恐怖生存游戏的"导演兼规则仲裁者"。你的任务是：
1. 基于NPC的性格、恐惧值、理智值和当前状态，生成真实自然的中文对话（每人1-2句）
2. 对话要反映角色的心理状态和对最近事件的反应
3. 根据对话内容和角色状态，为每个NPC分配合理的行动
4. 行动必须符合角色性格，并考虑当前环境和规则限制
5. 严格按照JSON Schema格式输出，确保JSON语法正确
6. 如果无法满足要求，在响应中包含 "error" 字段说明原因"""

NARRATIVE_SYSTEM = """你是一位专业的恐怖小说作家，擅长将游戏事件转化为引人入胜的叙述。要求：
1. 使用第三人称视角，200-300字的篇幅
2. 营造恐怖、悬疑、压抑的氛围
3. 注重环境描写和心理刻画
4. 保持叙事的连贯性和逻辑性
5. 不要提及任何游戏机制、规则引擎等元信息
6. 适当使用悬念和暗示增强恐怖感"""

RULE_EVAL_SYSTEM = """你是恐怖游戏的资深规则设计师和平衡专家。你需要：
1. 分析玩家提出的自然语言规则，将其转化为结构化的触发器和效果
2. 评估规则的实施成本（50-500积分）和难度（1-10级）
3. 识别规则中的潜在漏洞和可被利用的地方
4. 提供改进建议以增强规则的恐怖感和平衡性
5. 预估规则带来的恐惧值收益
6. 输出格式必须严格遵循JSON Schema"""

DIALOGUE_GEN_SYSTEM = """你是恐怖故事中的角色配音导演。基于角色状态和场景，生成符合人物性格的对话。要求：
1. 对话要自然、口语化，符合中文表达习惯
2. 反映角色当前的恐惧和理智状态
3. 对话中体现角色之间的关系动态
4. 适当加入情绪表达和肢体语言描述
5. 营造紧张、不安的氛围"""

# ========== User Prompt Templates ==========

TURN_PLAN_USER = """【场景概述】
时间：{{ time_of_day }}    
地点：{{ location }}
天气：{{ weather | default('阴沉') }}
环境恐惧等级：{{ ambient_fear }}/100

【最近发生的事件】（按时间顺序）
{% for event in recent_events %}
{{ loop.index }}. {{ event }}
{% endfor %}

【当前激活的规则】
{% for rule in active_rules %}
- {{ rule }}
{% endfor %}

【存活NPC状态】
{% for npc in npcs %}
{{ loop.index }}. {{ npc.name }}
   - 恐惧值：{{ npc.fear }}/100 {% if npc.fear > 80 %}[极度恐慌]{% elif npc.fear > 60 %}[非常害怕]{% elif npc.fear > 40 %}[感到恐惧]{% elif npc.fear > 20 %}[略微不安]{% else %}[相对冷静]{% endif %}
   - 理智值：{{ npc.sanity }}/100 {% if npc.sanity < 20 %}[濒临崩溃]{% elif npc.sanity < 40 %}[精神不稳]{% elif npc.sanity < 60 %}[压力较大]{% elif npc.sanity < 80 %}[尚可应对]{% else %}[思维清晰]{% endif %}
   - 性格特征：{{ npc.traits | join("、") }}
   - 当前状态：{{ npc.status }}
   - 所在位置：{{ npc.location }}
   {% if npc.inventory %}
   - 携带物品：{{ npc.inventory | join("、") }}
   {% endif %}
{% endfor %}

【可访问的地点】
{{ available_places | join("、") }}

【特殊条件】
{% for condition in special_conditions %}
- {{ condition }}
{% endfor %}

【行动规则】
1. 每个NPC本回合只能执行一个主要行动
2. 行动类型包括：move(移动)、search(搜索)、talk(交谈)、use_item(使用物品)、wait(等待)、defend(防御)、investigate(调查)、hide(躲藏)、run(逃跑)
3. 行动必须符合角色性格和当前状态
4. 需要考虑已知规则的限制

【输出要求】
请生成包含对话和行动计划的JSON，格式如下：

```json
{
  "dialogue": [
    {
      "speaker": "NPC名字",
      "text": "说话内容",
      "emotion": "情绪（可选）"
    }
  ],
  "actions": [
    {
      "npc": "NPC名字",
      "action": "行动类型",
      "target": "目标地点或对象",
      "reason": "选择该行动的理由",
      "risk": "可能的风险（可选）",
      "priority": 1-5的优先级
    }
  ],
  "turn_summary": "本回合概要（可选）",
  "atmosphere": "回合氛围（可选）"
}
```

请确保：
1. 每个存活NPC都应该有对话或行动
2. 对话要反映角色当前的心理状态
3. 行动要有合理的动机
4. 输出必须是合法的JSON格式"""

NARRATIVE_USER = """【时间段】{{ time_of_day }}
【地点】{{ location }}
【环境】{{ atmosphere }}

【本回合关键事件】（按时间顺序）
{% for event in events %}
{{ loop.index }}. {{ event }}
{% endfor %}

【参与人物及其状态】
{% for npc in npc_states %}
- {{ npc.name }}：{{ npc.status }}（恐惧{{ npc.fear }}/理智{{ npc.sanity }}）
{% endfor %}

【写作要求】
1. 将上述事件整合成一段200-300字的恐怖叙事
2. 使用第三人称，时态统一
3. 重点描写：
   - 环境的诡异氛围
   - 人物的心理活动和恐惧
   - 事件之间的因果关联
   - 潜在的危险暗示
4. 可以适当添加环境细节，但不要偏离主要事件
5. 结尾留下悬念或不祥的预感

请直接输出叙事文本，不要有其他说明。"""

RULE_EVAL_USER = """【玩家提出的规则】
"{{ rule_nl }}"

【当前游戏世界状态】
- 已存在规则数量：{{ rule_count }}
- 平均恐惧等级：{{ avg_fear }}/100
- 游戏难度：{{ difficulty_level | default('普通') }}
- 可用地点：{{ places | join("、") }}
- 常见物品：{{ common_items | join("、") | default('手电筒、日记本、钥匙、镜子') }}

【规则设计指导原则】
1. 规则应该增强恐怖氛围，而不是单纯的难度
2. 最好有明确的触发条件和可预见的后果
3. 给玩家留下一定的应对空间，但不能太容易规避
4. 规则之间可以有关联性，形成规则网络
5. 成本应该与规则的致命程度和影响范围成正比

【评估要求】
请分析该规则并输出以下JSON格式的评估结果：

```json
{
  "name": "规则名称（精炼、恐怖）",
  "trigger": {
    "type": "触发器类型（time/location/action/item/dialogue/condition/composite）",
    "conditions": ["具体触发条件列表"],
    "logic": "AND或OR（多条件时的逻辑关系）"
  },
  "effect": {
    "type": "效果类型（death/injury/fear/sanity/teleport/transform/reveal/custom）",
    "params": {
      "参数名": "参数值"
    },
    "description": "效果的详细描述"
  },
  "cooldown": 冷却时间（秒）,
  "cost": 成本评估（50-500）,
  "difficulty": 难度等级（1-10）,
  "loopholes": [
    "潜在漏洞1",
    "潜在漏洞2"
  ],
  "suggestion": "改进建议",
  "estimated_fear_gain": 预估恐惧值收益（0-200）
}
```

请确保：
1. 成本在50-500之间，考虑规则的威力和覆盖面
2. 难度在1-10之间，反映玩家避免触发的难易程度
3. 至少识别2个潜在漏洞
4. 提供具体可行的改进建议"""

DIALOGUE_CONTEXT_USER = """【场景】{{ scene_description }}
【时间】{{ time }}
【氛围】{{ atmosphere }}

【参与对话的角色】
{% for participant in participants %}
{{ loop.index }}. {{ participant.name }}
   - 性格：{{ participant.traits | join("、") }}
   - 状态：{{ participant.status }}
   - 情绪：{{ participant.emotion | default('紧张') }}
{% endfor %}

【对话背景】
{{ context }}

【对话要求】
1. 每人说1-2句话，总共不超过{{ max_turns | default(6) }}个对话轮次
2. 对话要体现角色性格和当前情绪
3. 适当加入语气词、停顿、重复等口语特征
4. 可以包含动作描述（用括号表示）

请按以下格式生成对话：
角色名：对话内容（可选的动作描述）"""

# ========== Prompt Builder Class ==========

class PromptManager:
    """Prompt模板管理器"""
    
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
        self._template_cache: Dict[str, Template] = {}
    
    def _get_template(self, template_str: str) -> Template:
        """获取或缓存模板"""
        cache_key = hash(template_str)
        if cache_key not in self._template_cache:
            self._template_cache[cache_key] = self.env.from_string(template_str)
        return self._template_cache[cache_key]
    
    def build_turn_plan_prompt(
        self,
        npcs: List[Dict[str, Any]],
        time_of_day: str,
        location: str,
        recent_events: List[str],
        available_places: List[str],
        active_rules: Optional[List[str]] = None,
        weather: Optional[str] = None,
        ambient_fear: int = 50,
        special_conditions: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """构建回合计划的prompt"""
        template = self._get_template(TURN_PLAN_USER)
        
        # 确保必要字段存在
        for npc in npcs:
            npc.setdefault('inventory', [])
            npc.setdefault('status', '正常')
            npc.setdefault('traits', [])
        
        user_prompt = template.render(
            npcs=npcs,
            time_of_day=time_of_day,
            location=location,
            recent_events=recent_events[-5:] if recent_events else [],  # 最近5条
            available_places=available_places,
            active_rules=active_rules or [],
            weather=weather,
            ambient_fear=ambient_fear,
            special_conditions=special_conditions or []
        )
        
        return TURN_PLAN_SYSTEM, user_prompt
    
    def build_narrative_prompt(
        self,
        events: List[str],
        time_of_day: str,
        location: str = "未知地点",
        atmosphere: str = "恐怖压抑",
        npc_states: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[str, str]:
        """构建叙事生成的prompt"""
        template = self._get_template(NARRATIVE_USER)
        
        user_prompt = template.render(
            events=events,
            time_of_day=time_of_day,
            location=location,
            atmosphere=atmosphere,
            npc_states=npc_states or []
        )
        
        return NARRATIVE_SYSTEM, user_prompt
    
    def build_rule_eval_prompt(
        self,
        rule_nl: str,
        rule_count: int,
        avg_fear: float,
        places: List[str],
        difficulty_level: Optional[str] = None,
        common_items: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """构建规则评估的prompt"""
        template = self._get_template(RULE_EVAL_USER)
        
        user_prompt = template.render(
            rule_nl=rule_nl,
            rule_count=rule_count,
            avg_fear=int(avg_fear),
            places=places,
            difficulty_level=difficulty_level,
            common_items=common_items
        )
        
        return RULE_EVAL_SYSTEM, user_prompt
    
    def build_dialogue_prompt(
        self,
        participants: List[Dict[str, Any]],
        context: str,
        scene_description: str = "阴暗的房间",
        time: str = "深夜",
        atmosphere: str = "紧张",
        max_turns: int = 6
    ) -> Tuple[str, str]:
        """构建对话生成的prompt"""
        template = self._get_template(DIALOGUE_CONTEXT_USER)
        
        user_prompt = template.render(
            participants=participants,
            context=context,
            scene_description=scene_description,
            time=time,
            atmosphere=atmosphere,
            max_turns=max_turns
        )
        
        return DIALOGUE_GEN_SYSTEM, user_prompt

    def format_npc_state(self, npc: Dict[str, Any]) -> str:
        """格式化单个NPC状态用于prompt"""
        parts = [f"{npc.get('name', '未知')}"]
        parts.append(f"恐惧{npc.get('fear', 0)}")
        parts.append(f"理智{npc.get('sanity', 100)}")
        
        if traits := npc.get('traits'):
            parts.append(f"性格[{','.join(traits)}]")
        
        if status := npc.get('status'):
            parts.append(f"状态:{status}")
            
        if location := npc.get('location'):
            parts.append(f"@{location}")
            
        return " | ".join(parts)
    
    def format_event_for_narrative(self, event: Dict[str, Any]) -> str:
        """格式化事件用于叙事生成"""
        event_type = event.get('type', 'unknown')
        
        if event_type == 'dialogue':
            return f"{event.get('speaker', '某人')}说：{event.get('text', '...')}"
        elif event_type == 'action':
            actor = event.get('actor', '某人')
            action = event.get('action', '做了什么')
            target = event.get('target', '')
            return f"{actor}在{event.get('location', '某处')}{action}{target}"
        elif event_type == 'rule_triggered':
            return f"[规则触发] {event.get('description', '发生了诡异的事情')}"
        elif event_type == 'death':
            return f"[死亡] {event.get('victim', '某人')}{event.get('cause', '神秘死亡')}"
        else:
            return event.get('description', '发生了未知事件')

    def validate_json_response(self, response: str, expected_type: str) -> Tuple[bool, Any, Optional[str]]:
        """验证和解析JSON响应"""
        try:
            # 尝试提取JSON部分（去除可能的markdown标记）
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            # 解析JSON
            data = json.loads(response)
            
            # 根据期望类型进行基本验证
            if expected_type == "turn_plan":
                if not isinstance(data.get('dialogue'), list):
                    return False, None, "对话必须是列表"
                if not isinstance(data.get('actions'), list):
                    return False, None, "行动必须是列表"
            elif expected_type == "rule_eval":
                required_fields = ['name', 'trigger', 'effect', 'cost', 'difficulty']
                missing = [f for f in required_fields if f not in data]
                if missing:
                    return False, None, f"缺少必要字段: {', '.join(missing)}"
            
            return True, data, None
            
        except json.JSONDecodeError as e:
            return False, None, f"JSON解析错误: {str(e)}"
        except Exception as e:
            return False, None, f"验证错误: {str(e)}"


# ========== 便捷函数 ==========

def create_prompt_manager() -> PromptManager:
    """创建Prompt管理器实例"""
    return PromptManager()


def get_system_prompt(prompt_type: str) -> str:
    """获取系统prompt"""
    prompts = {
        "turn_plan": TURN_PLAN_SYSTEM,
        "narrative": NARRATIVE_SYSTEM,
        "rule_eval": RULE_EVAL_SYSTEM,
        "dialogue": DIALOGUE_GEN_SYSTEM
    }
    return prompts.get(prompt_type, "")


# ========== 测试示例 ==========

if __name__ == "__main__":
    # 测试prompt生成
    pm = PromptManager()
    
    # 测试回合计划prompt
    test_npcs = [
        {
            "name": "张三",
            "fear": 45,
            "sanity": 75,
            "traits": ["谨慎", "理性"],
            "status": "警觉",
            "location": "客厅"
        }
    ]
    
    system, user = pm.build_turn_plan_prompt(
        npcs=test_npcs,
        time_of_day="午夜",
        location="废弃医院",
        recent_events=["听到二楼传来脚步声"],
        available_places=["客厅", "走廊", "楼梯"]
    )
    
    print("=== Turn Plan Prompt ===")
    print("System:", system[:100] + "...")
    print("User:", user[:200] + "...")
