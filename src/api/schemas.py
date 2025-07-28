# -*- coding: utf-8 -*-
"""
API数据模型定义
使用Pydantic进行数据验证和序列化
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime

# ---------- 对话和行动 ----------
class DialogueTurn(BaseModel):
    """单个对话回合"""
    speaker: str = Field(..., description="说话者名字")
    text: str = Field(..., description="对话内容")
    emotion: Optional[str] = Field(None, description="情绪标签")
    
    class Config:
        schema_extra = {
            "example": {
                "speaker": "张三",
                "text": "我...我看到了什么？那个影子刚才是不是动了？",
                "emotion": "恐惧"
            }
        }


class PlannedAction(BaseModel):
    """计划的NPC行动"""
    npc: str = Field(..., description="执行行动的NPC名字")
    action: Literal["move", "search", "talk", "use_item", "wait", "defend", "investigate", "hide", "run", "custom"] = Field(..., description="行动类型")
    target: Optional[str] = Field(None, description="目标地点或对象")
    reason: Optional[str] = Field(None, description="选择该行动的心理/逻辑理由")
    risk: Optional[str] = Field(None, description="可能的风险简述")
    priority: Optional[int] = Field(1, description="行动优先级(1-5)", ge=1, le=5)
    
    class Config:
        schema_extra = {
            "example": {
                "npc": "李四",
                "action": "move",
                "target": "kitchen",
                "reason": "听到厨房传来奇怪的声音，想去查看",
                "risk": "可能触发厨房的规则",
                "priority": 3
            }
        }


class TurnPlan(BaseModel):
    """回合计划：包含对话和行动"""
    dialogue: List[DialogueTurn] = Field(default_factory=list, description="NPC对话列表")
    actions: List[PlannedAction] = Field(default_factory=list, description="NPC行动列表")
    turn_summary: Optional[str] = Field(None, description="回合总结")
    atmosphere: Optional[str] = Field("tense", description="回合氛围")
    
    @validator("dialogue")
    def validate_dialogue_count(cls, v):
        if len(v) > 10:
            raise ValueError("单回合对话不应超过10条")
        return v
    
    @validator("actions")
    def validate_action_count(cls, v):
        if len(v) > 6:
            raise ValueError("单回合行动不应超过6个")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "dialogue": [
                    {"speaker": "张三", "text": "大家冷静！我们必须团结在一起！"},
                    {"speaker": "李四", "text": "这个房间的温度怎么突然变得这么冷..."}
                ],
                "actions": [
                    {"npc": "张三", "action": "search", "target": "desk", "reason": "寻找线索"}
                ],
                "turn_summary": "NPC们开始探索房间，气氛越发紧张",
                "atmosphere": "horror"
            }
        }


# ---------- 叙事 ----------
class NarrativeOut(BaseModel):
    """叙事输出"""
    narrative: str = Field(..., description="叙事文本")
    style: Optional[str] = Field("horror", description="叙事风格")
    word_count: Optional[int] = Field(None, description="字数统计")
    
    @validator("narrative")
    def enforce_len(cls, v):
        """确保叙事长度至少200字"""
        if len(v) < 200:
            v += "\n\n……夜色渐深，真正的恐怖才刚刚开始。"
        return v
    
    @validator("word_count", always=True)
    def calculate_word_count(cls, v, values):
        if "narrative" in values:
            return len(values["narrative"])
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "narrative": "夜幕降临，废弃公寓里的温度骤然下降。走廊尽头传来若有若无的脚步声...",
                "style": "horror",
                "word_count": 250
            }
        }


# ---------- 规则评估 ----------
class RuleTrigger(BaseModel):
    """规则触发器"""
    type: Literal["time", "location", "action", "item", "dialogue", "condition", "composite"] = Field(..., description="触发器类型")
    conditions: List[str] = Field(default_factory=list, description="触发条件列表")
    logic: Optional[Literal["AND", "OR"]] = Field("AND", description="条件逻辑关系")
    
    class Config:
        schema_extra = {
            "example": {
                "type": "time",
                "conditions": ["hour >= 22", "hour <= 6"],
                "logic": "AND"
            }
        }


class RuleEffect(BaseModel):
    """规则效果"""
    type: Literal["death", "injury", "fear", "sanity", "teleport", "transform", "reveal", "custom"] = Field(..., description="效果类型")
    params: Dict[str, Any] = Field(default_factory=dict, description="效果参数")
    description: Optional[str] = Field(None, description="效果描述")
    
    class Config:
        schema_extra = {
            "example": {
                "type": "death",
                "params": {"method": "心脏停止跳动", "instant": True},
                "description": "违反者将立即死亡"
            }
        }


class RuleEvalResult(BaseModel):
    """规则评估结果"""
    name: str = Field(..., description="规则名称")
    trigger: RuleTrigger = Field(..., description="规则触发器")
    effect: RuleEffect = Field(..., description="规则效果")
    cooldown: int = Field(0, description="冷却时间（秒）", ge=0)
    cost: int = Field(..., description="规则成本", ge=50, le=500)
    difficulty: int = Field(..., description="规则难度", ge=1, le=10)
    loopholes: List[str] = Field(default_factory=list, description="规则漏洞")
    suggestion: str = Field("", description="改进建议")
    estimated_fear_gain: Optional[int] = Field(None, description="预估恐惧值收益")
    
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
    
    @validator("loopholes")
    def limit_loopholes(cls, v):
        if len(v) > 5:
            return v[:5]  # 最多保留5个漏洞
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "午夜镜像",
                "trigger": {
                    "type": "composite",
                    "conditions": ["time == 00:00", "location == bathroom", "action == look_mirror"]
                },
                "effect": {
                    "type": "death",
                    "params": {"method": "被镜中的自己拖入"}
                },
                "cooldown": 3600,
                "cost": 300,
                "difficulty": 8,
                "loopholes": ["可以闭眼", "破碎的镜子无效"],
                "suggestion": "建议增加镜子完整性检测",
                "estimated_fear_gain": 150
            }
        }


# ---------- NPC状态 ----------
class NPCState(BaseModel):
    """NPC状态信息"""
    name: str = Field(..., description="NPC名字")
    fear: int = Field(..., description="恐惧值", ge=0, le=100)
    sanity: int = Field(..., description="理智值", ge=0, le=100)
    traits: List[str] = Field(default_factory=list, description="性格特征")
    status: str = Field("正常", description="当前状态")
    location: str = Field(..., description="当前位置")
    inventory: List[str] = Field(default_factory=list, description="携带物品")
    relationships: Dict[str, int] = Field(default_factory=dict, description="与其他NPC的关系值")
    
    @validator("traits")
    def limit_traits(cls, v):
        if len(v) > 3:
            return v[:3]  # 最多3个性格特征
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "张三",
                "fear": 35,
                "sanity": 80,
                "traits": ["谨慎", "理性", "领导力"],
                "status": "轻微恐慌",
                "location": "living_room",
                "inventory": ["手电筒", "笔记本"],
                "relationships": {"李四": 60, "王五": 40}
            }
        }


# ---------- 场景上下文 ----------
class SceneContext(BaseModel):
    """场景上下文信息"""
    current_location: str = Field(..., description="当前主要场景")
    time_of_day: str = Field(..., description="时间段")
    weather: Optional[str] = Field(None, description="天气状况")
    recent_events: List[str] = Field(default_factory=list, description="最近发生的事件")
    active_rules: List[str] = Field(default_factory=list, description="当前激活的规则")
    ambient_fear_level: int = Field(50, description="环境恐惧等级", ge=0, le=100)
    special_conditions: List[str] = Field(default_factory=list, description="特殊条件")
    
    @validator("recent_events")
    def limit_events(cls, v):
        return v[-5:]  # 只保留最近5条事件
    
    class Config:
        schema_extra = {
            "example": {
                "current_location": "abandoned_hospital",
                "time_of_day": "深夜",
                "weather": "雷雨",
                "recent_events": [
                    "张三发现了一本神秘日记",
                    "李四听到二楼传来脚步声",
                    "王五的手电筒突然熄灭"
                ],
                "active_rules": ["午夜镜像", "暗夜低语"],
                "ambient_fear_level": 75,
                "special_conditions": ["停电", "通讯中断"]
            }
        }


# ---------- API响应模型 ----------
class APIResponse(BaseModel):
    """统一API响应格式"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[Any] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {"message": "操作成功"},
                "error": None,
                "timestamp": "2024-12-20T10:30:00"
            }
        }


# ---------- 批量操作模型 ----------
class NPCBatchGenerateRequest(BaseModel):
    """批量生成NPC请求"""
    count: int = Field(..., description="生成数量", ge=1, le=10)
    trait_pool: Optional[List[str]] = Field(None, description="性格特征池")
    fear_range: Optional[tuple[int, int]] = Field((20, 60), description="恐惧值范围")
    sanity_range: Optional[tuple[int, int]] = Field((60, 90), description="理智值范围")
    
    @validator("fear_range", "sanity_range")
    def validate_range(cls, v):
        if v and (v[0] < 0 or v[1] > 100 or v[0] > v[1]):
            raise ValueError("范围必须在0-100之间，且最小值不能大于最大值")
        return v


class NPCBatchGenerateResponse(BaseModel):
    """批量生成NPC响应"""
    npcs: List[NPCState] = Field(..., description="生成的NPC列表")
    generation_time: float = Field(..., description="生成耗时（秒）")
    
    @validator("npcs")
    def validate_npcs(cls, v):
        if not v:
            raise ValueError("至少需要生成一个NPC")
        return v
