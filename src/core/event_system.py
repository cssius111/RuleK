"""
事件系统
管理游戏中的随机事件和触发事件
"""
from typing import Dict, List, Any, Optional
import random
from datetime import datetime


class EventSystem:
    """事件系统"""
    
    def __init__(self):
        self.event_history = []
        self.random_events = [
            {
                "id": "strange_noise",
                "name": "奇怪的声音",
                "description": "从{location}传来了令人不安的声响",
                "effects": {
                    "fear_increase": 10,
                    "trigger_probability": 0.3
                }
            },
            {
                "id": "power_outage",
                "name": "停电",
                "description": "灯光突然熄灭，黑暗笼罩了整个空间",
                "effects": {
                    "fear_increase": 20,
                    "trigger_probability": 0.2
                }
            },
            {
                "id": "door_slam",
                "name": "门突然关闭",
                "description": "一扇门猛地关上，仿佛有人在愤怒",
                "effects": {
                    "fear_increase": 15,
                    "trigger_probability": 0.25
                }
            },
            {
                "id": "temperature_drop",
                "name": "温度骤降",
                "description": "房间突然变得异常寒冷，呼出的气都变成了白雾",
                "effects": {
                    "fear_increase": 12,
                    "trigger_probability": 0.35
                }
            },
            {
                "id": "shadow_movement",
                "name": "影子移动",
                "description": "墙上的影子似乎有了自己的生命",
                "effects": {
                    "fear_increase": 18,
                    "sanity_decrease": 5,
                    "trigger_probability": 0.15
                }
            }
        ]
    
    def trigger_random_event(self, turn: int, fear_level: int) -> Optional[Dict[str, Any]]:
        """触发随机事件"""
        # 根据回合数和恐惧等级计算触发概率
        base_probability = 0.1
        turn_modifier = min(turn * 0.02, 0.3)  # 回合越多，概率越高
        fear_modifier = fear_level / 1000  # 恐惧越高，概率越高
        
        trigger_probability = base_probability + turn_modifier + fear_modifier
        
        if random.random() < trigger_probability:
            # 选择一个随机事件
            event = random.choice(self.random_events)
            
            # 选择随机位置
            locations = ["客厅", "卧室", "厨房", "浴室", "地下室"]
            location = random.choice(locations)
            
            # 生成事件描述
            description = event["description"].format(location=location)
            
            # 记录事件
            event_record = {
                "type": "random_event",
                "id": event["id"],
                "name": event["name"],
                "description": description,
                "location": location,
                "turn": turn,
                "timestamp": datetime.now().isoformat(),
                "effects": event["effects"]
            }
            
            self.event_history.append(event_record)
            
            return event_record
        
        return None
    
    def create_custom_event(self, event_type: str, description: str, **kwargs) -> Dict[str, Any]:
        """创建自定义事件"""
        event = {
            "type": event_type,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        
        self.event_history.append(event)
        return event
    
    def get_recent_events(self, count: int = 5) -> List[Dict[str, Any]]:
        """获取最近的事件"""
        return self.event_history[-count:] if self.event_history else []
    
    def clear_old_events(self, keep_count: int = 100):
        """清理旧事件，只保留最近的事件"""
        if len(self.event_history) > keep_count:
            self.event_history = self.event_history[-keep_count:]
    
    def find_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """根据类型查找事件"""
        return [event for event in self.event_history if event.get("type") == event_type]
    
    def find_events_by_turn(self, turn: int) -> List[Dict[str, Any]]:
        """根据回合查找事件"""
        return [event for event in self.event_history if event.get("turn") == turn]
