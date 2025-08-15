#!/usr/bin/env python
"""
test_current_api.py - 测试当前API功能
用于验证现有Web服务器是否正常工作
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

API_BASE_URL = "http://localhost:8000"


async def test_current_api():
    """测试当前API"""
    print("""
╔══════════════════════════════════════════════════╗
║           RuleK 当前API测试                      ║
╚══════════════════════════════════════════════════╝
    """)
    
    async with aiohttp.ClientSession() as session:
        # 1. 测试根路径
        print("\n📌 测试1: API根路径")
        try:
            async with session.get(f"{API_BASE_URL}/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   ✅ 成功 - API版本: {data.get('version', 'unknown')}")
                    print(f"   状态: {data.get('status', 'unknown')}")
                else:
                    print(f"   ❌ 失败 - 状态码: {resp.status}")
        except Exception as e:
            print(f"   ❌ 失败 - {e}")
            print("\n⚠️  服务器未运行！请先启动服务器：")
            print("   python start_web_server.py")
            return
        
        # 2. 测试健康检查
        print("\n📌 测试2: 健康检查")
        try:
            async with session.get(f"{API_BASE_URL}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   ✅ 成功 - 状态: {data.get('status', 'unknown')}")
                    print(f"   活跃游戏数: {data.get('active_games', 0)}")
                else:
                    print(f"   ❌ 失败 - 状态码: {resp.status}")
        except Exception as e:
            print(f"   ❌ 失败 - {e}")
        
        # 3. 测试创建游戏
        print("\n📌 测试3: 创建游戏")
        try:
            payload = {
                "difficulty": "normal",
                "npc_count": 4
            }
            async with session.post(f"{API_BASE_URL}/api/games", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    game_id = data.get("game_id", data.get("state", {}).get("game_id"))
                    print(f"   ✅ 成功 - 游戏ID: {game_id}")
                    
                    # 4. 测试获取游戏状态
                    if game_id:
                        print("\n📌 测试4: 获取游戏状态")
                        async with session.get(f"{API_BASE_URL}/api/games/{game_id}") as resp2:
                            if resp2.status == 200:
                                state_data = await resp2.json()
                                print(f"   ✅ 成功")
                                print(f"   回合: {state_data.get('state', {}).get('current_turn', 'unknown')}")
                                print(f"   恐惧积分: {state_data.get('state', {}).get('fear_points', 'unknown')}")
                            else:
                                print(f"   ❌ 失败 - 状态码: {resp2.status}")
                    
                    # 5. 测试AI状态（如果存在）
                    if game_id:
                        print("\n📌 测试5: AI状态检查")
                        try:
                            async with session.get(f"{API_BASE_URL}/api/games/{game_id}/ai/status") as resp3:
                                if resp3.status == 200:
                                    ai_data = await resp3.json()
                                    print(f"   ✅ AI端点存在")
                                    print(f"   AI启用: {ai_data.get('ai_enabled', False)}")
                                    print(f"   AI初始化: {ai_data.get('ai_initialized', False)}")
                                elif resp3.status == 404:
                                    print(f"   ⚠️  AI端点不存在（正常，当前版本）")
                                else:
                                    print(f"   ❌ 失败 - 状态码: {resp3.status}")
                        except Exception as e:
                            print(f"   ⚠️  AI功能未实现: {e}")
                    
                    # 6. 测试删除游戏
                    if game_id:
                        print("\n📌 测试6: 删除游戏")
                        async with session.delete(f"{API_BASE_URL}/api/games/{game_id}") as resp4:
                            if resp4.status == 200:
                                print(f"   ✅ 成功 - 游戏已删除")
                            else:
                                print(f"   ❌ 失败 - 状态码: {resp4.status}")
                    
                else:
                    print(f"   ❌ 失败 - 状态码: {resp.status}")
                    text = await resp.text()
                    print(f"   错误信息: {text}")
        except Exception as e:
            print(f"   ❌ 失败 - {e}")
    
    print("\n" + "=" * 50)
    print("✨ 测试完成！")


async def main():
    """主函数"""
    await test_current_api()


if __name__ == "__main__":
    print("⚠️  请确保Web服务器正在运行")
    print("   如未运行，请在另一个终端执行：")
    print("   python start_web_server.py")
    print("")
    
    input("按Enter键开始测试...")
    
    asyncio.run(main())
