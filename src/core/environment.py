from collections import defaultdict
from typing import Dict, List


class EnvironmentService:
    """管理游戏世界环境状态"""

    def __init__(self) -> None:
        self.scene_effects: Dict[str, List[str]] = defaultdict(list)
        self.room_temperature: Dict[str, int] = defaultdict(lambda: 20)
        self.light_events: Dict[str, bool] = defaultdict(bool)

    def add_scene_effect(self, location: str, effect: str) -> bool:
        self.scene_effects[location].append(effect)
        return True

    def change_room_temp(self, location: str, change: int) -> bool:
        self.room_temperature[location] = self.room_temperature[location] + change
        return True

    def trigger_light_event(self, location: str) -> bool:
        self.light_events[location] = True
        return True
