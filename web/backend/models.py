"""
API 数据模型定义
使用 Pydantic 进行数据验证
"""
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime


# ==================== 请求模型 ====================

class GameCreateRequest(BaseModel):
    """创建游戏请求"""
    difficulty: Literal["easy", "normal", "hard"] = Field(
        default="normal",
        description="游戏难度"
    )
    npc_count: int = Field(
        default=4,
        ge=2,
        le=6,
        description="NPC数量"
    )
    
    @field_validator('npc_count')
    def validate_npc_count(cls, v):
        if v < 2 or v > 6:
            raise ValueError("NPC count must be between 2 and 6")
        return v


class RuleCreateRequest(BaseModel):
    """创建规则请求"""
    name: str = Field(..., min_length=1, max_length=50, description="规则名称")
    description: str = Field(..., min_length=1, max_length=500, description="规则描述")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="触发条件")
    trigger: Dict[str, Any] = Field(..., description="触发器配置")
    effect: Dict[str, Any] = Field(..., description="效果配置")
    cost: int = Field(..., ge=50, le=1000, description="消耗积分")
    
    model_config = {
        "json_json_schema_extra": {
            "example": {
                "name": "午夜照镜死",
                "description": "午夜时分照镜子会导致死亡",
                "requirements": {
                    "time": {"from": "00:00", "to": "04:00"},
                    "areas": ["bathroom"],
                    "items": ["mirror"]
                },
                "trigger": {
                    "action": "look_mirror",
                    "extra_conditions": ["lights_off"]
                },
                "effect": {
                    "type": "instant_death",
                    "fear_gain": 200
                },
                "cost": 150
            }
        }
    }


class ActionRequest(BaseModel):
    """玩家动作请求"""
    action_type: str = Field(..., description="动作类型")
    target: Optional[str] = Field(None, description="目标ID")
    params: Dict[str, Any] = Field(default_factory=dict, description="额外参数")


class ModeSwitchRequest(BaseModel):
    """模式切换请求"""
    mode: Literal["backstage", "in_scene"] = Field(..., description="游戏模式")
    character_name: Optional[str] = Field(None, description="下场时的角色名")


# ==================== 响应模型 ====================

class NPCStatus(BaseModel):
    """NPC状态"""
    id: str
    name: str
    hp: int
    sanity: int
    fear: int
    location: str
    status_effects: List[str]
    is_alive: bool
    
    model_config = ConfigDict(
        from_attributes = True


class RuleInfo(BaseModel):
    """规则信息"""
    id: str
    name: str
    description: str
    level: int
    cost: int
    is_active: bool
    times_triggered: int
    loopholes: List[Dict[str, Any]]


class GameStateResponse(BaseModel):
    """游戏状态响应"""
    game_id: str
    started_at: datetime
    current_turn: int
    fear_points: int
    phase: str
    mode: str
    time_of_day: str
    npcs: List[NPCStatus]
    active_rules: int
    total_fear_gained: int
    npcs_died: int
    
    model_config = {
        "json_json_schema_extra": {
            "example": {
                "game_id": "game_123",
                "started_at": "2024-01-01T00:00:00",
                "current_turn": 5,
                "fear_points": 850,
                "phase": "action",
                "mode": "backstage",
                "time_of_day": "night",
                "npcs": [],
                "active_rules": 3,
                "total_fear_gained": 450,
                "npcs_died": 1
            }
        }
    }


class TurnResult(BaseModel):
    """回合结果"""
    turn: int
    events: List[Dict[str, Any]]
    fear_gained: int
    npcs_affected: List[str]
    rules_triggered: List[str]
    narrative: Optional[str] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ==================== WebSocket模型 ====================

class WebSocketMessage(BaseModel):
    """WebSocket消息"""
    type: Literal["ping", "pong", "action", "update", "error"]
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class GameUpdate(BaseModel):
    """游戏更新推送"""
    update_type: Literal["state", "event", "npc", "rule", "dialogue"]
    game_id: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


# ==================== 存档模型 ====================

class SaveGameInfo(BaseModel):
    """存档信息"""
    filename: str
    game_id: str
    saved_at: datetime
    turn: int
    description: Optional[str] = None


class LoadGameRequest(BaseModel):
    """加载游戏请求"""
    filename: str


# ==================== AI相关模型 ====================

class AITurnRequest(BaseModel):
    """AI回合请求"""
    force_dialogue: bool = Field(default=True, description="是否强制生成对话")
    include_hidden_events: bool = Field(default=False, description="叙事中是否包含隐藏事件")
    

class AIDialogueResponse(BaseModel):
    """AI对话响应"""
    speaker: str
    text: str
    emotion: Optional[str] = None


class AIActionResponse(BaseModel):
    """AI行动响应"""
    npc: str
    action: str
    target: Optional[str] = None
    reason: Optional[str] = None
    risk: Optional[str] = None
    priority: int = 1


class AITurnPlanResponse(BaseModel):
    """AI回合计划响应"""
    dialogue: List[AIDialogueResponse]
    actions: List[AIActionResponse]
    turn_summary: Optional[str] = None
    atmosphere: Optional[str] = None


class AIRuleEvaluationRequest(BaseModel):
    """AI规则评估请求"""
    rule_description: str = Field(..., min_length=5, max_length=500, description="规则的自然语言描述")
    
    model_config = {
        "json_json_schema_extra": {
            "example": {
                "rule_description": "晚上10点后不能开灯，否则会吸引怪物"
            }
        }
    }


class AIRuleEvaluationResponse(BaseModel):
    """AI规则评估响应"""
    name: str
    cost: int
    difficulty: int
    loopholes: List[str]
    suggestion: str
    estimated_fear_gain: Optional[int] = None
    parsed_rule: Dict[str, Any]
    

class AINarrativeRequest(BaseModel):
    """AI叙事生成请求"""
    include_hidden_events: bool = Field(default=False, description="是否包含隐藏事件")
    style: str = Field(default="horror", description="叙事风格")
    

class AINarrativeResponse(BaseModel):
    """AI叙事生成响应"""
    narrative: str
    word_count: int
    style: str
