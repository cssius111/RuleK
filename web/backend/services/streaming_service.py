"""
WebSocket流式推送服务
实现实时消息推送、断线重连、心跳检测等功能
"""
import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime
from collections import deque
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ConnectionInfo(BaseModel):
    """连接信息"""
    client_id: str
    connected_at: datetime
    last_ping: datetime
    websocket: Optional[Any] = None  # WebSocket实例不能序列化

    class Config:
        arbitrary_types_allowed = True


class Message(BaseModel):
    """消息模型"""
    id: str
    type: str  # 'game_update', 'ai_response', 'error', 'ping', 'pong'
    data: Dict[str, Any]
    timestamp: datetime
    sequence: int  # 消息序号，用于保证顺序


class StreamingService:
    """流式推送服务"""
    
    def __init__(self):
        # 活跃连接管理
        self.active_connections: Dict[str, ConnectionInfo] = {}
        # WebSocket实例映射
        self.websockets: Dict[str, WebSocket] = {}
        # 消息队列（每个客户端一个队列）
        self.message_queues: Dict[str, deque] = {}
        # 消息序号计数器
        self.sequence_counters: Dict[str, int] = {}
        # 心跳检测任务
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
        # 配置
        self.heartbeat_interval = 30  # 心跳间隔（秒）
        self.heartbeat_timeout = 60   # 心跳超时（秒）
        self.max_queue_size = 100     # 最大队列长度
        self.reconnect_window = 300   # 重连窗口（秒）
        
    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """
        建立WebSocket连接
        
        Args:
            websocket: WebSocket实例
            client_id: 客户端ID
        """
        await websocket.accept()
        
        # 记录连接信息
        now = datetime.now()
        self.active_connections[client_id] = ConnectionInfo(
            client_id=client_id,
            connected_at=now,
            last_ping=now,
            websocket=websocket
        )
        self.websockets[client_id] = websocket
        
        # 初始化消息队列
        if client_id not in self.message_queues:
            self.message_queues[client_id] = deque(maxlen=self.max_queue_size)
            self.sequence_counters[client_id] = 0
        
        # 启动心跳检测
        if client_id in self.heartbeat_tasks:
            self.heartbeat_tasks[client_id].cancel()
        self.heartbeat_tasks[client_id] = asyncio.create_task(
            self._heartbeat_loop(client_id)
        )
        
        # 发送连接成功消息
        await self.send_message(client_id, {
            "type": "connection",
            "data": {
                "status": "connected",
                "client_id": client_id,
                "reconnect_window": self.reconnect_window
            }
        })
        
        logger.info(f"Client {client_id} connected")
        
    async def disconnect(self, client_id: str) -> None:
        """
        断开WebSocket连接
        
        Args:
            client_id: 客户端ID
        """
        # 取消心跳任务
        if client_id in self.heartbeat_tasks:
            self.heartbeat_tasks[client_id].cancel()
            del self.heartbeat_tasks[client_id]
        
        # 移除连接
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.websockets:
            del self.websockets[client_id]
            
        # 保留消息队列一段时间，以支持重连
        asyncio.create_task(self._cleanup_queue_later(client_id))
        
        logger.info(f"Client {client_id} disconnected")
        
    async def _cleanup_queue_later(self, client_id: str) -> None:
        """
        延迟清理消息队列（支持重连）
        
        Args:
            client_id: 客户端ID
        """
        await asyncio.sleep(self.reconnect_window)
        
        # 如果客户端没有重连，清理队列
        if client_id not in self.active_connections:
            if client_id in self.message_queues:
                del self.message_queues[client_id]
            if client_id in self.sequence_counters:
                del self.sequence_counters[client_id]
            logger.info(f"Cleaned up queue for {client_id}")
            
    async def send_message(self, client_id: str, message_data: Dict[str, Any]) -> bool:
        """
        发送消息给特定客户端
        
        Args:
            client_id: 客户端ID
            message_data: 消息数据
            
        Returns:
            是否发送成功
        """
        if client_id not in self.websockets:
            # 客户端未连接，加入队列
            if client_id in self.message_queues:
                self.message_queues[client_id].append(message_data)
            return False
            
        websocket = self.websockets[client_id]
        
        # 生成消息
        self.sequence_counters[client_id] += 1
        message = Message(
            id=f"{client_id}_{self.sequence_counters[client_id]}",
            type=message_data.get("type", "unknown"),
            data=message_data.get("data", {}),
            timestamp=datetime.now(),
            sequence=self.sequence_counters[client_id]
        )
        
        try:
            await websocket.send_json(message.dict())
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {client_id}: {e}")
            # 发送失败，加入队列
            self.message_queues[client_id].append(message_data)
            return False
            
    async def broadcast(self, message_data: Dict[str, Any]) -> None:
        """
        广播消息给所有连接的客户端
        
        Args:
            message_data: 消息数据
        """
        tasks = []
        for client_id in list(self.active_connections.keys()):
            tasks.append(self.send_message(client_id, message_data))
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def send_stream(self, client_id: str, data_generator) -> None:
        """
        流式发送数据
        
        Args:
            client_id: 客户端ID
            data_generator: 数据生成器（异步生成器）
        """
        chunk_id = 0
        async for chunk in data_generator:
            chunk_id += 1
            await self.send_message(client_id, {
                "type": "stream_chunk",
                "data": {
                    "chunk_id": chunk_id,
                    "content": chunk,
                    "is_final": False
                }
            })
            # 控制发送速率
            await asyncio.sleep(0.05)
            
        # 发送结束标记
        await self.send_message(client_id, {
            "type": "stream_chunk",
            "data": {
                "chunk_id": chunk_id + 1,
                "content": "",
                "is_final": True
            }
        })
        
    async def _heartbeat_loop(self, client_id: str) -> None:
        """
        心跳检测循环
        
        Args:
            client_id: 客户端ID
        """
        while client_id in self.active_connections:
            try:
                # 发送ping
                await self.send_message(client_id, {"type": "ping", "data": {}})
                
                # 等待心跳间隔
                await asyncio.sleep(self.heartbeat_interval)
                
                # 检查是否超时
                if client_id in self.active_connections:
                    last_ping = self.active_connections[client_id].last_ping
                    if (datetime.now() - last_ping).seconds > self.heartbeat_timeout:
                        logger.warning(f"Client {client_id} heartbeat timeout")
                        await self.disconnect(client_id)
                        break
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error for {client_id}: {e}")
                break
                
    async def handle_message(self, client_id: str, message: str) -> None:
        """
        处理客户端消息
        
        Args:
            client_id: 客户端ID
            message: 消息内容
        """
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "pong":
                # 更新心跳时间
                if client_id in self.active_connections:
                    self.active_connections[client_id].last_ping = datetime.now()
                    
            elif msg_type == "reconnect":
                # 处理重连，发送队列中的消息
                await self._handle_reconnect(client_id)
                
            else:
                # 其他消息类型，交给业务处理
                logger.info(f"Received message from {client_id}: {msg_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from {client_id}: {message}")
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            
    async def _handle_reconnect(self, client_id: str) -> None:
        """
        处理客户端重连
        
        Args:
            client_id: 客户端ID
        """
        if client_id in self.message_queues:
            # 发送队列中的消息
            queue = self.message_queues[client_id]
            while queue:
                message_data = queue.popleft()
                await self.send_message(client_id, message_data)
                
            logger.info(f"Sent {len(queue)} queued messages to {client_id}")


# 全局流式服务实例
streaming_service = StreamingService()


# WebSocket路由处理函数
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket端点处理函数
    
    Args:
        websocket: WebSocket实例
        client_id: 客户端ID
    """
    await streaming_service.connect(websocket, client_id)
    
    try:
        while True:
            # 接收客户端消息
            message = await websocket.receive_text()
            await streaming_service.handle_message(client_id, message)
            
    except WebSocketDisconnect:
        await streaming_service.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        await streaming_service.disconnect(client_id)
