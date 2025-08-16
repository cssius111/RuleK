#!/usr/bin/env python3
"""
WebSocket功能测试脚本
测试流式推送、断线重连、心跳检测等功能
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import websockets
from datetime import datetime
import random
import time


class WebSocketTestClient:
    """WebSocket测试客户端"""
    
    def __init__(self, url: str, client_id: str):
        self.url = url
        self.client_id = client_id
        self.ws = None
        self.running = True
        self.message_count = 0
        self.last_sequence = 0
        
    async def connect(self):
        """连接到服务器"""
        uri = f"{self.url}?client_id={self.client_id}"
        print(f"🔗 连接到: {uri}")
        
        try:
            self.ws = await websockets.connect(uri)
            print(f"✅ 连接成功！客户端ID: {self.client_id}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
            
    async def send_message(self, message_type: str, data: dict):
        """发送消息"""
        if not self.ws:
            print("❌ WebSocket未连接")
            return
            
        message = {
            "type": message_type,
            "data": data
        }
        
        await self.ws.send(json.dumps(message))
        print(f"📤 发送消息: {message_type}")
        
    async def receive_messages(self):
        """接收消息"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                self.message_count += 1
                
                # 更新序列号
                if "sequence" in data:
                    self.last_sequence = data["sequence"]
                    
                msg_type = data.get("type")
                
                if msg_type == "ping":
                    # 响应心跳
                    await self.send_message("pong", {})
                    print(f"💓 心跳响应")
                elif msg_type == "stream_chunk":
                    # 流式数据
                    chunk_data = data.get("data", {})
                    if chunk_data.get("is_final"):
                        print(f"📦 流式传输完成，共{chunk_data.get('chunk_id')}个块")
                    else:
                        print(f"📦 接收流块 #{chunk_data.get('chunk_id')}: {len(chunk_data.get('content', ''))} 字节")
                elif msg_type == "connection":
                    print(f"🎉 {data.get('data', {}).get('status')}")
                else:
                    print(f"📥 收到消息 #{self.message_count}: {msg_type}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("🔌 连接已关闭")
        except Exception as e:
            print(f"❌ 接收消息错误: {e}")
            
    async def simulate_disconnect(self, duration: int = 5):
        """模拟断线"""
        print(f"🔌 模拟断线 {duration} 秒...")
        if self.ws:
            await self.ws.close()
        await asyncio.sleep(duration)
        print("🔄 尝试重连...")
        await self.connect()
        
    async def test_streaming(self):
        """测试流式传输"""
        print("\n📊 测试流式传输...")
        await self.send_message("request_stream", {
            "content": "生成一个长文本响应"
        })
        
    async def test_reconnect(self):
        """测试重连机制"""
        print("\n🔄 测试重连机制...")
        # 发送一些消息
        for i in range(3):
            await self.send_message("test", {"index": i})
            await asyncio.sleep(0.5)
            
        # 模拟断线
        await self.simulate_disconnect()
        
        # 发送重连消息
        await self.send_message("reconnect", {
            "last_sequence": self.last_sequence
        })
        
    async def run_tests(self):
        """运行所有测试"""
        if not await self.connect():
            return
            
        # 启动接收任务
        receive_task = asyncio.create_task(self.receive_messages())
        
        try:
            # 等待连接稳定
            await asyncio.sleep(1)
            
            # 测试基本消息
            print("\n📨 测试基本消息...")
            await self.send_message("test", {"message": "Hello, WebSocket!"})
            await asyncio.sleep(1)
            
            # 测试流式传输
            await self.test_streaming()
            await asyncio.sleep(3)
            
            # 测试重连
            await self.test_reconnect()
            await asyncio.sleep(5)
            
            # 等待心跳
            print("\n💓 等待心跳测试（30秒）...")
            await asyncio.sleep(30)
            
        except KeyboardInterrupt:
            print("\n⏹️ 测试中断")
        finally:
            self.running = False
            if self.ws:
                await self.ws.close()
            receive_task.cancel()
            
        print(f"\n📊 测试完成！")
        print(f"   总消息数: {self.message_count}")
        print(f"   最后序列号: {self.last_sequence}")


async def run_server_test():
    """测试服务器端功能"""
    print("=" * 60)
    print("🧪 WebSocket 服务器端测试")
    print("=" * 60)
    
    # 导入服务器模块
    from web.backend.services.streaming_service import streaming_service
    
    # 测试客户端ID
    test_client_id = "test_client_001"
    
    print("\n1️⃣ 测试消息发送...")
    success = await streaming_service.send_message(test_client_id, {
        "type": "test",
        "data": {"message": "Hello from server"}
    })
    print(f"   发送结果: {'✅ 成功' if success else '❌ 失败（客户端未连接）'}")
    
    print("\n2️⃣ 测试广播...")
    await streaming_service.broadcast({
        "type": "broadcast",
        "data": {"message": "System announcement"}
    })
    print("   ✅ 广播完成")
    
    print("\n3️⃣ 测试流式发送...")
    async def generate_stream():
        """生成流式数据"""
        for i in range(5):
            yield f"Data chunk {i+1}"
            await asyncio.sleep(0.1)
            
    await streaming_service.send_stream(test_client_id, generate_stream())
    print("   ✅ 流式发送完成")
    
    print("\n✅ 服务器端测试完成！")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WebSocket功能测试")
    parser.add_argument(
        "--mode", 
        choices=["client", "server"], 
        default="client",
        help="测试模式"
    )
    parser.add_argument(
        "--url",
        default="ws://localhost:8000/ws",
        help="WebSocket服务器URL"
    )
    parser.add_argument(
        "--client-id",
        default=f"test_client_{int(time.time())}",
        help="客户端ID"
    )
    
    args = parser.parse_args()
    
    if args.mode == "client":
        print("=" * 60)
        print("🧪 WebSocket 客户端测试")
        print("=" * 60)
        print(f"📍 服务器: {args.url}")
        print(f"🆔 客户端: {args.client_id}")
        print("=" * 60)
        
        client = WebSocketTestClient(args.url, args.client_id)
        await client.run_tests()
    else:
        await run_server_test()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 测试结束")
