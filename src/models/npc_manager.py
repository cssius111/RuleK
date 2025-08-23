"""
NPC管理器
管理所有NPC的创建、状态和行为
"""
from typing import Dict, List, Optional
from .npc import NPC


class NPCManager:
    """NPC管理器"""

    def __init__(self):
        self.npcs: Dict[str, NPC] = {}
        # 使用更多样化的英文名字
        self.npc_names = [
            # 普通人名
            "Alice", "Bob", "Charlie", "Diana", "Eric", "Fiona",
            "George", "Helen", "Ivan", "Julia", "Kevin", "Luna",
            "Marcus", "Nina", "Oliver", "Petra", "Quinn", "Ruby",
            "Sam", "Tina", "Ulrich", "Vera", "Walter", "Xena",
            "Yuki", "Zoe",
            # 职业相关命名
            "Dr. Morgan", "Prof. Chen", "Officer Davis", "Nurse Kelly",
            "Engineer Park", "Janitor Mike", "Security Tom", "Student Amy"
        ]
        self.name_index = 0
        self.used_names = set()

    def create_npc(
        self, name: Optional[str] = None, template: Optional[str] = None, **kwargs
    ) -> NPC:
        """创建NPC"""
        if not name:
            # 智能选择名字
            available_names = [n for n in self.npc_names if n not in self.used_names]
            if available_names:
                import random
                name = random.choice(available_names)
                self.used_names.add(name)
            elif self.name_index < len(self.npc_names):
                # 如果没有可用名字，顺序使用
                name = self.npc_names[self.name_index]
                self.name_index += 1
            else:
                # 全部用完，生成序号名
                name = f"Survivor_{len(self.npcs) + 1}"

        # 设置默认值
        npc_data = {
            "name": name,
            "hp": kwargs.get("hp", 100),
            "sanity": kwargs.get("sanity", 100),
            "fear": kwargs.get("fear", 0),
            "location": kwargs.get("location", "living_room"),
            "traits": kwargs.get("traits", ["普通"]),
            "alive": kwargs.get("alive", True),
            "inventory": kwargs.get("inventory", []),
        }

        # 如果有模板，应用模板设置
        if template:
            if template == "brave":
                npc_data["traits"] = ["勇敢", "冲动"]
                npc_data["fear"] = 30
            elif template == "clever":
                npc_data["traits"] = ["聪明", "谨慎"]
                npc_data["fear"] = 40
            elif template == "timid":
                npc_data["traits"] = ["胆小", "敏感"]
                npc_data["fear"] = 60

        npc = NPC(**npc_data)
        self.npcs[npc.id] = npc
        return npc

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """获取NPC"""
        return self.npcs.get(npc_id)

    def get_npcs_in_location(self, location: str) -> List[NPC]:
        """获取指定位置的所有NPC"""
        return [npc for npc in self.npcs.values() if npc.location == location]

    def get_alive_npcs(self) -> List[NPC]:
        """获取所有存活的NPC"""
        return [npc for npc in self.npcs.values() if npc.is_alive]

    def clear(self):
        """清空所有NPC"""
        self.npcs.clear()
        self.name_index = 0
        self.used_names.clear()

    def remove_npc(self, npc_id: str) -> bool:
        """移除NPC"""
        if npc_id in self.npcs:
            del self.npcs[npc_id]
            return True
        return False

    def update_npc(self, npc_id: str, updates: dict):
        """更新NPC状态"""
        npc = self.get_npc(npc_id)
        if npc:
            for key, value in updates.items():
                if hasattr(npc, key):
                    setattr(npc, key, value)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()}

    def from_dict(self, data: dict):
        """从字典恢复"""
        self.npcs = {}
        for npc_id, npc_data in data.items():
            npc = NPC(
                name=npc_data["name"],
                rationality=npc_data.get("rationality", 5),
                courage=npc_data.get("courage", 5),
                curiosity=npc_data.get("curiosity", 5),
            )
            npc.id = npc_id
            npc.hp = npc_data.get("hp", 100)
            npc.sanity = npc_data.get("sanity", 100)
            npc.fear = npc_data.get("fear", 0)
            npc.location = npc_data.get("location", "living_room")
            npc.status_effects = npc_data.get("status_effects", [])
            npc.inventory = npc_data.get("inventory", [])
            npc.memories = npc_data.get("memories", [])
            self.npcs[npc_id] = npc
