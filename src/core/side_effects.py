"""
规则副作用系统
定义和管理规则触发后的各种副作用
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class SideEffect(ABC):
    """副作用基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def apply(self, game_state: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用副作用

        Args:
            game_state: 游戏状态管理器
            context: 副作用上下文，包含位置、触发者等信息

        Returns:
            Dict: 副作用执行结果
        """
        pass

    def can_apply(self, game_state: Any, context: Dict[str, Any]) -> bool:
        """检查是否可以应用此副作用"""
        return True


class BloodMessageEffect(SideEffect):
    """血字消息副作用"""

    def __init__(self):
        super().__init__("blood_message", "在墙上或镜子上出现血字")

    def apply(self, game_state: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """在指定位置添加血字"""
        location = context.get("location", "unknown")
        message = context.get("message", "你逃不掉的...")
        surface = context.get("surface", "wall")  # wall, mirror, floor

        # 添加环境效果
        effect_data = {
            "type": "blood_message",
            "location": location,
            "surface": surface,
            "message": message,
            "discovered": False,
        }

        # 如果有地图管理器，添加到场景
        if hasattr(game_state, "map_manager"):
            area = game_state.map_manager.get_area(location)
            if area:
                if "effects" not in area.__dict__:
                    area.effects = []
                area.effects.append(effect_data)

        logger.info(f"血字出现在{location}的{surface}上: {message}")

        return {
            "success": True,
            "effect_type": "blood_message",
            "fear_bonus": 10,  # 发现血字的人额外恐惧
            "data": effect_data,
        }


class LightFlickerEffect(SideEffect):
    """灯光闪烁副作用"""

    def __init__(self):
        super().__init__("light_flicker", "房间灯光开始闪烁")

    def apply(self, game_state: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """使指定位置的灯光闪烁"""
        location = context.get("location", "unknown")
        duration = context.get("duration", 3)  # 持续回合数
        intensity = context.get("intensity", "normal")  # normal, intense, brief

        # 影响该位置所有NPC
        affected_npcs = []
        fear_increase = 5 if intensity == "normal" else 10

        if hasattr(game_state, "get_npcs_in_location"):
            npcs_in_area = game_state.get_npcs_in_location(location)
            for npc in npcs_in_area:
                npc_id = npc.get("id")
                if npc_id:
                    # 增加恐惧值
                    new_fear = min(100, npc.get("fear", 0) + fear_increase)
                    game_state.update_npc(npc_id, {"fear": new_fear})
                    affected_npcs.append(npc.get("name", "Unknown"))

        logger.info(f"{location}的灯光开始{intensity}闪烁，持续{duration}回合")

        return {
            "success": True,
            "effect_type": "light_flicker",
            "affected_npcs": affected_npcs,
            "fear_caused": fear_increase * len(affected_npcs),
        }


class TemperatureDropEffect(SideEffect):
    """温度骤降副作用"""

    def __init__(self):
        super().__init__("temperature_drop", "房间温度突然下降")

    def apply(self, game_state: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """降低房间温度"""
        location = context.get("location", "unknown")
        drop_amount = context.get("drop_amount", 10)  # 温度下降度数

        # 创建环境效果
        effect_data = {
            "type": "temperature_drop",
            "location": location,
            "drop_amount": drop_amount,
            "turns_remaining": 5,  # 持续5回合
        }

        # 影响NPC行为 - 寒冷会让NPC想要离开或寻找温暖
        behavioral_changes = []
        if hasattr(game_state, "get_npcs_in_location"):
            npcs_in_area = game_state.get_npcs_in_location(location)
            for npc in npcs_in_area:
                # 理智较低的NPC更容易感到恐惧
                if npc.get("sanity", 100) < 70:
                    behavioral_changes.append(
                        {"npc": npc.get("name"), "change": "wants_to_leave"}
                    )

        logger.info(f"{location}的温度下降了{drop_amount}度")

        return {
            "success": True,
            "effect_type": "temperature_drop",
            "behavioral_changes": behavioral_changes,
            "data": effect_data,
        }


class ScreamHeardEffect(SideEffect):
    """听到尖叫声副作用"""

    def __init__(self):
        super().__init__("scream_heard", "附近传来恐怖的尖叫声")

    def apply(self, game_state: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """在附近区域播放尖叫声"""
        source_location = context.get("location", "unknown")
        scream_type = context.get("scream_type", "terror")  # terror, pain, death

        # 获取相邻房间
        affected_locations = [source_location]
        if hasattr(game_state, "map_manager"):
            area = game_state.map_manager.get_area(source_location)
            if area and hasattr(area, "connections"):
                affected_locations.extend(area.connections)

        # 影响所有听到尖叫的NPC
        affected_npcs = []
        total_fear = 0

        for location in affected_locations:
            distance_modifier = 1.0 if location == source_location else 0.5
            fear_increase = (
                int(15 * distance_modifier)
                if scream_type == "death"
                else int(10 * distance_modifier)
            )

            if hasattr(game_state, "get_npcs_in_location"):
                npcs = game_state.get_npcs_in_location(location)
                for npc in npcs:
                    npc_id = npc.get("id")
                    if npc_id:
                        new_fear = min(100, npc.get("fear", 0) + fear_increase)
                        new_suspicion = min(100, npc.get("suspicion", 0) + 5)

                        game_state.update_npc(
                            npc_id, {"fear": new_fear, "suspicion": new_suspicion}
                        )

                        affected_npcs.append(
                            {
                                "name": npc.get("name"),
                                "location": location,
                                "fear_increase": fear_increase,
                            }
                        )
                        total_fear += fear_increase

        logger.info(f"{source_location}传来{scream_type}尖叫，影响了{len(affected_npcs)}个NPC")

        return {
            "success": True,
            "effect_type": "scream_heard",
            "affected_npcs": affected_npcs,
            "total_fear_caused": total_fear,
            "affected_locations": affected_locations,
        }


class ItemAppearEffect(SideEffect):
    """物品出现副作用"""

    def __init__(self):
        super().__init__("item_appear", "诡异的物品突然出现")

    def apply(self, game_state: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """在指定位置生成物品"""
        location = context.get("location", "unknown")
        item_type = context.get("item_type", "cursed_doll")
        item_properties = context.get("properties", {})

        # 创建物品
        item_data = {
            "type": item_type,
            "location": location,
            "properties": item_properties,
            "discovered": False,
        }

        # 添加到地图
        if hasattr(game_state, "map_manager"):
            area = game_state.map_manager.get_area(location)
            if area:
                if "items" not in area.__dict__:
                    area.items = []
                area.items.append(item_data)

        logger.info(f"{item_type}出现在{location}")

        return {"success": True, "effect_type": "item_appear", "item": item_data}


class DoorLockEffect(SideEffect):
    """门锁定副作用"""

    def __init__(self):
        super().__init__("door_lock", "门突然锁上了")

    def apply(self, game_state: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """锁定指定房间的门"""
        location = context.get("location", "unknown")
        duration = context.get("duration", 3)  # 锁定回合数
        exits = context.get("exits", [])  # 特定出口，空则锁定所有

        # 创建锁定效果
        lock_data = {
            "type": "door_lock",
            "location": location,
            "locked_exits": exits if exits else "all",
            "turns_remaining": duration,
        }

        # 检查是否有NPC被困
        trapped_npcs = []
        if hasattr(game_state, "get_npcs_in_location"):
            npcs = game_state.get_npcs_in_location(location)
            for npc in npcs:
                trapped_npcs.append(npc.get("name"))
                # 被困会增加恐慌
                npc_id = npc.get("id")
                if npc_id:
                    new_fear = min(100, npc.get("fear", 0) + 20)
                    game_state.update_npc(npc_id, {"fear": new_fear})

        logger.info(f"{location}的门被锁定{duration}回合，困住了{len(trapped_npcs)}个NPC")

        return {
            "success": True,
            "effect_type": "door_lock",
            "trapped_npcs": trapped_npcs,
            "data": lock_data,
        }


# 副作用注册表
SIDE_EFFECTS_REGISTRY = {
    "blood_message": BloodMessageEffect(),
    "light_flicker": LightFlickerEffect(),
    "temperature_drop": TemperatureDropEffect(),
    "scream_heard": ScreamHeardEffect(),
    "item_appear": ItemAppearEffect(),
    "door_lock": DoorLockEffect(),
}


class SideEffectManager:
    """副作用管理器"""

    def __init__(self):
        self.effects = SIDE_EFFECTS_REGISTRY.copy()
        self.active_effects: List[Dict[str, Any]] = []

    def register_effect(self, name: str, effect: SideEffect):
        """注册新的副作用"""
        self.effects[name] = effect
        logger.info(f"注册副作用: {name}")

    def apply_effect(
        self, effect_name: str, game_state: Any, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """应用指定的副作用"""
        effect = self.effects.get(effect_name)
        if not effect:
            logger.warning(f"未找到副作用: {effect_name}")
            return None

        if not effect.can_apply(game_state, context):
            logger.info(f"副作用 {effect_name} 当前无法应用")
            return None

        result = effect.apply(game_state, context)

        # 记录活跃的副作用
        if result.get("success"):
            self.active_effects.append(
                {
                    "effect_name": effect_name,
                    "turn_applied": game_state.state.turn
                    if hasattr(game_state, "state")
                    else 0,
                    "context": context,
                    "result": result,
                }
            )

        return result

    def apply_multiple_effects(
        self, effect_names: List[str], game_state: Any, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """应用多个副作用"""
        results = []
        for effect_name in effect_names:
            result = self.apply_effect(effect_name, game_state, context)
            if result:
                results.append(result)
        return results

    def update_active_effects(self, current_turn: int) -> None:
        """更新活跃副作用列表并移除过期的副作用。

        Args:
            current_turn: 当前游戏回合数
        """
        remaining_effects = []
        for effect in self.active_effects:
            context = effect.get("context", {})
            duration = context.get("duration", 1)
            turn_applied = effect.get("turn_applied", 0)

            if current_turn - turn_applied >= duration:
                logger.info("副作用 %s 已过期", effect.get("effect_name"))
                continue

            remaining_effects.append(effect)

        self.active_effects = remaining_effects

    def get_effects_in_location(self, location: str) -> List[Dict[str, Any]]:
        """获取指定位置的所有活跃副作用"""
        return [
            effect
            for effect in self.active_effects
            if effect.get("context", {}).get("location") == location
        ]


# 导出
__all__ = [
    "SideEffect",
    "SideEffectManager",
    "SIDE_EFFECTS_REGISTRY",
    "BloodMessageEffect",
    "LightFlickerEffect",
    "TemperatureDropEffect",
    "ScreamHeardEffect",
    "ItemAppearEffect",
    "DoorLockEffect",
]
