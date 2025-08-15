"""
配置模型
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import json
from pathlib import Path


class AIConfig(BaseModel):
    """AI配置"""
    api_key: str = ""
    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com/v1"
    max_tokens: int = 2000
    temperature: float = 0.7
    enabled: bool = False


class GameConfig(BaseModel):
    """游戏配置"""
    initial_fear_points: int = 1000
    initial_npc_count: int = 4
    difficulty: str = "normal"
    ai_enabled: bool = False
    max_turns: int = 100
    auto_save: bool = True


class ServerConfig(BaseModel):
    """服务器配置"""
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True
    log_level: str = "info"


class Config(BaseModel):
    """主配置类"""
    game: GameConfig = Field(default_factory=GameConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    
    @classmethod
    def load_from_file(cls, config_path: Optional[Path] = None) -> "Config":
        """从文件加载配置"""
        if config_path is None:
            # 默认配置文件路径
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return cls(**data)
            except Exception as e:
                print(f"警告: 加载配置文件失败，使用默认配置: {e}")
                return cls()
        else:
            print(f"警告: 配置文件不存在，使用默认配置: {config_path}")
            return cls()
    
    def save_to_file(self, config_path: Optional[Path] = None):
        """保存配置到文件"""
        if config_path is None:
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.json"
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
    
    def get_ai_enabled(self) -> bool:
        """获取AI是否启用"""
        return self.ai.enabled or self.game.ai_enabled
    
    def get_initial_npcs(self) -> int:
        """获取初始NPC数量"""
        return self.game.initial_npc_count
    
    def get_initial_fear_points(self) -> int:
        """获取初始恐惧点数"""
        return self.game.initial_fear_points
