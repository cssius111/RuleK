"""
规则系统数据模型
定义游戏中所有规则相关的数据结构
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class EffectType(str, Enum):
    """规则效果类型枚举"""
    INSTANT_DEATH = "instant_death"
    FEAR_GAIN = "fear_gain"
    SANITY_LOSS = "sanity_loss"
    TELEPORT = "teleport"
    TRANSFORM = "transform"
    SPAWN_SPIRIT = "spawn_spirit"
    TRIGGER_EVENT = "trigger_event"


class TriggerCondition(BaseModel):
    """触发条件模型"""
    action: str = Field(..., description="触发动作，如look_mirror, open_door")
    time_range: Optional[Dict[str, str]] = Field(None, description="触发时间范围")
    location: Optional[List[str]] = Field(None, description="触发地点列表")
    extra_conditions: List[str] = Field(default_factory=list, description="额外条件")
    probability: float = Field(0.8, ge=0.0, le=1.0, description="基础触发概率")
    
    @field_validator('time_range')
    @classmethod
    def validate_time_range(cls, v):
        if v and ('from' not in v or 'to' not in v):
            raise ValueError("time_range必须包含'from'和'to'字段")
        return v


class RuleRequirement(BaseModel):
    """规则前置要求"""
    items: List[str] = Field(default_factory=list, description="需要的物品")
    areas: List[str] = Field(default_factory=list, description="限定区域")
    min_fear_level: int = Field(0, ge=0, description="最小恐惧等级要求")
    actor_traits: Dict[str, Any] = Field(default_factory=dict, description="触发者特质要求")


class RuleEffect(BaseModel):
    """规则效果定义"""
    type: EffectType
    params: Dict[str, Any] = Field(default_factory=dict, description="效果参数")
    fear_gain: int = Field(0, ge=0, description="获得的恐惧积分")
    side_effects: List[str] = Field(default_factory=list, description="副作用列表")
    delay: int = Field(0, ge=0, description="延迟回合数")


class Loophole(BaseModel):
    """规则破绽"""
    id: str
    description: str
    discovery_difficulty: int = Field(5, ge=1, le=10, description="发现难度")
    patch_cost: int = Field(100, ge=0, description="修补成本")
    patched: bool = False
    auto_discovered_after: Optional[int] = Field(None, description="多少回合后自动发现")


class Rule(BaseModel):
    """游戏规则核心模型"""
    id: str = Field(..., description="规则唯一ID")
    name: str = Field(..., min_length=1, max_length=50, description="规则名称")
    description: str = Field("", description="规则描述")
    level: int = Field(1, ge=1, le=10, description="规则等级")
    
    # 创建信息
    creator: str = Field("system", description="创建者：system/player")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # 触发系统
    requirements: RuleRequirement = Field(default_factory=RuleRequirement)
    trigger: TriggerCondition
    
    # 效果系统
    effect: RuleEffect
    
    # 成本系统
    base_cost: int = Field(100, ge=0, description="基础成本")
    maintenance_cost: int = Field(0, ge=0, description="每回合维护成本")
    
    # 破绽系统
    loopholes: List[Loophole] = Field(default_factory=list, description="规则破绽列表")
    detectable: bool = Field(True, description="是否可被推理发现")
    reverse_risk: float = Field(0.1, ge=0.0, le=1.0, description="被反利用风险")
    
    # 状态
    active: bool = True
    cooldown_turns: int = Field(0, ge=0, description="冷却回合数")
    times_triggered: int = Field(0, ge=0, description="已触发次数")
    times_discovered: int = Field(0, ge=0, description="被发现次数")
    
    # 升级路径
    upgrade_options: List[str] = Field(default_factory=list, description="可用升级选项")
    
    def calculate_total_cost(self) -> int:
        """计算规则总成本"""
        level_modifier = self.level * 50
        loophole_discount = len([l for l in self.loopholes if not l.patched]) * 20
        complexity_cost = len(self.requirements.items) * 10 + len(self.requirements.areas) * 15
        
        return max(50, self.base_cost + level_modifier + complexity_cost - loophole_discount)
    
    def can_trigger(self, context: Dict[str, Any]) -> bool:
        """检查规则是否可以触发"""
        if not self.active or self.cooldown_turns > 0:
            return False
            
        # 检查时间条件
        if self.trigger.time_range:
            current_time = context.get('current_time', '00:00')
            try:
                current = int(current_time.replace(":", ""))
                start = int(self.trigger.time_range["from"].replace(":", ""))
                end = int(self.trigger.time_range["to"].replace(":", ""))

                if start <= end:
                    if not (start <= current <= end):
                        return False
                else:
                    if not (current >= start or current <= end):
                        return False
            except Exception:
                return False
            
        # 检查地点条件
        if self.trigger.location:
            actor_location = context.get('actor_location')
            if actor_location not in self.trigger.location:
                return False
                
        # 检查物品需求
        if self.requirements.items:
            actor_items = context.get('actor_items', [])
            if not all(item in actor_items for item in self.requirements.items):
                return False
                
        return True
    
    def apply_effect(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """应用规则效果"""
        result = {
            'success': True,
            'effect_type': self.effect.type,
            'fear_gained': self.effect.fear_gain,
            'messages': []
        }
        
        # 根据效果类型处理
        if self.effect.type == EffectType.INSTANT_DEATH:
            result['target_died'] = True
            result['messages'].append(f"{target.get('name', '某人')}触发了{self.name}，当场死亡！")
            
        elif self.effect.type == EffectType.SANITY_LOSS:
            loss = self.effect.params.get('amount', 20)
            result['sanity_loss'] = loss
            result['messages'].append(f"理智值下降{loss}点")
            
        # 处理副作用
        for side_effect in self.effect.side_effects:
            result['side_effects'] = result.get('side_effects', [])
            result['side_effects'].append(side_effect)
            
        # 更新触发计数
        self.times_triggered += 1
        
        # 设置冷却
        if hasattr(self, 'cooldown_after_trigger'):
            self.cooldown_turns = self.cooldown_after_trigger
            
        return result
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


# 规则模板加载
def load_rule_templates(path: str = "data/rule_templates.json") -> Dict[str, Any]:
    """从指定JSON文件加载规则模板"""
    from pathlib import Path
    import json

    file_path = Path(path)
    if not file_path.exists():
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}


RULE_TEMPLATES = load_rule_templates()


if __name__ == "__main__":
    # 测试规则创建
    mirror_rule = Rule(
        id="rule_001",
        name="午夜照镜死",
        trigger=TriggerCondition(
            action="look_mirror",
            time_range={"from": "00:00", "to": "04:00"},
            location=["bathroom"]
        ),
        effect=RuleEffect(
            type=EffectType.INSTANT_DEATH,
            fear_gain=200
        )
    )
    
    print(f"规则创建成功: {mirror_rule.name}")
    print(f"总成本: {mirror_rule.calculate_total_cost()}")
    
    # 测试触发条件
    context = {
        "current_time": "01:30",
        "actor_location": "bathroom",
        "actor_items": ["mirror"]
    }
    
    if mirror_rule.can_trigger(context):
        print("规则可以触发！")
        result = mirror_rule.apply_effect({"name": "测试玩家"})
        print(f"效果: {result}")
