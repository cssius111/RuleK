"""
位置模型
定义游戏中的位置和区域
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Location(BaseModel):
    """位置/区域"""
    id: str = Field(..., description="位置ID")
    name: str = Field(..., description="位置名称")
    description: str = Field("", description="位置描述")
    connected_to: List[str] = Field(default_factory=list, description="连接的位置")
    items: List[str] = Field(default_factory=list, description="该位置的物品")
    npcs: List[str] = Field(default_factory=list, description="该位置的NPC")
    properties: List[str] = Field(default_factory=list, description="位置属性")
    is_safe: bool = Field(True, description="是否安全")
    
    def add_npc(self, npc_id: str):
        """添加NPC到该位置"""
        if npc_id not in self.npcs:
            self.npcs.append(npc_id)
    
    def remove_npc(self, npc_id: str):
        """从该位置移除NPC"""
        if npc_id in self.npcs:
            self.npcs.remove(npc_id)
    
    def add_item(self, item: str):
        """添加物品到该位置"""
        if item not in self.items:
            self.items.append(item)
    
    def remove_item(self, item: str) -> bool:
        """从该位置移除物品"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def is_connected_to(self, location_id: str) -> bool:
        """检查是否连接到指定位置"""
        return location_id in self.connected_to
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()


# 预定义位置
DEFAULT_LOCATIONS = {
    "living_room": Location(
        id="living_room",
        name="客厅",
        description="一个宽敞的客厅，但灯光忽明忽暗",
        connected_to=["kitchen", "corridor", "bathroom"],
        is_safe=True
    ),
    "kitchen": Location(
        id="kitchen",
        name="厨房",
        description="散发着奇怪味道的厨房",
        connected_to=["living_room", "dining_room"],
        is_safe=False
    ),
    "corridor": Location(
        id="corridor",
        name="走廊",
        description="昏暗的走廊，墙上挂着诡异的画",
        connected_to=["living_room", "bedroom", "bathroom"],
        properties=["dark"],
        is_safe=False
    ),
    "bedroom": Location(
        id="bedroom",
        name="卧室",
        description="床上似乎有什么东西在动",
        connected_to=["corridor"],
        properties=["dark", "cold"],
        is_safe=False
    ),
    "bathroom": Location(
        id="bathroom",
        name="浴室",
        description="镜子里倒映着不属于你的影子",
        connected_to=["living_room", "corridor"],
        properties=["mirror", "wet"],
        is_safe=False
    ),
    "dining_room": Location(
        id="dining_room",
        name="餐厅",
        description="餐桌上摆着腐烂的食物",
        connected_to=["kitchen"],
        is_safe=False
    ),
    "basement": Location(
        id="basement",
        name="地下室",
        description="黑暗深处传来奇怪的声音",
        connected_to=["kitchen"],
        properties=["dark", "cold", "dangerous"],
        is_safe=False
    )
}


def create_default_locations() -> Dict[str, Location]:
    """创建默认位置"""
    return DEFAULT_LOCATIONS.copy()
