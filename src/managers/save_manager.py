"""
游戏存档管理系统
负责游戏状态的保存和加载
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil

from ..core.game_state import GameState, GameStateManager
from ..models.rule import Rule
from ..models.npc import NPC
from ..models.map import MapManager
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SaveManager:
    """存档管理器"""
    
    def __init__(self, save_dir: str = "data/saves"):
        """
        初始化存档管理器
        
        Args:
            save_dir: 存档目录路径
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # 存档版本，用于兼容性检查
        self.SAVE_VERSION = "1.0"
        
        # 存档文件扩展名
        self.SAVE_EXTENSION = ".rulek"
        
        logger.info(f"存档管理器初始化，存档目录: {self.save_dir.absolute()}")
    
    def save_game(self, game_state_manager: GameStateManager, 
                  save_name: Optional[str] = None,
                  description: Optional[str] = None) -> str:
        """
        保存游戏
        
        Args:
            game_state_manager: 游戏状态管理器
            save_name: 存档名称，如果不提供则自动生成
            description: 存档描述
            
        Returns:
            str: 存档文件名
        """
        # 生成存档文件名
        if not save_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = f"save_{game_state_manager.state.game_id}_{timestamp}"
        
        filename = f"{save_name}{self.SAVE_EXTENSION}"
        filepath = self.save_dir / filename
        
        # 准备存档数据
        save_data = {
            "version": self.SAVE_VERSION,
            "saved_at": datetime.now().isoformat(),
            "description": description or f"Turn {game_state_manager.state.turn}",
            "game_state": self._serialize_game_state(game_state_manager.state),
            "managers": {
                "rules": self._serialize_rules(game_state_manager.rules),
                "npcs": self._serialize_npcs(game_state_manager.state.npcs),
                "map": self._serialize_map(game_state_manager.map_manager if hasattr(game_state_manager, 'map_manager') else None),
            },
            "statistics": game_state_manager.get_statistics() if hasattr(game_state_manager, 'get_statistics') else {}
        }
        
        try:
            # 先保存到临时文件
            temp_filepath = filepath.with_suffix('.tmp')
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            # 验证保存的数据
            with open(temp_filepath, 'r', encoding='utf-8') as f:
                json.load(f)  # 确保可以正确读取
            
            # 移动到最终位置
            shutil.move(str(temp_filepath), str(filepath))
            
            logger.info(f"游戏已保存: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"保存游戏失败: {e}")
            # 清理临时文件
            if temp_filepath.exists():
                temp_filepath.unlink()
            raise
    
    def load_game(self, filename: str) -> Dict[str, Any]:
        """
        加载游戏存档
        
        Args:
            filename: 存档文件名
            
        Returns:
            Dict: 游戏数据
        """
        # 添加扩展名（如果没有）
        if not filename.endswith(self.SAVE_EXTENSION):
            filename = f"{filename}{self.SAVE_EXTENSION}"
        
        filepath = self.save_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"存档文件不存在: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # 检查版本兼容性
            save_version = save_data.get("version", "0.0")
            if not self._is_compatible_version(save_version):
                logger.warning(f"存档版本 {save_version} 可能不兼容当前版本 {self.SAVE_VERSION}")
            
            logger.info(f"成功加载存档: {filename}")
            return save_data
            
        except json.JSONDecodeError as e:
            logger.error(f"存档文件损坏: {filename} - {e}")
            raise
        except Exception as e:
            logger.error(f"加载存档失败: {filename} - {e}")
            raise
    
    def restore_game_state(self, save_data: Dict[str, Any]) -> GameStateManager:
        """
        从存档数据恢复游戏状态
        
        Args:
            save_data: 存档数据
            
        Returns:
            GameStateManager: 恢复的游戏状态管理器
        """
        # 创建新的游戏状态管理器
        game_manager = GameStateManager()
        
        # 恢复游戏状态
        game_state_data = save_data.get("game_state", {})
        game_manager.state = self._deserialize_game_state(game_state_data)
        
        # 恢复规则
        rules_data = save_data.get("managers", {}).get("rules", {})
        game_manager.rules = self._deserialize_rules(rules_data)
        
        # 恢复NPC
        npcs_data = save_data.get("managers", {}).get("npcs", {})
        game_manager.state.npcs = self._deserialize_npcs(npcs_data)
        
        # 恢复地图（如果有）
        map_data = save_data.get("managers", {}).get("map")
        if map_data and hasattr(game_manager, 'map_manager'):
            game_manager.map_manager = self._deserialize_map(map_data)
        
        logger.info(f"游戏状态已恢复，当前回合: {game_manager.state.turn}")
        return game_manager
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """
        列出所有存档
        
        Returns:
            List[Dict]: 存档信息列表
        """
        saves = []
        
        for filepath in self.save_dir.glob(f"*{self.SAVE_EXTENSION}"):
            try:
                # 获取文件信息
                stat = filepath.stat()
                
                # 尝试读取存档信息
                with open(filepath, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                saves.append({
                    "filename": filepath.name,
                    "saved_at": save_data.get("saved_at", "Unknown"),
                    "description": save_data.get("description", ""),
                    "game_id": save_data.get("game_state", {}).get("game_id", "Unknown"),
                    "turn": save_data.get("game_state", {}).get("turn", 0),
                    "file_size": stat.st_size,
                    "version": save_data.get("version", "Unknown")
                })
                
            except Exception as e:
                logger.warning(f"无法读取存档信息: {filepath.name} - {e}")
                saves.append({
                    "filename": filepath.name,
                    "error": str(e)
                })
        
        # 按保存时间排序（最新的在前）
        saves.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
        
        return saves
    
    def delete_save(self, filename: str) -> bool:
        """
        删除存档
        
        Args:
            filename: 存档文件名
            
        Returns:
            bool: 是否成功删除
        """
        if not filename.endswith(self.SAVE_EXTENSION):
            filename = f"{filename}{self.SAVE_EXTENSION}"
        
        filepath = self.save_dir / filename
        
        if filepath.exists():
            try:
                filepath.unlink()
                logger.info(f"已删除存档: {filename}")
                return True
            except Exception as e:
                logger.error(f"删除存档失败: {filename} - {e}")
                return False
        else:
            logger.warning(f"存档不存在: {filename}")
            return False
    
    def create_autosave(self, game_state_manager: GameStateManager) -> Optional[str]:
        """
        创建自动存档
        
        Args:
            game_state_manager: 游戏状态管理器
            
        Returns:
            Optional[str]: 存档文件名，失败返回None
        """
        try:
            # 自动存档使用特殊前缀
            save_name = f"autosave_{game_state_manager.state.game_id}"
            description = f"自动存档 - 回合 {game_state_manager.state.turn}"
            
            # 删除旧的自动存档
            old_autosave = self.save_dir / f"{save_name}{self.SAVE_EXTENSION}"
            if old_autosave.exists():
                old_autosave.unlink()
            
            # 创建新的自动存档
            filename = self.save_game(game_state_manager, save_name, description)
            logger.info(f"自动存档已创建: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"创建自动存档失败: {e}")
            return None
    
    # ========== 序列化方法 ==========
    
    def _serialize_game_state(self, state: GameState) -> Dict[str, Any]:
        """序列化游戏状态"""
        return {
            "game_id": state.game_id,
            "turn": state.turn,
            "phase": state.phase,
            "fear_points": state.fear_points,
            "current_time": state.current_time,
            "active_rules": list(state.active_rules),
            "events_history": state.events_history[-100:],  # 只保存最近100条事件
            "statistics": {
                "total_fear_gained": state.total_fear_gained,
                "npcs_died": state.npcs_died,
                "rules_triggered": state.rules_triggered,
                "rules_discovered": state.rules_discovered
            }
        }
    
    def _serialize_rules(self, rules: Dict[str, Rule]) -> Dict[str, Dict]:
        """序列化规则"""
        serialized = {}
        for rule_id, rule in rules.items():
            serialized[rule_id] = rule.to_dict() if hasattr(rule, 'to_dict') else {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "trigger": rule.trigger.__dict__ if hasattr(rule.trigger, '__dict__') else {},
                "effect": rule.effect.__dict__ if hasattr(rule.effect, '__dict__') else {},
                "requirements": rule.requirements,
                "cost": rule.cost,
                "level": rule.level,
                "times_triggered": rule.times_triggered,
                "loopholes": [lh.__dict__ for lh in rule.loopholes] if hasattr(rule, 'loopholes') else [],
                "active": rule.active
            }
        return serialized
    
    def _serialize_npcs(self, npcs: Dict[str, NPC]) -> Dict[str, Dict]:
        """序列化NPC"""
        serialized = {}
        for npc_id, npc in npcs.items():
            # 处理NPC可能是字典或对象的情况
            if isinstance(npc, dict):
                serialized[npc_id] = npc
            else:
                serialized[npc_id] = npc.to_dict() if hasattr(npc, 'to_dict') else {
                    "id": npc.id,
                    "name": npc.name,
                    "hp": npc.hp,
                    "sanity": npc.sanity,
                    "fear": npc.fear,
                    "suspicion": npc.suspicion,
                    "location": npc.location,
                    "inventory": npc.inventory,
                    "memory": npc.memory,
                    "relationships": npc.relationships,
                    "personality": npc.personality.__dict__ if hasattr(npc.personality, '__dict__') else {},
                    "alive": npc.alive,
                    "death_cause": getattr(npc, 'death_cause', None),
                    "death_turn": getattr(npc, 'death_turn', None)
                }
        return serialized
    
    def _serialize_map(self, map_manager: Optional[MapManager]) -> Optional[Dict]:
        """序列化地图"""
        if not map_manager:
            return None
        
        return map_manager.to_dict() if hasattr(map_manager, 'to_dict') else {
            "areas": {
                area_id: area.__dict__ for area_id, area in map_manager.areas.items()
            } if hasattr(map_manager, 'areas') else {}
        }
    
    # ========== 反序列化方法 ==========
    
    def _deserialize_game_state(self, data: Dict[str, Any]) -> GameState:
        """反序列化游戏状态"""
        state = GameState()
        
        # 恢复基本属性
        for key in ["game_id", "turn", "phase", "fear_points", "current_time"]:
            if key in data:
                setattr(state, key, data[key])
        
        # 恢复集合类型
        state.active_rules = set(data.get("active_rules", []))
        state.events_history = data.get("events_history", [])
        
        # 恢复统计信息
        stats = data.get("statistics", {})
        for key, value in stats.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        return state
    
    def _deserialize_rules(self, data: Dict[str, Dict]) -> Dict[str, Rule]:
        """反序列化规则"""
        rules = {}
        for rule_id, rule_data in data.items():
            try:
                # 这里需要根据实际的Rule类构造方法来创建对象
                # 简化处理，假设Rule类可以从字典创建
                rule = Rule(**rule_data) if 'trigger' in rule_data else Rule.from_dict(rule_data)
                rules[rule_id] = rule
            except Exception as e:
                logger.error(f"反序列化规则失败: {rule_id} - {e}")
        return rules
    
    def _deserialize_npcs(self, data: Dict[str, Dict]) -> Dict[str, NPC]:
        """反序列化NPC"""
        # 由于GameState中的npcs可能直接存储字典，这里返回原始数据
        return data
    
    def _deserialize_map(self, data: Optional[Dict]) -> Optional[MapManager]:
        """反序列化地图"""
        if not data:
            return None
        
        # 创建MapManager实例并恢复数据
        map_manager = MapManager()
        if hasattr(map_manager, 'from_dict'):
            map_manager.from_dict(data)
        
        return map_manager
    
    def _is_compatible_version(self, version: str) -> bool:
        """检查版本兼容性"""
        # 简单的版本检查，实际应用中可能需要更复杂的逻辑
        major_current = int(self.SAVE_VERSION.split('.')[0])
        major_save = int(version.split('.')[0])
        return major_current == major_save


# 全局存档管理器实例
_save_manager = None


def get_save_manager() -> SaveManager:
    """获取全局存档管理器实例"""
    global _save_manager
    if _save_manager is None:
        _save_manager = SaveManager()
    return _save_manager


if __name__ == "__main__":
    # 测试代码
    from ..core.game_state import GameStateManager
    
    # 创建测试游戏
    game_manager = GameStateManager()
    game_manager.new_game()
    
    # 创建存档管理器
    save_manager = SaveManager("test_saves")
    
    # 测试保存
    print("测试保存游戏...")
    filename = save_manager.save_game(game_manager, "test_save", "测试存档")
    print(f"保存成功: {filename}")
    
    # 测试列出存档
    print("\n所有存档:")
    saves = save_manager.list_saves()
    for save in saves:
        print(f"- {save['filename']} (回合 {save.get('turn', 'Unknown')})")
    
    # 测试加载
    print("\n测试加载游戏...")
    save_data = save_manager.load_game(filename)
    restored_manager = save_manager.restore_game_state(save_data)
    print(f"加载成功，当前回合: {restored_manager.state.turn}")
    
    # 测试自动存档
    print("\n测试自动存档...")
    autosave = save_manager.create_autosave(game_manager)
    print(f"自动存档: {autosave}")
