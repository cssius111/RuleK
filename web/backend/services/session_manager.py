"""
游戏会话管理器
管理多个并行的游戏实例
"""
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
import uuid
import logging

from .game_service import GameService

logger = logging.getLogger(__name__)


class SessionManager:
    """游戏会话管理器"""
    
    def __init__(self, max_sessions: int = 100, session_timeout: int = 3600):
        """
        初始化会话管理器
        
        Args:
            max_sessions: 最大并行游戏数
            session_timeout: 会话超时时间（秒）
        """
        self.sessions: Dict[str, GameService] = {}
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self._cleanup_task = None
        self._lock = asyncio.Lock()
    
    async def create_game(self, difficulty: str = "normal", npc_count: int = 4) -> GameService:
        """创建新游戏会话"""
        async with self._lock:
            if len(self.sessions) >= self.max_sessions:
                # 清理过期会话
                await self._cleanup_expired_sessions()
                if len(self.sessions) >= self.max_sessions:
                    raise ValueError("Maximum number of active games reached")
            
            game_id = f"game_{uuid.uuid4().hex[:8]}"
            game_service = GameService(game_id, difficulty, npc_count)
            await game_service.initialize()
            
            self.sessions[game_id] = game_service
            logger.info(f"Created new game session: {game_id}")
            
            # 启动定期清理任务
            if not self._cleanup_task:
                self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            
            return game_service
    
    def get_game(self, game_id: str) -> Optional[GameService]:
        """获取游戏会话"""
        game_service = self.sessions.get(game_id)
        if game_service:
            game_service.update_last_accessed()
        return game_service
    
    def remove_game(self, game_id: str) -> bool:
        """移除游戏会话"""
        if game_id in self.sessions:
            game_service = self.sessions[game_id]
            asyncio.create_task(game_service.cleanup())
            del self.sessions[game_id]
            logger.info(f"Removed game session: {game_id}")
            return True
        return False
    
    def get_active_game_count(self) -> int:
        """获取活跃游戏数量"""
        return len(self.sessions)
    
    def get_all_games(self) -> Dict[str, Dict]:
        """获取所有游戏的简要信息"""
        games_info = {}
        for game_id, game_service in self.sessions.items():
            games_info[game_id] = {
                "game_id": game_id,
                "created_at": game_service.created_at.isoformat(),
                "last_accessed": game_service.last_accessed.isoformat(),
                "current_turn": game_service.game_state.current_turn,
                "npc_count": len(game_service.npcs),
                "active": game_service.is_active()
            }
        return games_info
    
    async def load_game(self, filename: str) -> GameService:
        """从文件加载游戏"""
        async with self._lock:
            if len(self.sessions) >= self.max_sessions:
                await self._cleanup_expired_sessions()
            
            # 创建新的游戏服务并加载存档
            game_service = GameService.load_from_file(filename)
            await game_service.initialize()
            
            game_id = game_service.game_state.game_id
            self.sessions[game_id] = game_service
            logger.info(f"Loaded game from save: {game_id}")
            
            return game_service
    
    async def _cleanup_expired_sessions(self):
        """清理过期的游戏会话"""
        current_time = datetime.now()
        expired_games = []
        
        for game_id, game_service in self.sessions.items():
            if not game_service.is_active():
                time_since_access = (current_time - game_service.last_accessed).total_seconds()
                if time_since_access > self.session_timeout:
                    expired_games.append(game_id)
        
        for game_id in expired_games:
            logger.info(f"Cleaning up expired session: {game_id}")
            self.remove_game(game_id)
    
    async def _periodic_cleanup(self):
        """定期清理任务"""
        while self.sessions:
            await asyncio.sleep(300)  # 每5分钟检查一次
            await self._cleanup_expired_sessions()
    
    async def cleanup(self):
        """清理所有会话"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # 清理所有游戏会话
        game_ids = list(self.sessions.keys())
        for game_id in game_ids:
            self.remove_game(game_id)
        
        logger.info("Session manager cleaned up")
