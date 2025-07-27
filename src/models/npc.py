"""
NPC系统数据模型
定义NPC的属性、行为和状态
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from enum import Enum
import random
import uuid


class NPCStatus(str, Enum):
    """NPC状态枚举"""
    NORMAL = "normal"
    FRIGHTENED = "frightened"
    PANICKED = "panicked"
    INSANE = "insane"
    DEAD = "dead"


class NPCAction(str, Enum):
    """NPC行动枚举"""
    MOVE = "move"
    INVESTIGATE = "investigate"
    TALK = "talk"
    HIDE = "hide"
    RUN = "run"
    USE_ITEM = "use_item"
    LOOK_AROUND = "look_around"
    TURN_AROUND = "turn_around"
    OPEN_DOOR = "open_door"
    LOOK_MIRROR = "look_mirror"


class NPCPersonality(BaseModel):
    """NPC性格特征"""
    rationality: int = Field(5, ge=1, le=10, description="理性程度")
    courage: int = Field(5, ge=1, le=10, description="勇气值")
    curiosity: int = Field(5, ge=1, le=10, description="好奇心")
    sociability: int = Field(5, ge=1, le=10, description="社交性")
    paranoia: int = Field(3, ge=1, le=10, description="偏执程度")
    
    def get_action_weights(self) -> Dict[NPCAction, float]:
        """根据性格返回行动权重"""
        weights = {
            NPCAction.MOVE: 0.3,
            NPCAction.INVESTIGATE: self.curiosity * 0.1,
            NPCAction.TALK: self.sociability * 0.1,
            NPCAction.HIDE: (10 - self.courage) * 0.05,
            NPCAction.RUN: (10 - self.courage) * 0.05,
            NPCAction.USE_ITEM: self.rationality * 0.05,
            NPCAction.LOOK_AROUND: 0.2,
            NPCAction.TURN_AROUND: 0.1,
            NPCAction.OPEN_DOOR: self.curiosity * 0.05,
            NPCAction.LOOK_MIRROR: self.curiosity * 0.03
        }
        return weights


class NPCMemory(BaseModel):
    """NPC记忆系统"""
    events: List[Dict[str, Any]] = Field(default_factory=list)
    known_rules: List[str] = Field(default_factory=list)
    suspicious_locations: List[str] = Field(default_factory=list)
    trusted_npcs: List[str] = Field(default_factory=list)
    feared_objects: List[str] = Field(default_factory=list)
    
    def add_event(self, event_type: str, details: Dict[str, Any]):
        """添加事件记忆"""
        self.events.append({
            "type": event_type,
            "details": details,
            "turn": details.get("turn", 0)
        })
        # 只保留最近20条记忆
        if len(self.events) > 20:
            self.events = self.events[-20:]
            
    def remember_rule(self, rule_id: str):
        """记住一条规则"""
        if rule_id not in self.known_rules:
            self.known_rules.append(rule_id)
            
    def has_seen_similar(self, event_type: str) -> bool:
        """是否见过类似事件"""
        return any(e["type"] == event_type for e in self.events)


class NPC(BaseModel):
    """NPC核心模型"""
    id: str = Field(default_factory=lambda: f"npc_{uuid.uuid4().hex[:8]}")
    name: str
    background: str = ""
    
    # 基础属性
    hp: int = Field(100, ge=0, le=100)
    sanity: int = Field(100, ge=0, le=100)
    stamina: int = Field(100, ge=0, le=100)
    
    # 状态值
    fear: int = Field(0, ge=0, le=100)
    suspicion: int = Field(0, ge=0, le=100)
    stress: int = Field(0, ge=0, le=100)
    
    # 性格
    personality: NPCPersonality = Field(default_factory=NPCPersonality)
    
    # 位置和状态
    location: str = "living_room"
    status: NPCStatus = NPCStatus.NORMAL
    is_alone: bool = False
    
    # 物品和记忆
    inventory: List[str] = Field(default_factory=list)
    memory: NPCMemory = Field(default_factory=NPCMemory)
    
    # 关系网络 (NPC_ID -> 信任度)
    relationships: Dict[str, int] = Field(default_factory=dict)
    
    # 行为修正
    action_modifiers: Dict[str, float] = Field(default_factory=dict)
    
    def update_status(self):
        """根据当前状态更新NPC状态"""
        if self.hp <= 0:
            self.status = NPCStatus.DEAD
        elif self.sanity <= 20:
            self.status = NPCStatus.INSANE
        elif self.fear >= 80:
            self.status = NPCStatus.PANICKED
        elif self.fear >= 50:
            self.status = NPCStatus.FRIGHTENED
        else:
            self.status = NPCStatus.NORMAL
            
    def take_damage(self, amount: int, damage_type: str = "physical"):
        """受到伤害"""
        self.hp = max(0, self.hp - amount)
        
        # 不同类型伤害的额外效果
        if damage_type == "mental":
            self.sanity = max(0, self.sanity - amount // 2)
        elif damage_type == "fear":
            self.add_fear(amount)
            
        self.update_status()
        
    def add_fear(self, amount: int):
        """增加恐惧值"""
        self.fear = min(100, self.fear + amount)
        
        # 恐惧影响理智
        if self.fear > 50:
            sanity_loss = (self.fear - 50) // 10
            self.sanity = max(0, self.sanity - sanity_loss)
            
        # 恐惧影响压力
        self.stress = min(100, self.stress + amount // 2)
        
        self.update_status()
        
    def reduce_fear(self, amount: int):
        """减少恐惧值"""
        self.fear = max(0, self.fear - amount)
        self.stress = max(0, self.stress - amount // 2)
        
    def can_act(self) -> bool:
        """是否可以行动"""
        return self.status not in [NPCStatus.DEAD, NPCStatus.INSANE] and self.stamina > 0
        
    def decide_action(self, context: Dict[str, Any]) -> NPCAction:
        """根据当前状态决定行动"""
        if not self.can_act():
            return None
            
        # 获取基础权重
        weights = self.personality.get_action_weights()
        
        # 根据状态调整权重
        if self.status == NPCStatus.PANICKED:
            weights[NPCAction.RUN] *= 3
            weights[NPCAction.HIDE] *= 2
            weights[NPCAction.INVESTIGATE] *= 0.1
            weights[NPCAction.MOVE] *= 2  # 恐慌时更想逃离
            
        elif self.status == NPCStatus.FRIGHTENED:
            weights[NPCAction.HIDE] *= 1.5
            weights[NPCAction.INVESTIGATE] *= 0.5
            weights[NPCAction.TALK] *= 1.5  # 寻求同伴
            weights[NPCAction.MOVE] *= 1.2  # 轻微增加移动倾向
            
        # 根据记忆调整
        if self.memory.feared_objects:
            weights[NPCAction.INVESTIGATE] *= 0.7
            
        if self.memory.suspicious_locations:
            # 如果当前位置是可疑地点，增加移动权重
            current_location = context.get("current_location")
            if current_location in self.memory.suspicious_locations:
                weights[NPCAction.MOVE] *= 2.5
                weights[NPCAction.RUN] *= 2
            
        # 根据关系调整
        nearby_npcs = context.get("nearby_npcs", [])
        if nearby_npcs:
            # 有信任的人在附近
            trusted_nearby = any(npc_id in self.relationships and self.relationships[npc_id] > 5 
                               for npc_id in nearby_npcs)
            if trusted_nearby:
                weights[NPCAction.TALK] *= 1.5
                weights[NPCAction.HIDE] *= 0.8
                weights[NPCAction.MOVE] *= 0.7  # 有信任的人在，不太想离开
        else:
            # 独自一人时
            self.is_alone = True
            if self.personality.sociability > 6:
                weights[NPCAction.MOVE] *= 1.3  # 社交型的人想找其他人
                
        # 体力影响
        if self.stamina < 30:
            weights[NPCAction.RUN] *= 0.3
            weights[NPCAction.MOVE] *= 0.7
            weights[NPCAction.HIDE] *= 1.5
                
        # 应用行为修正
        for action, modifier in self.action_modifiers.items():
            if action in weights:
                weights[action] *= modifier
                
        # 根据权重随机选择
        actions = list(weights.keys())
        probabilities = list(weights.values())
        total = sum(probabilities)
        probabilities = [p/total for p in probabilities]
        
        return random.choices(actions, weights=probabilities)[0]
        
    def interact_with(self, other_npc: 'NPC'):
        """与其他NPC互动"""
        # 初始化关系
        if other_npc.id not in self.relationships:
            # 基于性格的初始好感度
            initial_trust = 5 + (self.personality.sociability - 5) + (other_npc.personality.sociability - 5) // 2
            self.relationships[other_npc.id] = initial_trust
            
        # 互动影响
        if self.status == NPCStatus.FRIGHTENED and other_npc.status == NPCStatus.NORMAL:
            # 受惊吓时得到安慰
            self.reduce_fear(10)
            self.relationships[other_npc.id] += 1
            
        elif self.status == NPCStatus.NORMAL and other_npc.status == NPCStatus.PANICKED:
            # 看到别人恐慌也会害怕
            self.add_fear(15)
            
    def use_item(self, item: str) -> Dict[str, Any]:
        """使用物品"""
        if item not in self.inventory:
            return {"success": False, "message": "没有该物品"}
            
        result = {"success": True, "item": item}
        
        # 不同物品的效果
        if item == "flashlight":
            self.reduce_fear(10)
            result["message"] = "手电筒的光让你感觉安心了一些"
            
        elif item == "phone":
            if random.random() < 0.3:  # 30%概率没信号
                self.add_fear(5)
                result["message"] = "手机没有信号..."
            else:
                result["message"] = "你试图打电话求救"
                
        elif item == "medicine":
            self.sanity = min(100, self.sanity + 20)
            self.inventory.remove(item)
            result["message"] = "药物让你的精神稳定了一些"
            
        return result
        
    def observe_event(self, event_type: str, details: Dict[str, Any]):
        """观察到事件"""
        # 记录到记忆
        self.memory.add_event(event_type, details)
        
        # 不同事件的反应
        if event_type == "npc_death":
            self.add_fear(30)
            self.suspicion += 20
            
        elif event_type == "rule_triggered":
            # 可能学会规则
            if self.personality.rationality >= 7 and random.random() < 0.5:
                rule_id = details.get("rule_id")
                if rule_id:
                    self.memory.remember_rule(rule_id)
                    
        elif event_type == "strange_sound":
            self.add_fear(10)
            self.stress += 5
            
    def get_status_description(self) -> str:
        """获取状态描述"""
        desc = f"{self.name} ({self.status.value})"
        
        if self.hp < 50:
            desc += " [受伤]"
        if self.sanity < 50:
            desc += " [精神不稳]"
        if self.fear > 70:
            desc += " [极度恐惧]"
            
        return desc
        
    def choose_move_destination(self, current_area, available_areas, map_manager) -> Optional[str]:
        """选择移动目的地"""
        from src.models.map import AreaProperty
        
        if not available_areas:
            return None
            
        # 评估每个可用区域的吸引力
        area_scores = {}
        
        for area_id in available_areas:
            area = map_manager.get_area(area_id)
            if not area:
                continue
                
            score = 50  # 基础分数
            
            # 根据区域属性调整
            if AreaProperty.SAFE in area.properties:
                score += 30
            if AreaProperty.DANGEROUS in area.properties:
                score -= 40
            if AreaProperty.DARK in area.properties:
                score -= 20 * (10 - self.personality.courage) / 10
                
            # 根据其他NPC数量调整
            npc_count = len(area.current_npcs)
            if self.status == NPCStatus.PANICKED:
                # 恐慌时想远离人群
                score -= npc_count * 10
            elif self.personality.sociability > 5:
                # 社交型的人喜欢人多的地方
                score += npc_count * 5
            else:
                # 不太社交的人避免过于拥挤
                if npc_count > 3:
                    score -= (npc_count - 3) * 5
                    
            # 根据记忆调整
            if area_id in self.memory.suspicious_locations:
                score -= 50
            if area.area_type.value in ["bathroom", "basement"]:
                # 危险区域类型
                score -= 20
                
            # 体力影响（远的地方分数低）
            if self.stamina < 50:
                # 简单距离计算（直接连接为1，否则为2）
                if area_id not in current_area.connections.values():
                    score -= 20
                    
            area_scores[area_id] = max(0, score)
            
        # 根据分数加权随机选择
        if not area_scores:
            return None
            
        areas = list(area_scores.keys())
        scores = list(area_scores.values())
        total_score = sum(scores)
        
        if total_score == 0:
            # 所有地方都不想去，随机选一个
            return random.choice(areas)
            
        probabilities = [s/total_score for s in scores]
        return random.choices(areas, weights=probabilities)[0]
        
    def perform_move(self, distance: int = 1):
        """执行移动，消耗体力"""
        stamina_cost = 5 * distance
        if self.status == NPCStatus.PANICKED:
            stamina_cost *= 1.5  # 恐慌时消耗更多
        elif self.status == NPCStatus.FRIGHTENED:
            stamina_cost *= 1.2
            
        self.stamina = max(0, self.stamina - int(stamina_cost))
        
        # 体力过低可能影响状态
        if self.stamina == 0:
            self.add_fear(10)
            self.stress += 15
            
    def enter_area(self, area_id: str, area_properties: List[str]):
        """进入新区域的反应"""
        # 记录位置
        self.location = area_id
        
        # 根据区域属性产生反应
        if "dark" in area_properties and self.personality.courage < 5:
            self.add_fear(5)
        if "cold" in area_properties:
            self.stress += 5
        if "safe" in area_properties:
            self.reduce_fear(5)
            
    class Config:
        """Pydantic配置"""
        use_enum_values = True


# NPC名字池
NPC_NAMES = [
    "小明", "小红", "张伟", "李静", "王芳", "刘洋",
    "陈晨", "赵雷", "孙悦", "周涛", "吴敏", "郑浩",
    "老王", "小李", "阿姨", "大叔", "小妹", "老张"
]

# NPC背景模板
NPC_BACKGROUNDS = [
    "大学生，放假回家探亲",
    "上班族，加班到深夜",
    "保安，负责夜班巡逻",
    "清洁工，打扫这栋建筑",
    "记者，调查灵异事件",
    "探险爱好者，寻求刺激",
    "普通居民，不小心卷入",
    "外卖员，送餐时被困"
]


def generate_random_npc(name: Optional[str] = None) -> NPC:
    """生成随机NPC"""
    if not name:
        name = random.choice(NPC_NAMES)
        
    background = random.choice(NPC_BACKGROUNDS)
    
    # 随机性格
    personality = NPCPersonality(
        rationality=random.randint(3, 8),
        courage=random.randint(2, 8),
        curiosity=random.randint(3, 9),
        sociability=random.randint(2, 8),
        paranoia=random.randint(1, 6)
    )
    
    # 随机初始物品
    possible_items = ["flashlight", "phone", "key", "medicine", "knife", "rope"]
    inventory = random.sample(possible_items, random.randint(0, 2))
    
    return NPC(
        name=name,
        background=background,
        personality=personality,
        inventory=inventory,
        hp=random.randint(80, 100),
        sanity=random.randint(70, 100),
        stamina=random.randint(80, 100)
    )


# 测试代码
if __name__ == "__main__":
    # 创建测试NPC
    npc1 = generate_random_npc("测试员A")
    npc2 = generate_random_npc("测试员B")
    
    print(f"NPC创建: {npc1.name}")
    print(f"性格: 理性{npc1.personality.rationality} 勇气{npc1.personality.courage}")
    print(f"物品: {npc1.inventory}")
    
    # 测试行动决策
    context = {"nearby_npcs": [npc2.id]}
    action = npc1.decide_action(context)
    print(f"\n决定执行: {action}")
    
    # 测试互动
    npc1.interact_with(npc2)
    print(f"与{npc2.name}的关系: {npc1.relationships.get(npc2.id, 0)}")
    
    # 测试恐惧系统
    npc1.add_fear(60)
    print(f"\n增加恐惧后状态: {npc1.get_status_description()}")
    
    # 测试记忆系统
    npc1.observe_event("strange_sound", {"location": "corridor", "turn": 1})
    print(f"记忆事件数: {len(npc1.memory.events)}")
