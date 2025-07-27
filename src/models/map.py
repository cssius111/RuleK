"""
地图系统数据模型
定义游戏中的区域、连接关系和地图管理
"""
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class AreaType(str, Enum):
    """区域类型枚举"""
    ROOM = "room"              # 房间
    CORRIDOR = "corridor"      # 走廊
    BATHROOM = "bathroom"      # 浴室
    KITCHEN = "kitchen"        # 厨房
    BASEMENT = "basement"      # 地下室
    OUTDOOR = "outdoor"        # 户外


class AreaProperty(str, Enum):
    """区域特殊属性"""
    DARK = "dark"              # 黑暗的
    COLD = "cold"              # 寒冷的
    LOCKED = "locked"          # 锁住的
    HAUNTED = "haunted"        # 闹鬼的
    SAFE = "safe"              # 安全的
    DANGEROUS = "dangerous"    # 危险的


class InteractableObject(BaseModel):
    """可交互物品"""
    id: str
    name: str
    description: str = ""
    can_take: bool = False
    can_use: bool = True
    required_item: Optional[str] = None  # 需要特定物品才能交互
    one_time_use: bool = False
    used: bool = False
    
    def interact(self, actor_items: List[str] = None) -> Dict[str, Any]:
        """与物品交互"""
        if self.used and self.one_time_use:
            return {"success": False, "message": f"{self.name}已经被使用过了"}
            
        if self.required_item and (not actor_items or self.required_item not in actor_items):
            return {"success": False, "message": f"需要{self.required_item}才能使用{self.name}"}
            
        if self.one_time_use:
            self.used = True
            
        return {"success": True, "message": f"成功与{self.name}交互"}


class Area(BaseModel):
    """区域模型"""
    id: str = Field(..., description="区域唯一ID")
    name: str = Field(..., description="区域名称")
    description: str = Field("", description="区域描述")
    area_type: AreaType = Field(AreaType.ROOM, description="区域类型")
    
    # 容量和限制
    max_npcs: int = Field(5, ge=1, description="最大容纳NPC数")
    min_light_level: int = Field(50, ge=0, le=100, description="最低光照等级")
    
    # 连接关系
    connections: Dict[str, str] = Field(default_factory=dict, description="连接的区域 {方向: 区域ID}")
    
    # 特殊属性
    properties: List[AreaProperty] = Field(default_factory=list, description="区域属性")
    
    # 允许的内容
    allowed_spirits: List[str] = Field(default_factory=list, description="允许的灵体类型")
    allowed_rules: List[str] = Field(default_factory=list, description="允许的规则类型")
    
    # 物品
    objects: List[InteractableObject] = Field(default_factory=list, description="区域内的物品")
    items: List[str] = Field(default_factory=list, description="地上的物品")
    
    # 事件
    event_pool: List[str] = Field(default_factory=list, description="可能发生的事件")
    event_weights: Dict[str, float] = Field(default_factory=dict, description="事件权重")
    
    # 状态
    current_npcs: List[str] = Field(default_factory=list, description="当前在此区域的NPC ID")
    current_spirits: List[str] = Field(default_factory=list, description="当前在此区域的灵体")
    
    @field_validator('connections')
    @classmethod
    def validate_connections(cls, v):
        """验证连接方向"""
        valid_directions = {'north', 'south', 'east', 'west', 'up', 'down'}
        for direction in v.keys():
            if direction not in valid_directions:
                raise ValueError(f"Invalid direction: {direction}")
        return v
    
    def is_full(self) -> bool:
        """检查区域是否已满"""
        return len(self.current_npcs) >= self.max_npcs
    
    def is_accessible(self, from_area_id: str = None) -> bool:
        """检查区域是否可访问"""
        if AreaProperty.LOCKED in self.properties:
            return False
        return True
    
    def add_npc(self, npc_id: str) -> bool:
        """添加NPC到区域"""
        if self.is_full():
            return False
        if npc_id not in self.current_npcs:
            self.current_npcs.append(npc_id)
        return True
    
    def remove_npc(self, npc_id: str) -> bool:
        """从区域移除NPC"""
        if npc_id in self.current_npcs:
            self.current_npcs.remove(npc_id)
            return True
        return False
    
    def get_exit_directions(self) -> List[str]:
        """获取可用的出口方向"""
        return list(self.connections.keys())
    
    def get_random_event(self) -> Optional[str]:
        """根据权重随机获取事件"""
        if not self.event_pool:
            return None
            
        import random
        
        # 如果有权重，使用权重随机
        if self.event_weights:
            events = []
            weights = []
            for event in self.event_pool:
                events.append(event)
                weights.append(self.event_weights.get(event, 1.0))
            return random.choices(events, weights=weights)[0]
        else:
            return random.choice(self.event_pool)
    
    def find_object(self, object_id: str) -> Optional[InteractableObject]:
        """查找区域内的物品"""
        for obj in self.objects:
            if obj.id == object_id:
                return obj
        return None


@dataclass
class PathNode:
    """路径节点（用于寻路）"""
    area_id: str
    parent: Optional['PathNode'] = None
    g_cost: float = 0  # 从起点到当前节点的成本
    h_cost: float = 0  # 启发式成本（到目标的估计）
    
    @property
    def f_cost(self) -> float:
        """总成本"""
        return self.g_cost + self.h_cost


class MapManager:
    """地图管理器"""
    
    def __init__(self):
        self.areas: Dict[str, Area] = {}
        self.starting_area: Optional[str] = None
        
    def add_area(self, area: Area):
        """添加区域"""
        self.areas[area.id] = area
        if not self.starting_area:
            self.starting_area = area.id
            
    def get_area(self, area_id: str) -> Optional[Area]:
        """获取区域"""
        return self.areas.get(area_id)
    
    def connect_areas(self, area1_id: str, direction: str, area2_id: str, bidirectional: bool = True):
        """连接两个区域"""
        area1 = self.get_area(area1_id)
        area2 = self.get_area(area2_id)
        
        if not area1 or not area2:
            raise ValueError("Invalid area IDs")
            
        # 建立连接
        area1.connections[direction] = area2_id
        
        # 双向连接
        if bidirectional:
            opposite = self._get_opposite_direction(direction)
            area2.connections[opposite] = area1_id
            
    def _get_opposite_direction(self, direction: str) -> str:
        """获取相反方向"""
        opposites = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east',
            'up': 'down',
            'down': 'up'
        }
        return opposites.get(direction, direction)
    
    def move_npc(self, npc_id: str, from_area_id: str, to_area_id: str) -> bool:
        """移动NPC"""
        from_area = self.get_area(from_area_id)
        to_area = self.get_area(to_area_id)
        
        if not from_area or not to_area:
            return False
            
        # 检查是否可以移动
        if to_area_id not in from_area.connections.values():
            logger.warning(f"No direct connection from {from_area_id} to {to_area_id}")
            return False
            
        if not to_area.is_accessible(from_area_id):
            logger.warning(f"Area {to_area_id} is not accessible")
            return False
            
        if to_area.is_full():
            logger.warning(f"Area {to_area_id} is full")
            return False
            
        # 执行移动
        if from_area.remove_npc(npc_id) and to_area.add_npc(npc_id):
            logger.info(f"NPC {npc_id} moved from {from_area_id} to {to_area_id}")
            return True
            
        return False
    
    def find_path(self, start_area_id: str, end_area_id: str) -> Optional[List[str]]:
        """使用A*算法寻找路径"""
        if start_area_id == end_area_id:
            return [start_area_id]
            
        if start_area_id not in self.areas or end_area_id not in self.areas:
            return None
            
        # 开放列表和关闭列表
        open_list: List[PathNode] = []
        closed_set: Set[str] = set()
        
        # 创建起始节点
        start_node = PathNode(start_area_id)
        open_list.append(start_node)
        
        while open_list:
            # 选择f_cost最小的节点
            current_node = min(open_list, key=lambda n: n.f_cost)
            open_list.remove(current_node)
            closed_set.add(current_node.area_id)
            
            # 到达目标
            if current_node.area_id == end_area_id:
                path = []
                while current_node:
                    path.append(current_node.area_id)
                    current_node = current_node.parent
                return list(reversed(path))
            
            # 探索邻居
            current_area = self.areas[current_node.area_id]
            for direction, neighbor_id in current_area.connections.items():
                if neighbor_id in closed_set:
                    continue
                    
                neighbor_area = self.areas.get(neighbor_id)
                if not neighbor_area or not neighbor_area.is_accessible(current_node.area_id):
                    continue
                    
                # 计算成本
                g_cost = current_node.g_cost + 1  # 简单起见，每步成本为1
                
                # 检查是否已在开放列表中
                existing_node = next((n for n in open_list if n.area_id == neighbor_id), None)
                
                if existing_node and g_cost >= existing_node.g_cost:
                    continue
                    
                # 创建或更新节点
                if not existing_node:
                    neighbor_node = PathNode(neighbor_id, current_node, g_cost, 0)
                    open_list.append(neighbor_node)
                else:
                    existing_node.parent = current_node
                    existing_node.g_cost = g_cost
                    
        return None  # 没有找到路径
    
    def get_nearby_areas(self, area_id: str, max_distance: int = 1) -> List[str]:
        """获取附近的区域"""
        if area_id not in self.areas:
            return []
            
        nearby = set()
        to_explore = [(area_id, 0)]
        explored = set()
        
        while to_explore:
            current_id, distance = to_explore.pop(0)
            
            if current_id in explored or distance > max_distance:
                continue
                
            explored.add(current_id)
            
            if distance > 0:
                nearby.add(current_id)
                
            current_area = self.areas.get(current_id)
            if current_area:
                for neighbor_id in current_area.connections.values():
                    if neighbor_id not in explored:
                        to_explore.append((neighbor_id, distance + 1))
                        
        return list(nearby)
    
    def load_from_json(self, file_path: str):
        """从JSON文件加载地图"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Map file not found: {file_path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 加载区域
        for area_data in data.get('areas', []):
            # 处理物品
            objects = []
            for obj_data in area_data.get('objects', []):
                objects.append(InteractableObject(**obj_data))
            area_data['objects'] = objects
            
            area = Area(**area_data)
            self.add_area(area)
            
        # 设置起始区域
        if 'starting_area' in data:
            self.starting_area = data['starting_area']
            
    def save_to_json(self, file_path: str):
        """保存地图到JSON文件"""
        data = {
            'areas': [],
            'starting_area': self.starting_area
        }
        
        for area in self.areas.values():
            area_dict = area.dict()
            # 转换物品为可序列化格式
            area_dict['objects'] = [obj.dict() for obj in area.objects]
            data['areas'].append(area_dict)
            
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def create_default_map() -> MapManager:
    """创建默认地图"""
    map_manager = MapManager()
    
    # 创建区域
    areas = [
        Area(
            id="living_room",
            name="客厅",
            description="一个破旧的客厅，墙纸已经剥落，空气中弥漫着霉味",
            area_type=AreaType.ROOM,
            max_npcs=8,
            properties=[AreaProperty.SAFE],
            objects=[
                InteractableObject(
                    id="old_tv",
                    name="老电视",
                    description="一台布满灰尘的老式电视机",
                    can_use=True
                ),
                InteractableObject(
                    id="sofa",
                    name="破沙发",
                    description="一个破旧的沙发，上面有些可疑的污渍"
                )
            ],
            event_pool=["strange_noise", "cold_wind"],
            event_weights={"strange_noise": 0.7, "cold_wind": 0.3}
        ),
        
        Area(
            id="corridor",
            name="走廊",
            description="昏暗的走廊，只有几盏忽明忽暗的灯",
            area_type=AreaType.CORRIDOR,
            max_npcs=4,
            min_light_level=20,
            properties=[AreaProperty.DARK],
            event_pool=["footsteps", "shadow_movement", "door_slam"],
            event_weights={"footsteps": 0.5, "shadow_movement": 0.3, "door_slam": 0.2}
        ),
        
        Area(
            id="bedroom_a",
            name="卧室A",
            description="一间普通的卧室，床上的被子似乎刚刚被动过",
            area_type=AreaType.ROOM,
            max_npcs=3,
            objects=[
                InteractableObject(
                    id="closet",
                    name="衣柜",
                    description="一个老式衣柜，门缝里透出奇怪的气息",
                    can_use=True
                ),
                InteractableObject(
                    id="diary",
                    name="日记本",
                    description="一本泛黄的日记本",
                    can_take=True
                )
            ],
            allowed_spirits=["wandering_soul"],
            event_pool=["whisper", "temperature_drop"]
        ),
        
        Area(
            id="bedroom_b",
            name="卧室B",
            description="另一间卧室，窗户被木板钉死了",
            area_type=AreaType.ROOM,
            max_npcs=3,
            properties=[AreaProperty.DARK],
            allowed_spirits=["wandering_soul", "resentful_spirit"]
        ),
        
        Area(
            id="bathroom",
            name="浴室",
            description="狭小的浴室，镜子上布满了裂纹",
            area_type=AreaType.BATHROOM,
            max_npcs=2,
            properties=[AreaProperty.DANGEROUS],
            objects=[
                InteractableObject(
                    id="mirror",
                    name="破碎的镜子",
                    description="一面布满裂纹的镜子，似乎映照着不属于这个世界的东西",
                    can_use=True
                ),
                InteractableObject(
                    id="bathtub",
                    name="浴缸",
                    description="生锈的浴缸，里面有些黑色的污渍"
                )
            ],
            allowed_rules=["mirror_death", "bathroom_rules"],
            event_pool=["water_drip", "mirror_crack", "blood_appear"],
            event_weights={"water_drip": 0.5, "mirror_crack": 0.3, "blood_appear": 0.2}
        ),
        
        Area(
            id="kitchen",
            name="厨房",
            description="废弃的厨房，柜子里传来奇怪的声音",
            area_type=AreaType.KITCHEN,
            max_npcs=4,
            objects=[
                InteractableObject(
                    id="knife",
                    name="菜刀",
                    description="一把锋利的菜刀",
                    can_take=True
                ),
                InteractableObject(
                    id="fridge",
                    name="冰箱",
                    description="一个老旧的冰箱，门缝里渗出腐臭的气味",
                    can_use=True
                )
            ],
            items=["flashlight"],
            event_pool=["cabinet_open", "smell_rot"]
        )
    ]
    
    # 添加区域
    for area in areas:
        map_manager.add_area(area)
    
    # 建立连接关系
    # 客厅连接走廊
    map_manager.connect_areas("living_room", "north", "corridor")
    
    # 走廊连接各个房间
    map_manager.connect_areas("corridor", "west", "bedroom_a")
    map_manager.connect_areas("corridor", "east", "bedroom_b")
    map_manager.connect_areas("corridor", "north", "bathroom")
    
    # 客厅连接厨房
    map_manager.connect_areas("living_room", "east", "kitchen")
    
    return map_manager


# 测试代码
if __name__ == "__main__":
    # 创建默认地图
    map_manager = create_default_map()
    
    print("=== 地图测试 ===")
    
    # 显示所有区域
    print("\n所有区域:")
    for area_id, area in map_manager.areas.items():
        print(f"- {area.name} ({area_id})")
        print(f"  连接: {area.connections}")
        print(f"  属性: {[p.value for p in area.properties]}")
        
    # 测试寻路
    print("\n寻路测试:")
    path = map_manager.find_path("bedroom_a", "kitchen")
    if path:
        print(f"从卧室A到厨房的路径: {' -> '.join(path)}")
    
    # 测试NPC移动
    print("\n移动测试:")
    map_manager.areas["living_room"].add_npc("npc_001")
    print(f"NPC在客厅: {map_manager.areas['living_room'].current_npcs}")
    
    if map_manager.move_npc("npc_001", "living_room", "corridor"):
        print("NPC成功移动到走廊")
        print(f"走廊中的NPC: {map_manager.areas['corridor'].current_npcs}")
    
    # 测试事件
    print("\n事件测试:")
    bathroom = map_manager.get_area("bathroom")
    for i in range(5):
        event = bathroom.get_random_event()
        print(f"浴室随机事件: {event}")
    
    # 保存地图
    map_manager.save_to_json("data/maps/default_map.json")
    print("\n地图已保存到 data/maps/default_map.json")
