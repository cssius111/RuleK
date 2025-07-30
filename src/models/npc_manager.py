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
        self.npc_names = [
            "张明", "李静", "王芳", "刘强", "陈雪", "杨帆",
            "赵磊", "周婷", "吴敏", "徐阳", "孙莉", "马超"
        ]
        self.name_index = 0
    
    def create_npc(self, name: Optional[str] = None, **kwargs) -> NPC:
        """创建NPC"""
        if not name:
            # 使用默认名字
            if self.name_index < len(self.npc_names):
                name = self.npc_names[self.name_index]
                self.name_index += 1
            else:
                name = f"NPC_{len(self.npcs) + 1}"

        assert name is not None
        npc = NPC(name=name, **kwargs)
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
        return {
            npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()
        }
    
    def from_dict(self, data: dict):
        """从字典恢复"""
        self.npcs = {}
        for npc_id, npc_data in data.items():
            npc = NPC(
                name=npc_data["name"],
                rationality=npc_data.get("rationality", 5),
                courage=npc_data.get("courage", 5),
                curiosity=npc_data.get("curiosity", 5)
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
