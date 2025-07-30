"""
地图管理器
管理游戏场景的地图和区域
"""
from typing import Dict, List, Optional


class Area:
    """区域类"""
    def __init__(self, id: str, name: str, description: str = "", connected_to: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.connected_to = connected_to or []
        self.items = []
        self.npcs = []
        self.rules = []
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connected_to": self.connected_to,
            "items": self.items,
            "npcs": self.npcs,
            "rules": self.rules
        }


class MapManager:
    """地图管理器"""
    
    def __init__(self):
        self.areas: Dict[str, Area] = {}
        self.current_area: Optional[str] = None
    
    def create_default_map(self):
        """创建默认地图"""
        # 创建默认区域
        areas_data = [
            {
                "id": "living_room",
                "name": "客厅",
                "description": "一个昏暗的客厅，墙上挂着一面古老的镜子",
                "connected_to": ["bedroom", "kitchen", "bathroom"]
            },
            {
                "id": "bedroom",
                "name": "卧室",
                "description": "狭小的卧室，床头柜上放着一本日记",
                "connected_to": ["living_room", "bathroom"]
            },
            {
                "id": "kitchen",
                "name": "厨房",
                "description": "破旧的厨房，水龙头滴答作响",
                "connected_to": ["living_room", "basement"]
            },
            {
                "id": "bathroom",
                "name": "浴室",
                "description": "镜子上布满了裂纹，空气中弥漫着潮湿的气息",
                "connected_to": ["living_room", "bedroom"]
            },
            {
                "id": "basement",
                "name": "地下室",
                "description": "黑暗的地下室，传来奇怪的声音",
                "connected_to": ["kitchen"]
            }
        ]
        
        for area_data in areas_data:
            area = Area(**area_data)
            self.add_area(area)
        
        # 设置初始区域
        self.current_area = "living_room"
    
    def add_area(self, area: Area):
        """添加区域"""
        self.areas[area.id] = area
    
    def get_area(self, area_id: str) -> Optional[Area]:
        """获取区域"""
        return self.areas.get(area_id)
    
    def get_connected_areas(self, area_id: str) -> List[Area]:
        """获取相邻区域"""
        area = self.get_area(area_id)
        if not area:
            return []
        
        connected = []
        for connected_id in area.connected_to:
            connected_area = self.get_area(connected_id)
            if connected_area:
                connected.append(connected_area)
        
        return connected
    
    def move_to(self, area_id: str) -> bool:
        """移动到指定区域"""
        if area_id in self.areas:
            self.current_area = area_id
            return True
        return False
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "areas": {area_id: area.to_dict() for area_id, area in self.areas.items()},
            "current_area": self.current_area
        }
    
    def from_dict(self, data: dict):
        """从字典恢复"""
        self.areas = {}
        for area_id, area_data in data.get("areas", {}).items():
            area = Area(
                id=area_data["id"],
                name=area_data["name"],
                description=area_data.get("description", ""),
                connected_to=area_data.get("connected_to", [])
            )
            area.items = area_data.get("items", [])
            area.npcs = area_data.get("npcs", [])
            area.rules = area_data.get("rules", [])
            self.areas[area_id] = area
        
        self.current_area = data.get("current_area")


def create_default_map() -> MapManager:
    """创建并返回默认地图"""
    map_manager = MapManager()
    map_manager.create_default_map()
    return map_manager
