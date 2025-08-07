"""
AI API 数据模型定义
使用 Pydantic 进行数据验证和序列化
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ========== 对话和行动相关 ==========


class DialogueTurn(BaseModel):
    """单个对话回合"""

    speaker: str = Field(description="说话者名字")
    text: str = Field(description="对话内容")
    emotion: Optional[Literal["fear", "calm", "panic", "suspicious", "angry"]] = Field(
        default="calm", description="情绪标签"
    )

    model_config = ConfigDict(extra="allow")


class PlannedAction(BaseModel):
    """NPC计划的行动"""

    npc: str = Field(description="执行者名字")
    action: Literal[
        "move",
        "search",
        "talk",
        "use_item",
        "wait",
        "defend",
        "investigate",
        "hide",
        "run",
        "custom",
    ] = Field(description="行动类型")
    target: Optional[str] = Field(default=None, description="目标对象或地点")
    reason: Optional[str] = Field(default=None, description="行动理由")
    risk: Optional[str] = Field(default=None, description="潜在风险")
    priority: Optional[Any] = Field(
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
        return "medium"

    model_config = ConfigDict(extra="allow")


class TurnPlan(BaseModel):
    """回合计划：包含对话和行动"""

    dialogue: List[DialogueTurn] = Field(default_factory=list, description="对话列表")
    actions: List[PlannedAction] = Field(default_factory=list, description="行动计划列表")
    atmosphere: Optional[str] = Field(default=None, description="氛围描述")

    model_config = ConfigDict(extra="allow")


# ========== 叙事相关 ==========


class NarrativeOut(BaseModel):
    """叙事输出"""

    narrative: str = Field(description="叙事文本")
    style: Literal["horror", "suspense", "mystery"] = Field(
        default="horror", description="叙事风格"
    )

    @field_validator("narrative")
    def enforce_min_length(cls, v):
        """确保叙事文本长度"""
        if len(v) < 200:
            # 自动补充到最小长度
            v += "\n\n夜色愈发深沉，诡异的氛围笼罩着整个空间。每个人都能感受到，真正的恐怖才刚刚开始……"
        return v

    model_config = ConfigDict(extra="allow")


# ========== 规则评估相关 ==========


class RuleTrigger(BaseModel):
    """规则触发器"""

    type: Literal[
        "action", "time", "location", "dialogue", "event", "compound"
    ] = Field(description="触发类型")
    conditions: List[str] = Field(default_factory=list, description="触发条件列表")
    probability: float = Field(default=0.8, ge=0.0, le=1.0, description="触发概率")

    model_config = ConfigDict(extra="allow")


class RuleEffect(BaseModel):
    """规则效果"""

    type: Literal[
        "instant_death",
        "damage",
        "fear_gain",
        "teleport",
        "transform",
        "summon",
        "custom",
    ] = Field(description="效果类型")
    params: Dict[str, Any] = Field(default_factory=dict, description="效果参数")
    description: str = Field(default="", description="效果描述")

    model_config = ConfigDict(extra="allow")


class RuleEvalResult(BaseModel):
    """规则评估结果"""

    name: str = Field(description="规则名称")
    trigger: RuleTrigger = Field(description="触发条件")
    effect: RuleEffect = Field(description="规则效果")
    cooldown: int = Field(default=0, ge=0, le=10, description="冷却回合数")
    cost: int = Field(description="消耗的恐惧点数")
    difficulty: int = Field(description="规则难度（1-10）")
    loopholes: List[str] = Field(default_factory=list, description="规则破绽")
    suggestion: str = Field(default="", description="改进建议")

    @field_validator("cost")
    def validate_cost(cls, v):
        """验证成本范围"""
        if not (50 <= v <= 500):
            # 自动修正到合理范围
            v = max(50, min(500, v))
        return v

    @field_validator("difficulty")
    def validate_difficulty(cls, v):
        """验证难度范围"""
        if not (1 <= v <= 10):
            # 自动修正到合理范围
            v = max(1, min(10, v))
        return v

    model_config = ConfigDict(extra="allow")


# ========== 复合响应 ==========


class DialoguePlanBundle(BaseModel):
    """对话和计划的组合响应"""

    turn_plan: TurnPlan = Field(description="回合计划")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    model_config = ConfigDict(extra="allow")


# ========== 游戏状态相关 ==========


class NPCStateForAI(BaseModel):
    """供AI使用的NPC状态"""

    name: str
    fear: int = Field(ge=0, le=100)
    sanity: int = Field(ge=0, le=100)
    hp: int = Field(ge=0, le=100)
    traits: List[str] = Field(default_factory=list)
    status: str = Field(default="正常")
    location: str
    inventory: List[str] = Field(default_factory=list)
    relationships: Dict[str, int] = Field(
        default_factory=dict, description="与其他NPC的关系值"
    )

    model_config = ConfigDict(extra="allow")


class SceneContext(BaseModel):
    """场景上下文"""

    current_location: str
    time_of_day: Literal["morning", "afternoon", "evening", "night"]
    recent_events: List[str] = Field(default_factory=list)
    active_rules: List[str] = Field(default_factory=list)
    ambient_fear_level: int = Field(ge=0, le=100)
    special_conditions: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


# ========== 错误处理 ==========


class AIError(BaseModel):
    """AI错误响应"""

    error: str = Field(description="错误信息")
    error_type: Literal["parse", "validation", "api", "timeout", "unknown"] = Field(
        default="unknown"
    )
    suggestion: Optional[str] = Field(default=None, description="建议的解决方案")
    fallback_used: bool = Field(default=False, description="是否使用了降级方案")

    model_config = ConfigDict(extra="allow")


# ========== 批处理请求 ==========


class BatchRequest(BaseModel):
    """批量请求"""

    requests: List[Dict[str, Any]] = Field(description="请求列表")
    priority: Literal["high", "normal", "low"] = Field(default="normal")
    timeout: int = Field(default=30, ge=10, le=120, description="超时时间(秒)")

    model_config = ConfigDict(extra="allow")


# ========== 工具函数 ==========


ErrorType = Literal["parse", "validation", "api", "timeout", "unknown"]


def create_error_response(error_msg: str, error_type: ErrorType = "unknown") -> AIError:
    """创建标准错误响应"""
    suggestions = {
        "parse": "请检查输入格式是否正确",
        "validation": "请确保所有必需字段都已提供且格式正确",
        "api": "API服务暂时不可用，请稍后重试",
        "timeout": "请求超时，可能是网络问题或服务器繁忙",
        "unknown": "发生未知错误，请联系技术支持",
    }

    return AIError(
        error=error_msg,
        error_type=error_type,
        suggestion=suggestions.get(error_type, suggestions["unknown"]),
        fallback_used=True,
    )


def validate_turn_plan(plan: TurnPlan) -> List[str]:
    """验证回合计划的合法性"""
    issues = []

    # 检查对话
    if not plan.dialogue:
        issues.append("缺少对话内容")

    # 检查行动
    npc_actions = {}
    for action in plan.actions:
        if action.npc in npc_actions:
            issues.append(f"NPC {action.npc} 有多个行动")
        npc_actions[action.npc] = action

    return issues


# === 兼容性垫片 (Compatibility Shims) ===
# 为了保持向后兼容，在这里添加旧测试期望的类型定义


class NPCState(TypedDict):
    """Simplified NPC state for API compatibility"""

    name: str
    fear: int
    sanity: int
    location: str
    status: Literal["normal", "frightened", "dead"]
    traits: Optional[List[str]]
