"""
规则相关的数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class TriggerType(str, Enum):
    """触发类型枚举"""
    ACTION = "action"
    TIME = "time"
    LOCATION = "location"
    ITEM = "item"
    CONDITION = "condition"
    RANDOM = "random"

class EffectType(str, Enum):
    """效果类型枚举"""
    INSTANT_DEATH = "instant_death"
    FEAR_INCREASE = "fear_increase"
    SANITY_DECREASE = "sanity_decrease"
    TELEPORT = "teleport"
    ITEM_GRANT = "item_grant"
    CONTINUOUS_DAMAGE = "continuous_damage"

class RuleTrigger(BaseModel):
    """规则触发条件"""
    type: TriggerType
    conditions: Dict[str, Any] = {}
    probability: float = Field(default=1.0, ge=0.0, le=1.0)

class RuleEffect(BaseModel):
    """规则效果"""
    type: EffectType
    value: Optional[int] = None
    target: Optional[str] = None
    duration: Optional[int] = None
    params: Dict[str, Any] = {}

class RuleModel(BaseModel):
    """规则模型"""
    id: str
    name: str
    description: str
    cost: int
    trigger: RuleTrigger
    effects: List[RuleEffect]
    cooldown: int = 0
    is_active: bool = True
    level: int = 1
    category: Optional[str] = None

class RuleTemplateRequest(BaseModel):
    """从模板创建规则请求"""
    template_id: str

class CustomRuleRequest(BaseModel):
    """创建自定义规则请求"""
    name: str
    description: str
    trigger: RuleTrigger
    effects: List[RuleEffect]
    cooldown: int = 0

class AIRuleParseRequest(BaseModel):
    """AI解析规则请求"""
    description: str
    game_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class RuleUpgradeRequest(BaseModel):
    """规则升级请求"""
    rule_id: str

class RuleCostCalculationRequest(BaseModel):
    """规则成本计算请求"""
    trigger: RuleTrigger
    effects: List[RuleEffect]
    cooldown: int = 0
