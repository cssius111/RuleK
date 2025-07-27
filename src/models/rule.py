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


# 示例规则模板
RULE_TEMPLATES = {
    "mirror_death": {
        "name": "午夜照镜死",
        "description": "在午夜时分照镜子会被镜中的恶灵拖入镜中世界",
        "trigger": {
            "action": "look_mirror",
            "time_range": {"from": "00:00", "to": "04:00"},
            "location": ["bathroom", "bedroom"],
            "extra_conditions": ["lights_off"],
            "probability": 0.8
        },
        "requirements": {
            "items": ["mirror"],
            "min_fear_level": 0
        },
        "effect": {
            "type": "instant_death",
            "fear_gain": 200,
            "side_effects": ["blood_on_mirror", "scream_heard"]
        },
        "loopholes": [
            {
                "id": "eyes_closed",
                "description": "闭着眼睛照镜子不会触发",
                "discovery_difficulty": 3,
                "patch_cost": 150
            },
            {
                "id": "broken_mirror",
                "description": "破碎的镜子无效",
                "discovery_difficulty": 5,
                "patch_cost": 200
            }
        ],
        "base_cost": 150,
        "detectable": True,
        "reverse_risk": 0.2
    },
    
    "red_word_taboo": {
        "name": "红字禁忌",
        "description": "说出特定词语会触发诅咒",
        "trigger": {
            "action": "speak_word",
            "probability": 1.0
        },
        "requirements": {},
        "effect": {
            "type": "sanity_loss",
            "params": {"amount": 30},
            "fear_gain": 50,
            "side_effects": ["temperature_drop", "lights_flicker"]
        },
        "loopholes": [
            {
                "id": "write_instead",
                "description": "写出来而不是说出来不会触发",
                "discovery_difficulty": 4,
                "patch_cost": 100
            }
        ],
        "base_cost": 80,
        "maintenance_cost": 5
    },
    
    # 新增规则模板
    "phone_ring_death": {
        "name": "电话铃声",
        "description": "深夜电话响起，接听者会在七天后消失",
        "trigger": {
            "action": "use_item",
            "time_range": {"from": "23:00", "to": "03:00"},
            "extra_conditions": ["phone_ringing"],
            "probability": 0.9
        },
        "requirements": {
            "items": ["phone"]
        },
        "effect": {
            "type": "trigger_event",
            "params": {"event": "delayed_death", "delay_turns": 7},
            "fear_gain": 100,
            "side_effects": ["static_noise", "cold_voice"]
        },
        "loopholes": [
            {
                "id": "dont_answer",
                "description": "不接听电话就不会触发",
                "discovery_difficulty": 2,
                "patch_cost": 80
            },
            {
                "id": "speaker_mode",
                "description": "使用扬声器模式可以避免",
                "discovery_difficulty": 6,
                "patch_cost": 120
            }
        ],
        "base_cost": 120,
        "detectable": True,
        "reverse_risk": 0.15
    },
    
    "group_hallucination": {
        "name": "群体幻觉",
        "description": "3人以上在同一房间时会集体发疯",
        "trigger": {
            "action": "move",
            "location": ["living_room", "bedroom_a", "bedroom_b"],
            "extra_conditions": ["npc_count >= 3"],
            "probability": 0.7
        },
        "requirements": {
            "min_fear_level": 30
        },
        "effect": {
            "type": "sanity_loss",
            "params": {"amount": 50, "target": "all_in_room"},
            "fear_gain": 150,
            "side_effects": ["shared_vision", "synchronized_movement"]
        },
        "loopholes": [
            {
                "id": "stay_separated",
                "description": "保持分散，每个房间不超过2人",
                "discovery_difficulty": 3,
                "patch_cost": 100
            },
            {
                "id": "close_eyes",
                "description": "所有人同时闭眼可以抵抗",
                "discovery_difficulty": 7,
                "patch_cost": 180
            }
        ],
        "base_cost": 180,
        "maintenance_cost": 10
    },
    
    "shadow_mimic": {
        "name": "影子模仿",
        "description": "做出特定动作后，影子会延迟模仿并攻击",
        "trigger": {
            "action": "turn_around",
            "location": ["corridor", "living_room"],
            "extra_conditions": ["has_shadow"],
            "probability": 0.6
        },
        "requirements": {
            "min_fear_level": 40
        },
        "effect": {
            "type": "instant_death",
            "params": {"delay": 3},
            "fear_gain": 180,
            "side_effects": ["shadow_movement", "delayed_attack"]
        },
        "loopholes": [
            {
                "id": "no_light_no_shadow",
                "description": "在完全黑暗中没有影子",
                "discovery_difficulty": 4,
                "patch_cost": 140
            },
            {
                "id": "constant_movement",
                "description": "保持移动不让影子跟上",
                "discovery_difficulty": 5,
                "patch_cost": 160
            }
        ],
        "base_cost": 200,
        "detectable": True,
        "reverse_risk": 0.25
    },
    
    "door_knock_pattern": {
        "name": "敲门死",
        "description": "听到特定节奏的敲门声后开门会死亡",
        "trigger": {
            "action": "open_door",
            "extra_conditions": ["heard_knock_pattern"],
            "probability": 0.85
        },
        "requirements": {},
        "effect": {
            "type": "instant_death",
            "fear_gain": 160,
            "side_effects": ["door_slam", "void_entrance"]
        },
        "loopholes": [
            {
                "id": "ignore_knocks",
                "description": "不管敲门声，不开门",
                "discovery_difficulty": 2,
                "patch_cost": 90
            },
            {
                "id": "wrong_pattern",
                "description": "只有特定节奏才危险",
                "discovery_difficulty": 6,
                "patch_cost": 130
            }
        ],
        "base_cost": 140,
        "detectable": True
    },
    
    "item_curse": {
        "name": "物品诅咒",
        "description": "拿起特定物品会被诅咒缠身",
        "trigger": {
            "action": "use_item",
            "extra_conditions": ["cursed_item"],
            "probability": 0.9
        },
        "requirements": {
            "items": ["knife", "diary", "key"]
        },
        "effect": {
            "type": "fear_gain",
            "params": {"continuous": True, "amount_per_turn": 10},
            "fear_gain": 80,
            "side_effects": ["item_stuck", "whispers"]
        },
        "loopholes": [
            {
                "id": "gloves",
                "description": "戴手套拿取不会触发",
                "discovery_difficulty": 5,
                "patch_cost": 110
            },
            {
                "id": "drop_immediately",
                "description": "立即丢弃可以解除",
                "discovery_difficulty": 3,
                "patch_cost": 70
            }
        ],
        "base_cost": 100,
        "maintenance_cost": 8
    },
    
    "memory_erasure": {
        "name": "记忆删除",
        "description": "进入特定房间会忘记之前的所有规则",
        "trigger": {
            "action": "move",
            "location": ["basement"],
            "probability": 0.75
        },
        "requirements": {
            "min_fear_level": 50
        },
        "effect": {
            "type": "trigger_event",
            "params": {"event": "memory_wipe", "target": "rules"},
            "fear_gain": 60,
            "side_effects": ["confusion", "headache"]
        },
        "loopholes": [
            {
                "id": "write_notes",
                "description": "写下规则笔记携带",
                "discovery_difficulty": 4,
                "patch_cost": 95
            },
            {
                "id": "dont_enter",
                "description": "不要进入该房间",
                "discovery_difficulty": 1,
                "patch_cost": 50
            }
        ],
        "base_cost": 90,
        "detectable": True
    },
    
    "chain_reaction": {
        "name": "连锁反应",
        "description": "一人死亡会触发同房间其他人的死亡倒计时",
        "trigger": {
            "action": "witness_death",
            "extra_conditions": ["same_room"],
            "probability": 0.8
        },
        "requirements": {
            "min_fear_level": 60
        },
        "effect": {
            "type": "trigger_event",
            "params": {"event": "death_timer", "countdown": 5},
            "fear_gain": 200,
            "side_effects": ["panic_spread", "countdown_visible"]
        },
        "loopholes": [
            {
                "id": "leave_room",
                "description": "立即离开房间",
                "discovery_difficulty": 3,
                "patch_cost": 120
            },
            {
                "id": "break_sight",
                "description": "不看死者就不会触发",
                "discovery_difficulty": 5,
                "patch_cost": 150
            }
        ],
        "base_cost": 220,
        "detectable": True,
        "reverse_risk": 0.3
    },
    
    "bathroom_trap": {
        "name": "浴室陷阱",
        "description": "在浴室待超过3分钟会被困住",
        "trigger": {
            "action": "stay_in_room",
            "location": ["bathroom"],
            "extra_conditions": ["duration > 3"],
            "probability": 0.9
        },
        "requirements": {},
        "effect": {
            "type": "teleport",
            "params": {"destination": "void", "trap_duration": 10},
            "fear_gain": 120,
            "side_effects": ["door_locked", "water_rising"]
        },
        "loopholes": [
            {
                "id": "quick_visit",
                "description": "快速进出，不超过3分钟",
                "discovery_difficulty": 2,
                "patch_cost": 80
            },
            {
                "id": "keep_door_open",
                "description": "保持门开着",
                "discovery_difficulty": 4,
                "patch_cost": 100
            }
        ],
        "base_cost": 110,
        "maintenance_cost": 6
    },
    
    "light_switch_death": {
        "name": "开关灯死",
        "description": "连续3次开关灯会召唤黑暗中的东西",
        "trigger": {
            "action": "use_item",
            "extra_conditions": ["light_switch", "count >= 3"],
            "probability": 0.95
        },
        "requirements": {},
        "effect": {
            "type": "spawn_spirit",
            "params": {"spirit_type": "shadow_beast", "aggressive": True},
            "fear_gain": 180,
            "side_effects": ["permanent_darkness", "growling"]
        },
        "loopholes": [
            {
                "id": "count_switches",
                "description": "记住只开关两次",
                "discovery_difficulty": 2,
                "patch_cost": 70
            },
            {
                "id": "use_flashlight",
                "description": "使用手电筒代替",
                "discovery_difficulty": 3,
                "patch_cost": 90
            }
        ],
        "base_cost": 160,
        "detectable": True,
        "reverse_risk": 0.2
    }
}


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
