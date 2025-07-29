# AI集成实施指南

## 快速开始

本指南提供了将AI功能集成到RuleK项目的具体步骤和代码示例。

## 步骤1：创建Schema文件

### 1.1 创建 `src/api/schemas.py`

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal, Dict, Any

# ---------- 对话和行动 ----------
class DialogueTurn(BaseModel):
    """单个对话回合"""
    speaker: str
    text: str

class PlannedAction(BaseModel):
    """计划的NPC行动"""
    npc: str
    action: Literal["move", "search", "talk", "use_item", "wait", "defend", "investigate", "custom"]
    target: Optional[str] = None
    reason: Optional[str] = None
    risk: Optional[str] = None

class TurnPlan(BaseModel):
    """回合计划：包含对话和行动"""
    dialogue: List[DialogueTurn] = Field(default_factory=list)
    actions: List[PlannedAction] = Field(default_factory=list)

# ---------- 叙事 ----------
class NarrativeOut(BaseModel):
    """叙事输出"""
    narrative: str

    @validator("narrative")
    def enforce_len(cls, v):
        if len(v) < 200:
            v += " ……他们意识到，这只是噩梦的开始。"
        return v

# ---------- 规则评估 ----------
class RuleTrigger(BaseModel):
    """规则触发器"""
    type: str
    conditions: List[str] = []

class RuleEffect(BaseModel):
    """规则效果"""
    type: str
    params: Dict[str, Any] = {}

class RuleEvalResult(BaseModel):
    """规则评估结果"""
    name: str
    trigger: RuleTrigger
    effect: RuleEffect
    cooldown: int = 0
    cost: int
    difficulty: int
    loopholes: List[str] = []
    suggestion: str = ""

    @validator("cost")
    def cost_range(cls, v):
        if not (50 <= v <= 500):
            raise ValueError("成本必须在50-500之间")
        return v

    @validator("difficulty")
    def difficulty_range(cls, v):
        if not (1 <= v <= 10):
            raise ValueError("难度必须在1-10之间")
        return v
```

## 步骤2：实现Prompt管理器

### 2.1 创建 `src/api/prompts.py`

```python
from jinja2 import Environment, BaseLoader
from typing import List, Dict, Any

# Prompt模板
TURN_PLAN_SYSTEM = """你是一个恐怖生存游戏的"导演兼规则仲裁者"。任务：
1. 用中文生成 NPC 之间的真实对话（每人1~2句）。
2. 对话要基于每个NPC的性格、恐惧/理智值、状态与最近事件。
3. 结尾给出本回合的"任务分配/行动计划"：谁去哪里、做什么、理由是什么。
4. 严格输出符合 JSON Schema 的结果，不要多输出其他内容。
5. 若无法满足要求，返回一个字段 "error" 描述问题。"""

TURN_PLAN_USER = """【场景概述】
时间：{{ time_of_day }}    地点：{{ location }}
最近事件摘要（最多3条）：
{% for event in recent_events %}
- {{ event }}
{% endfor %}

【存活NPC列表】
{% for npc in npcs %}
* {{ npc.name }} | fear={{ npc.fear }} | sanity={{ npc.sanity }} | traits={{ npc.traits|join(",") }} | status="{{ npc.status }}" | location="{{ npc.location }}"
{% endfor %}

【可访问的地点】
{{ available_places|join(", ") }}

【行动点规则】
- 每个NPC本回合最多 1 个主要行动（移动/调查/交互等）。
- 行动必须有理由，可受性格影响，也需考虑规则限制。

【输出要求】
请按以下 JSON Schema 输出（务必保证 JSON 严格合法）：

```json
{
  "dialogue": [
    {
      "speaker": "NPC名字",
      "text": "他/她说的话"
    }
  ],
  "actions": [
    {
      "npc": "NPC名字",
      "action": "动作关键词",
      "target": "目标地点或对象",
      "reason": "选择该行动的心理/逻辑理由",
      "risk": "可能的风险简述（可选）"
    }
  ]
}
```

请直接输出 JSON，不要加注释或多余文本。"""

NARRATIVE_SYSTEM = """你是恐怖小说叙述者，需将本回合发生的事件写成一段 200~300 字的第三人称中文叙事，风格恐怖/悬疑。
保持逻辑连贯，适当描写环境与心理，但不要提及"游戏""规则引擎"等元信息。
若输入不足以生成，请返回一个字段 "error"。"""

NARRATIVE_USER = """【时间段】{{ time_of_day }}
【关键事件列表】（时间顺序）：
{% for event in events %}
- {{ event }}
{% endfor %}

输出要求：
生成200-300字的恐怖叙事，只输出纯文本，不要JSON，不要额外说明。"""

RULE_EVAL_SYSTEM = """你是恐怖游戏的规则评估官：收到玩家提出的自然语言规则，需解析成结构化 JSON，估算成本并指出破绽。
遵守以下 Schema，不要输出其他内容。"""

RULE_EVAL_USER = """玩家提出的规则描述：
"{{ rule_nl }}"

当前游戏状态摘要：
* 已有规则数：{{ rule_count }}
* 平均恐惧：{{ avg_fear }}
* 现有地点：{{ places|join(", ") }}

请输出 JSON：
```json
{
  "name": "规则名",
  "trigger": { "type": "...", "conditions": [...] },
  "effect": { "type": "...", "params": {...} },
  "cooldown": 0,
  "cost": 0,
  "difficulty": 1,
  "loopholes": ["...", "..."],
  "suggestion": "改进建议"
}
```

注：cost 范围 50-500，difficulty 1-10。"""

class PromptManager:
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
    
    def build_turn_plan_prompt(
        self,
        npcs: List[Dict[str, Any]],
        time_of_day: str,
        location: str,
        recent_events: List[str],
        available_places: List[str]
    ) -> tuple[str, str]:
        """构建回合计划的prompt"""
        template = self.env.from_string(TURN_PLAN_USER)
        user_prompt = template.render(
            npcs=npcs,
            time_of_day=time_of_day,
            location=location,
            recent_events=recent_events[-3:],  # 最近3条
            available_places=available_places
        )
        return TURN_PLAN_SYSTEM, user_prompt
    
    def build_narrative_prompt(
        self,
        events: List[str],
        time_of_day: str
    ) -> tuple[str, str]:
        """构建叙事生成的prompt"""
        template = self.env.from_string(NARRATIVE_USER)
        user_prompt = template.render(
            events=events,
            time_of_day=time_of_day
        )
        return NARRATIVE_SYSTEM, user_prompt
    
    def build_rule_eval_prompt(
        self,
        rule_nl: str,
        rule_count: int,
        avg_fear: float,
        places: List[str]
    ) -> tuple[str, str]:
        """构建规则评估的prompt"""
        template = self.env.from_string(RULE_EVAL_USER)
        user_prompt = template.render(
            rule_nl=rule_nl,
            rule_count=rule_count,
            avg_fear=avg_fear,
            places=places
        )
        return RULE_EVAL_SYSTEM, user_prompt
```

## 步骤3：实现DeepSeek客户端

### 3.1 创建 `src/api/deepseek_client.py`

```python
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.api.schemas import TurnPlan, NarrativeOut, RuleEvalResult
from src.api.prompts import PromptManager
from src.config import APIConfig

logger = logging.getLogger(__name__)

class DeepSeekClient:
    def __init__(self, config: APIConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0)
        self.prompt_mgr = PromptManager()
        self.base_url = "https://api.deepseek.com/v1"
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送API请求（带重试）"""
        headers = {
            "Authorization": f"Bearer {self.config.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP错误: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            raise
    
    async def generate_turn_plan(
        self,
        npc_states: List[Dict[str, Any]],
        scene_context: Dict[str, Any],
        available_places: List[str],
        time_of_day: str,
        min_dialogue: int = 1
    ) -> TurnPlan:
        """生成回合计划（对话+行动）"""
        # 构建prompt
        system_prompt, user_prompt = self.prompt_mgr.build_turn_plan_prompt(
            npcs=npc_states,
            time_of_day=time_of_day,
            location=scene_context.get("current_location", "未知地点"),
            recent_events=scene_context.get("recent_events", []),
            available_places=available_places
        )
        
        # 构建请求数据
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 1000
        }
        
        try:
            # 发送请求
            response = await self._make_request("chat/completions", data)
            content = response["choices"][0]["message"]["content"]
            
            # 解析JSON
            try:
                result_data = json.loads(content)
            except json.JSONDecodeError:
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result_data = json.loads(json_match.group())
                else:
                    raise ValueError("无法解析AI响应为JSON")
            
            # 验证并返回
            plan = TurnPlan.parse_obj(result_data)
            
            # 确保至少有min_dialogue条对话
            if len(plan.dialogue) < min_dialogue:
                logger.warning(f"对话数量不足，期望{min_dialogue}条，实际{len(plan.dialogue)}条")
            
            return plan
            
        except Exception as e:
            logger.error(f"生成回合计划失败: {str(e)}")
            # 返回降级方案
            return TurnPlan(
                dialogue=[
                    DialogueTurn(speaker="系统", text="[AI生成失败，使用默认对话]")
                ],
                actions=[]
            )
    
    async def generate_narrative_text(
        self,
        events: List[Dict[str, Any]],
        time_of_day: str,
        min_len: int = 200
    ) -> str:
        """生成叙事文本"""
        # 将事件转换为文本描述
        event_texts = []
        for event in events:
            if event.get("type") == "dialogue":
                event_texts.append(f"{event.get('speaker')}说："{event.get('text')}"")
            elif event.get("type") == "action":
                event_texts.append(f"{event.get('actor')}在{event.get('location')}{event.get('action')}")
            else:
                event_texts.append(event.get("description", "发生了未知事件"))
        
        # 构建prompt
        system_prompt, user_prompt = self.prompt_mgr.build_narrative_prompt(
            events=event_texts,
            time_of_day=time_of_day
        )
        
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.9,
            "max_tokens": 500
        }
        
        try:
            response = await self._make_request("chat/completions", data)
            narrative = response["choices"][0]["message"]["content"].strip()
            
            # 验证长度
            if len(narrative) < min_len:
                narrative += "\n\n夜色渐深，恐惧如影随形……"
            
            return narrative
            
        except Exception as e:
            logger.error(f"生成叙事失败: {str(e)}")
            return "在这个诡异的空间里，一切都变得扑朔迷离……"
    
    async def evaluate_rule_nl(
        self,
        rule_nl: str,
        world_ctx: Dict[str, Any]
    ) -> RuleEvalResult:
        """评估自然语言规则"""
        # 构建prompt
        system_prompt, user_prompt = self.prompt_mgr.build_rule_eval_prompt(
            rule_nl=rule_nl,
            rule_count=world_ctx.get("rule_count", 0),
            avg_fear=world_ctx.get("avg_fear", 50),
            places=world_ctx.get("places", ["客厅", "卧室", "厨房"])
        )
        
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }
        
        try:
            response = await self._make_request("chat/completions", data)
            content = response["choices"][0]["message"]["content"]
            
            # 解析JSON
            result_data = json.loads(content)
            
            # 验证并返回
            return RuleEvalResult.parse_obj(result_data)
            
        except Exception as e:
            logger.error(f"评估规则失败: {str(e)}")
            # 返回默认评估
            return RuleEvalResult(
                name="未知规则",
                trigger=RuleTrigger(type="unknown", conditions=[]),
                effect=RuleEffect(type="unknown", params={}),
                cost=100,
                difficulty=5,
                loopholes=["规则解析失败"],
                suggestion="请尝试更清晰地描述规则"
            )
```

## 步骤4：实现AI管线

### 4.1 创建 `src/ai/turn_pipeline.py`

```python
import logging
from typing import Dict, Any, List, Optional

from src.api.deepseek_client import DeepSeekClient
from src.api.schemas import TurnPlan, PlannedAction
from src.managers.game_state_manager import GameStateManager
from src.models.event import Event, EventType

logger = logging.getLogger(__name__)

class AITurnPipeline:
    """AI驱动的回合管线"""
    
    def __init__(self, game_mgr: GameStateManager, ds_client: DeepSeekClient):
        self.game_mgr = game_mgr
        self.ds_client = ds_client
        
    async def run_turn_ai(self) -> TurnPlan:
        """执行AI驱动的回合"""
        state = self.game_mgr.state
        
        # 准备NPC状态数据
        npc_states = []
        for npc in state.npcs:
            if npc.is_alive:
                npc_states.append({
                    "name": npc.name,
                    "fear": npc.fear,
                    "sanity": npc.sanity,
                    "traits": npc.traits,
                    "status": npc.status,
                    "location": npc.location
                })
        
        # 准备场景上下文
        recent_events = self._get_recent_events(limit=5)
        scene_context = {
            "current_location": state.current_location,
            "recent_events": [e["description"] for e in recent_events]
        }
        
        # 获取可用地点
        available_places = list(state.locations.keys())
        
        # 生成回合计划
        plan = await self.ds_client.generate_turn_plan(
            npc_states=npc_states,
            scene_context=scene_context,
            available_places=available_places,
            time_of_day=state.time_of_day
        )
        
        # 记录对话
        for dialogue in plan.dialogue:
            self._log_dialogue(dialogue.speaker, dialogue.text)
        
        # 验证并执行行动
        for action in plan.actions:
            if self._validate_action(action):
                await self._execute_action(action)
            else:
                logger.warning(f"非法行动被阻止: {action}")
                self._log_event(
                    f"{action.npc}试图{action.action}，但被神秘力量阻止了",
                    EventType.RULE_TRIGGERED
                )
        
        return plan
    
    async def generate_turn_narrative(self) -> str:
        """生成回合叙事"""
        # 获取本回合事件
        turn_events = self._get_turn_events()
        
        # 格式化事件
        formatted_events = []
        for event in turn_events:
            formatted_events.append({
                "type": event.get("type", "unknown"),
                "description": event.get("description", ""),
                "actor": event.get("actor", ""),
                "location": event.get("location", ""),
                "action": event.get("action", "")
            })
        
        # 生成叙事
        narrative = await self.ds_client.generate_narrative_text(
            events=formatted_events,
            time_of_day=self.game_mgr.state.time_of_day
        )
        
        # 保存叙事
        self._save_narrative(narrative)
        
        return narrative
    
    async def evaluate_player_rule(self, rule_description: str) -> Dict[str, Any]:
        """评估玩家提出的规则"""
        # 获取世界状态
        world_ctx = {
            "rule_count": len(self.game_mgr.state.rules),
            "avg_fear": self._calculate_avg_fear(),
            "places": list(self.game_mgr.state.locations.keys())
        }
        
        # 评估规则
        eval_result = await self.ds_client.evaluate_rule_nl(
            rule_nl=rule_description,
            world_ctx=world_ctx
        )
        
        return {
            "name": eval_result.name,
            "cost": eval_result.cost,
            "difficulty": eval_result.difficulty,
            "loopholes": eval_result.loopholes,
            "suggestion": eval_result.suggestion,
            "parsed_rule": {
                "trigger": eval_result.trigger.dict(),
                "effect": eval_result.effect.dict()
            }
        }
    
    def _get_recent_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最近的事件"""
        events = self.game_mgr.state.events_history[-limit:]
        return [e.to_dict() for e in events]
    
    def _get_turn_events(self) -> List[Dict[str, Any]]:
        """获取本回合的事件"""
        current_turn = self.game_mgr.state.turn_count
        turn_events = []
        
        for event in reversed(self.game_mgr.state.events_history):
            if event.turn == current_turn:
                turn_events.append(event.to_dict())
            else:
                break
        
        return list(reversed(turn_events))
    
    def _log_dialogue(self, speaker: str, text: str):
        """记录对话"""
        event = Event(
            type=EventType.NPC_DIALOGUE,
            description=f"{speaker}: {text}",
            turn=self.game_mgr.state.turn_count,
            meta={"speaker": speaker, "text": text}
        )
        self.game_mgr.state.events_history.append(event)
    
    def _log_event(self, description: str, event_type: EventType):
        """记录事件"""
        event = Event(
            type=event_type,
            description=description,
            turn=self.game_mgr.state.turn_count
        )
        self.game_mgr.state.events_history.append(event)
    
    def _validate_action(self, action: PlannedAction) -> bool:
        """验证行动是否合法"""
        # 检查NPC是否存在且存活
        npc = next((n for n in self.game_mgr.state.npcs if n.name == action.npc), None)
        if not npc or not npc.is_alive:
            return False
        
        # 检查目标地点是否存在（如果是移动行动）
        if action.action == "move" and action.target:
            if action.target not in self.game_mgr.state.locations:
                return False
        
        # 其他验证逻辑...
        return True
    
    async def _execute_action(self, action: PlannedAction):
        """执行行动"""
        npc = next((n for n in self.game_mgr.state.npcs if n.name == action.npc), None)
        if not npc:
            return
        
        if action.action == "move":
            # 移动NPC
            old_location = npc.location
            npc.location = action.target
            self._log_event(
                f"{npc.name}从{old_location}移动到{action.target}",
                EventType.NPC_ACTION
            )
            
        elif action.action == "search":
            # 搜索行动
            self._log_event(
                f"{npc.name}在{npc.location}搜索{action.target or '线索'}",
                EventType.NPC_ACTION
            )
            # 可能触发发现事件...
            
        elif action.action == "talk":
            # 交谈行动（已在对话阶段处理）
            pass
            
        # 其他行动类型...
    
    def _calculate_avg_fear(self) -> float:
        """计算平均恐惧值"""
        alive_npcs = [n for n in self.game_mgr.state.npcs if n.is_alive]
        if not alive_npcs:
            return 0
        return sum(n.fear for n in alive_npcs) / len(alive_npcs)
    
    def _save_narrative(self, narrative: str):
        """保存叙事文本"""
        # 可以保存到文件或数据库
        event = Event(
            type=EventType.NARRATIVE,
            description=narrative,
            turn=self.game_mgr.state.turn_count,
            meta={"is_narrative": True}
        )
        self.game_mgr.state.events_history.append(event)
```

## 步骤5：集成到游戏管理器

### 5.1 修改 `src/managers/game_state_manager.py`

在GameStateManager中添加AI相关方法：

```python
# 在 __init__ 方法中添加
self.ai_enabled = config.get("ai_enabled", False)
self.ai_pipeline = None

# 添加新方法
async def init_ai_pipeline(self):
    """初始化AI管线"""
    if self.ai_enabled:
        from src.api.deepseek_client import DeepSeekClient
        from src.ai.turn_pipeline import AITurnPipeline
        
        ds_client = DeepSeekClient(self.config.api)
        self.ai_pipeline = AITurnPipeline(self, ds_client)
        logger.info("AI管线初始化完成")

async def run_ai_turn(self):
    """运行AI驱动的回合"""
    if not self.ai_pipeline:
        logger.warning("AI未启用或未初始化")
        return None
    
    try:
        plan = await self.ai_pipeline.run_turn_ai()
        logger.info(f"AI回合执行完成，生成{len(plan.dialogue)}条对话，{len(plan.actions)}个行动")
        return plan
    except Exception as e:
        logger.error(f"AI回合执行失败: {str(e)}")
        return None

async def generate_narrative(self) -> str:
    """生成回合叙事"""
    if not self.ai_pipeline:
        return "AI叙事生成未启用"
    
    try:
        narrative = await self.ai_pipeline.generate_turn_narrative()
        return narrative
    except Exception as e:
        logger.error(f"叙事生成失败: {str(e)}")
        return "叙事生成失败，请查看日志"
```

## 步骤6：更新配置文件

### 6.1 更新 `config/config.json`

```json
{
  "game": {
    "initial_fear_points": 1000,
    "max_npcs": 6,
    "default_difficulty": "normal",
    "ai_enabled": true
  },
  "api": {
    "deepseek_api_key": "${DEEPSEEK_API_KEY}",
    "model": "deepseek-chat",
    "timeout": 30,
    "max_retries": 3,
    "cache_ttl": 300
  },
  "ai_features": {
    "dialogue_generation": true,
    "action_planning": true,
    "narrative_generation": true,
    "rule_evaluation": true
  }
}
```

## 步骤7：添加CLI集成

### 7.1 更新CLI命令

在CLI模式中添加AI相关选项：

```python
# 在 setup_phase 中添加
if self.game_mgr.ai_enabled:
    choice = input("\n使用AI生成对话和行动？(y/n): ")
    if choice.lower() == 'y':
        print("\n🤖 AI正在生成回合内容...")
        plan = await self.game_mgr.run_ai_turn()
        if plan:
            print("\n【NPC对话】")
            for d in plan.dialogue:
                print(f"{d.speaker}: {d.text}")
            print("\n【行动计划】")
            for a in plan.actions:
                print(f"- {a.npc} → {a.action} {a.target or ''}")

# 在 resolution_phase 结束时添加
if self.game_mgr.ai_enabled:
    choice = input("\n生成本回合叙事？(y/n): ")
    if choice.lower() == 'y':
        print("\n📖 生成叙事中...")
        narrative = await self.game_mgr.generate_narrative()
        print("\n【回合叙事】")
        print(narrative)
```

## 测试检查清单

### 单元测试
- [ ] Schema验证测试
- [ ] Prompt构建测试
- [ ] JSON解析测试
- [ ] 错误处理测试

### 集成测试
- [ ] 完整回合流程
- [ ] API调用失败降级
- [ ] 超时处理
- [ ] 并发请求

### 端到端测试
- [ ] CLI模式下的AI功能
- [ ] Web API的AI端点
- [ ] 性能和响应时间

## 注意事项

1. **API密钥安全**：确保API密钥通过环境变量传递，不要硬编码
2. **错误处理**：所有AI调用都应有降级方案
3. **成本控制**：监控Token使用量，设置预算限制
4. **内容审核**：确保生成内容符合游戏氛围
5. **性能优化**：使用缓存减少重复请求

## 下一步

1. 实现上述所有代码文件
2. 编写单元测试
3. 进行集成测试
4. 优化Prompt以获得更好效果
5. 添加监控和日志

---

*本指南将持续更新*
