"""
NPC行为系统
实现NPC的AI行为逻辑
"""
import random
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

from ..core.game_state import GameStateManager
from ..utils.logger import get_logger

logger = get_logger(__name__)


class NPCAction(str, Enum):
    """NPC行为枚举"""
    MOVE = "move"
    INVESTIGATE = "investigate"
    TALK = "talk"
    USE_ITEM = "use_item"
    PICK_UP = "pick_up"
    REST = "rest"
    HIDE = "hide"
    ESCAPE = "escape"
    LOOK_MIRROR = "look_mirror"
    TURN_AROUND = "turn_around"
    OPEN_DOOR = "open_door"
    SEARCH = "search"


@dataclass
class ActionDecision:
    """行动决策"""
    action: NPCAction
    target: Optional[str] = None
    priority: float = 0.5
    reason: str = ""


class NPCBehavior:
    """NPC行为控制器"""
    
    def __init__(self, game_manager: GameStateManager):
        self.game_manager = game_manager
        self.action_history = {}  # NPC行动历史
        
    def decide_action(self, npc: Dict) -> ActionDecision:
        """决定NPC的下一个行动"""
        # 检查NPC状态
        if not npc.get("alive", True):
            return ActionDecision(NPCAction.REST, reason="已死亡")
            
        # 获取NPC的性格特质
        personality = self._get_personality_profile(npc)
        
        # 根据当前状态计算行动权重
        action_weights = self._calculate_action_weights(npc, personality)
        
        # 选择行动
        action = self._select_action(action_weights)
        
        # 确定行动目标
        target = self._determine_action_target(npc, action)
        
        # 记录决策
        decision = ActionDecision(
            action=action,
            target=target,
            priority=action_weights.get(action, 0),
            reason=self._get_action_reason(npc, action)
        )
        
        # 保存到历史
        if npc["id"] not in self.action_history:
            self.action_history[npc["id"]] = []
        self.action_history[npc["id"]].append({
            "turn": self.game_manager.state.turn,
            "action": action.value,
            "target": target
        })
        
        logger.debug(f"{npc['name']} 决定: {action.value} (原因: {decision.reason})")
        
        return decision
        
    def _get_personality_profile(self, npc: Dict) -> Dict[str, float]:
        """获取NPC性格特征"""
        return {
            "rationality": npc.get("rationality", 5) / 10,
            "courage": npc.get("courage", 5) / 10,
            "curiosity": npc.get("curiosity", 5) / 10,
            "sociability": npc.get("sociability", 5) / 10,
        }
        
    def _calculate_action_weights(self, npc: Dict, personality: Dict) -> Dict[NPCAction, float]:
        """计算各种行动的权重"""
        weights = {}
        
        # 基础权重
        base_weights = {
            NPCAction.MOVE: 0.3,
            NPCAction.INVESTIGATE: 0.2,
            NPCAction.TALK: 0.15,
            NPCAction.REST: 0.15,
            NPCAction.SEARCH: 0.1,
            NPCAction.USE_ITEM: 0.05,
            NPCAction.PICK_UP: 0.05,
        }
        
        # 根据状态调整权重
        fear = npc.get("fear", 0) / 100
        sanity = npc.get("sanity", 100) / 100
        stamina = npc.get("stamina", 100) / 100
        suspicion = npc.get("suspicion", 0) / 100
        
        # 恐惧影响
        if fear > 0.5:
            weights[NPCAction.HIDE] = 0.3 * fear
            weights[NPCAction.ESCAPE] = 0.4 * fear
            weights[NPCAction.INVESTIGATE] = base_weights[NPCAction.INVESTIGATE] * (1 - fear)
        else:
            weights[NPCAction.INVESTIGATE] = base_weights[NPCAction.INVESTIGATE]
            
        # 理智影响
        if sanity < 0.5:
            # 低理智时更容易做出危险行为
            weights[NPCAction.LOOK_MIRROR] = 0.1 * (1 - sanity)
            weights[NPCAction.TURN_AROUND] = 0.1 * (1 - sanity)
            weights[NPCAction.TALK] = base_weights[NPCAction.TALK] * sanity
        else:
            weights[NPCAction.TALK] = base_weights[NPCAction.TALK]
            
        # 体力影响
        if stamina < 0.3:
            weights[NPCAction.REST] = 0.5
            weights[NPCAction.MOVE] = base_weights[NPCAction.MOVE] * stamina
        else:
            weights[NPCAction.MOVE] = base_weights[NPCAction.MOVE]
            weights[NPCAction.REST] = base_weights[NPCAction.REST]
            
        # 怀疑度影响
        if suspicion > 0.5:
            weights[NPCAction.INVESTIGATE] = base_weights[NPCAction.INVESTIGATE] * 1.5
            weights[NPCAction.SEARCH] = base_weights[NPCAction.SEARCH] * 2
            
        # 性格影响
        weights[NPCAction.INVESTIGATE] = weights.get(NPCAction.INVESTIGATE, 0.2) * (0.5 + personality["curiosity"])
        weights[NPCAction.TALK] = weights.get(NPCAction.TALK, 0.15) * (0.5 + personality["sociability"])
        weights[NPCAction.HIDE] = weights.get(NPCAction.HIDE, 0) * (1.5 - personality["courage"])
        
        # 根据位置添加特定行动
        location = npc.get("location", "")
        if location == "bathroom":
            weights[NPCAction.LOOK_MIRROR] = weights.get(NPCAction.LOOK_MIRROR, 0) + 0.1
        if location == "corridor":
            weights[NPCAction.TURN_AROUND] = weights.get(NPCAction.TURN_AROUND, 0) + 0.05
            
        # 归一化权重
        total = sum(weights.values())
        if total > 0:
            for action in weights:
                weights[action] /= total
                
        # 补充缺失的基础行动
        for action, weight in base_weights.items():
            if action not in weights:
                weights[action] = weight * 0.1
                
        return weights
        
    def _select_action(self, weights: Dict[NPCAction, float]) -> NPCAction:
        """根据权重选择行动"""
        if not weights:
            return NPCAction.REST
            
        actions = list(weights.keys())
        probabilities = list(weights.values())
        
        # 使用轮盘赌选择
        return random.choices(actions, weights=probabilities)[0]
        
    def _determine_action_target(self, npc: Dict, action: NPCAction) -> Optional[str]:
        """确定行动目标"""
        if action == NPCAction.MOVE:
            # 选择相邻房间
            return self._get_adjacent_room(npc.get("location"))
            
        elif action == NPCAction.TALK:
            # 选择同房间的其他NPC
            others = self.game_manager.get_npcs_in_location(npc.get("location"))
            others = [o for o in others if o["id"] != npc["id"] and o.get("alive", True)]
            if others:
                return random.choice(others)["id"]
                
        elif action == NPCAction.USE_ITEM:
            # 选择背包中的物品
            inventory = npc.get("inventory", [])
            if inventory:
                return random.choice(inventory)
                
        elif action == NPCAction.INVESTIGATE:
            # 选择房间中的可疑对象
            return self._get_investigation_target(npc.get("location"))
            
        return None
        
    def _get_adjacent_room(self, current_location: str) -> str:
        """获取相邻房间"""
        # 简单的房间连接图
        connections = {
            "living_room": ["corridor", "kitchen"],
            "corridor": ["living_room", "bedroom_a", "bedroom_b", "bathroom"],
            "bedroom_a": ["corridor"],
            "bedroom_b": ["corridor"],
            "bathroom": ["corridor"],
            "kitchen": ["living_room"],
        }
        
        adjacent = connections.get(current_location, [])
        if adjacent:
            return random.choice(adjacent)
        return current_location
        
    def _get_investigation_target(self, location: str) -> str:
        """获取调查目标"""
        # 每个房间的可调查对象
        objects = {
            "bathroom": ["mirror", "bathtub", "cabinet"],
            "bedroom_a": ["bed", "wardrobe", "desk"],
            "bedroom_b": ["bed", "wardrobe", "window"],
            "kitchen": ["refrigerator", "stove", "cupboard"],
            "living_room": ["sofa", "tv", "bookshelf"],
            "corridor": ["paintings", "doors", "floor"],
        }
        
        room_objects = objects.get(location, ["wall", "floor"])
        return random.choice(room_objects)
        
    def _get_action_reason(self, npc: Dict, action: NPCAction) -> str:
        """获取行动原因说明"""
        reasons = {
            NPCAction.MOVE: "想要换个地方",
            NPCAction.INVESTIGATE: "感觉有些不对劲",
            NPCAction.TALK: "需要和其他人交流",
            NPCAction.REST: "感到疲惫",
            NPCAction.HIDE: "太害怕了",
            NPCAction.ESCAPE: "想要逃离这里",
            NPCAction.LOOK_MIRROR: "被镜子吸引",
            NPCAction.TURN_AROUND: "听到身后有声音",
            NPCAction.SEARCH: "寻找线索",
        }
        
        # 根据状态补充原因
        if npc.get("fear", 0) > 70:
            return f"{reasons.get(action, '本能反应')}（极度恐惧）"
        elif npc.get("sanity", 100) < 30:
            return f"{reasons.get(action, '失去理智')}（精神错乱）"
            
        return reasons.get(action, "随机行动")
        
    def execute_action(self, npc: Dict, decision: ActionDecision) -> Dict:
        """执行NPC行动"""
        result = {
            "success": True,
            "action": decision.action.value,
            "messages": []
        }
        
        # 根据行动类型执行
        if decision.action == NPCAction.MOVE:
            if decision.target:
                old_location = npc.get("location")
                self.game_manager.update_npc(npc["id"], {"location": decision.target})
                result["messages"].append(f"{npc['name']} 从 {old_location} 移动到 {decision.target}")
                
        elif decision.action == NPCAction.TALK:
            if decision.target:
                target_npc = self.game_manager.state.npcs.get(decision.target)
                if target_npc:
                    result["messages"].append(f"{npc['name']} 与 {target_npc['name']} 交谈")
                    # 降低双方的恐惧和怀疑
                    self.game_manager.update_npc(npc["id"], {
                        "fear": max(0, npc.get("fear", 0) - 5),
                        "suspicion": max(0, npc.get("suspicion", 0) - 3)
                    })
                    
        elif decision.action == NPCAction.REST:
            # 恢复体力
            self.game_manager.update_npc(npc["id"], {
                "stamina": min(100, npc.get("stamina", 100) + 20)
            })
            result["messages"].append(f"{npc['name']} 休息了一会儿")
            
        elif decision.action == NPCAction.INVESTIGATE:
            # 增加怀疑度，可能发现线索
            self.game_manager.update_npc(npc["id"], {
                "suspicion": min(100, npc.get("suspicion", 0) + 10)
            })
            result["messages"].append(f"{npc['name']} 调查了 {decision.target}")
            
        # 消耗体力
        stamina_cost = {
            NPCAction.MOVE: 5,
            NPCAction.INVESTIGATE: 10,
            NPCAction.ESCAPE: 20,
            NPCAction.HIDE: 3,
            NPCAction.TALK: 2,
        }.get(decision.action, 1)
        
        new_stamina = max(0, npc.get("stamina", 100) - stamina_cost)
        self.game_manager.update_npc(npc["id"], {"stamina": new_stamina})
        
        return result
        
    def get_npc_memory(self, npc_id: str) -> List[Dict]:
        """获取NPC的记忆/行动历史"""
        return self.action_history.get(npc_id, [])[-10:]  # 最近10个行动
        
    def update_npc_relationships(self, npc1_id: str, npc2_id: str, change: int):
        """更新NPC之间的关系"""
        npc1 = self.game_manager.state.npcs.get(npc1_id)
        if npc1:
            relationships = npc1.get("relationships", {})
            current = relationships.get(npc2_id, 50)  # 默认中立
            new_value = max(0, min(100, current + change))
            relationships[npc2_id] = new_value
            self.game_manager.update_npc(npc1_id, {"relationships": relationships})
            
    def get_behavior_stats(self) -> Dict:
        """获取行为统计"""
        stats = {
            "total_actions": sum(len(history) for history in self.action_history.values()),
            "active_npcs": len([npc for npc in self.game_manager.state.npcs.values() 
                               if npc.get("alive", True)]),
            "most_common_action": None,
            "location_distribution": {}
        }
        
        # 统计最常见的行动
        action_counts = {}
        for history in self.action_history.values():
            for record in history:
                action = record["action"]
                action_counts[action] = action_counts.get(action, 0) + 1
                
        if action_counts:
            most_common = max(action_counts.items(), key=lambda x: x[1])
            stats["most_common_action"] = {"action": most_common[0], "count": most_common[1]}
            
        # 统计位置分布
        for npc in self.game_manager.state.npcs.values():
            if npc.get("alive", True):
                loc = npc.get("location", "unknown")
                stats["location_distribution"][loc] = stats["location_distribution"].get(loc, 0) + 1
                
        return stats


if __name__ == "__main__":
    # 测试代码
    from ..core.game_state import GameStateManager
    
    # 创建游戏管理器
    game_manager = GameStateManager()
    game_manager.new_game()
    
    # 创建行为控制器
    behavior = NPCBehavior(game_manager)
    
    # 测试每个NPC的行为决策
    for npc_id, npc in game_manager.state.npcs.items():
        print(f"\n{npc['name']} 的行为决策:")
        
        # 决定行动
        decision = behavior.decide_action(npc)
        print(f"  行动: {decision.action.value}")
        print(f"  目标: {decision.target}")
        print(f"  原因: {decision.reason}")
        
        # 执行行动
        result = behavior.execute_action(npc, decision)
        for msg in result["messages"]:
            print(f"  -> {msg}")
