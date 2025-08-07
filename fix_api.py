#!/usr/bin/env python3
"""
RuleK API 修复和测试脚本
解决游戏状态404问题
"""

import httpx
import asyncio
import json
from typing import Optional

API_BASE = "http://localhost:8000"

class RuleKAPIClient:
    """RuleK API 客户端"""
    
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.game_id: Optional[str] = None
    
    async def check_server(self) -> bool:
        """检查服务器是否运行"""
        try:
            response = await self.client.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 服务器运行正常: {data['name']} v{data['version']}")
                return True
        except Exception as e:
            print(f"❌ 服务器连接失败: {e}")
        return False
    
    async def create_game(self, difficulty: str = "normal", npc_count: int = 4) -> Optional[str]:
        """创建新游戏"""
        try:
            print(f"\n🎮 创建新游戏...")
            response = await self.client.post(
                f"{self.base_url}/api/games",
                json={"difficulty": difficulty, "npc_count": npc_count}
            )
            if response.status_code == 200:
                data = response.json()
                self.game_id = data["game_id"]
                print(f"✅ 游戏创建成功!")
                print(f"   游戏ID: {self.game_id}")
                print(f"   NPC数量: {len(data['npcs'])}")
                print(f"   当前回合: {data['current_turn']}")
                print(f"   恐惧点数: {data['fear_points']}")
                return self.game_id
            else:
                print(f"❌ 创建失败: {response.status_code}")
                print(f"   错误: {response.text}")
        except Exception as e:
            print(f"❌ 创建游戏异常: {e}")
        return None
    
    async def get_game_state(self, game_id: str = None) -> dict:
        """获取游戏状态"""
        gid = game_id or self.game_id
        if not gid:
            print("❌ 没有游戏ID")
            return {}
        
        try:
            print(f"\n📊 获取游戏状态: {gid}")
            response = await self.client.get(f"{self.base_url}/api/games/{gid}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 游戏状态:")
                print(f"   回合: {data['current_turn']}")
                print(f"   阶段: {data['phase']}")
                print(f"   模式: {data['mode']}")
                print(f"   恐惧点数: {data['fear_points']}")
                print(f"   存活NPC: {sum(1 for npc in data['npcs'] if npc['is_alive'])}/{len(data['npcs'])}")
                return data
            else:
                print(f"❌ 获取失败: {response.status_code}")
                if response.status_code == 404:
                    print("   游戏不存在，需要先创建游戏")
        except Exception as e:
            print(f"❌ 获取状态异常: {e}")
        return {}
    
    async def create_rule(self, name: str, description: str, cost: int = 100) -> bool:
        """创建规则"""
        if not self.game_id:
            print("❌ 没有游戏ID")
            return False
        
        try:
            print(f"\n📝 创建规则: {name}")
            rule_data = {
                "name": name,
                "description": description,
                "requirements": {"time": "night"},
                "trigger": {"type": "time"},
                "effect": {"type": "damage", "value": 10},
                "cost": cost
            }
            response = await self.client.post(
                f"{self.base_url}/api/games/{self.game_id}/rules",
                json=rule_data
            )
            if response.status_code == 200:
                print(f"✅ 规则创建成功!")
                return True
            else:
                print(f"❌ 创建失败: {response.status_code}")
                print(f"   错误: {response.text}")
        except Exception as e:
            print(f"❌ 创建规则异常: {e}")
        return False
    
    async def advance_turn(self) -> bool:
        """推进回合"""
        if not self.game_id:
            print("❌ 没有游戏ID")
            return False
        
        try:
            print(f"\n⏭️ 推进回合...")
            response = await self.client.post(
                f"{self.base_url}/api/games/{self.game_id}/turn"
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 回合推进成功!")
                print(f"   结果: {json.dumps(data, ensure_ascii=False, indent=2)}")
                return True
            else:
                print(f"❌ 推进失败: {response.status_code}")
                print(f"   错误: {response.text}")
        except Exception as e:
            print(f"❌ 推进回合异常: {e}")
        return False
    
    async def init_ai(self) -> bool:
        """初始化AI系统"""
        if not self.game_id:
            print("❌ 没有游戏ID")
            return False
        
        try:
            print(f"\n🤖 初始化AI系统...")
            response = await self.client.post(
                f"{self.base_url}/api/games/{self.game_id}/ai/init"
            )
            if response.status_code == 200:
                print(f"✅ AI初始化成功!")
                return True
            else:
                print(f"❌ 初始化失败: {response.status_code}")
                print(f"   错误: {response.text}")
        except Exception as e:
            print(f"❌ AI初始化异常: {e}")
        return False
    
    async def run_ai_turn(self) -> bool:
        """执行AI回合"""
        if not self.game_id:
            print("❌ 没有游戏ID")
            return False
        
        try:
            print(f"\n🎭 执行AI回合...")
            response = await self.client.post(
                f"{self.base_url}/api/games/{self.game_id}/ai/turn",
                json={"force_dialogue": True, "include_hidden_events": False}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ AI回合执行成功!")
                print(f"\n对话:")
                for d in data.get("dialogue", []):
                    print(f"  {d['speaker']}: {d['text']}")
                print(f"\n行动:")
                for a in data.get("actions", []):
                    print(f"  {a['npc']} -> {a['action']}")
                return True
            else:
                print(f"❌ 执行失败: {response.status_code}")
                print(f"   错误: {response.text}")
        except Exception as e:
            print(f"❌ AI回合异常: {e}")
        return False
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


async def run_complete_test():
    """运行完整测试流程"""
    print("=" * 60)
    print("🎮 RuleK API 完整测试流程")
    print("=" * 60)
    
    client = RuleKAPIClient()
    
    try:
        # 1. 检查服务器
        if not await client.check_server():
            print("\n⚠️ 请先启动服务器: python start_web_server.py")
            return
        
        # 2. 创建游戏
        game_id = await client.create_game(difficulty="normal", npc_count=4)
        if not game_id:
            print("\n❌ 游戏创建失败，测试终止")
            return
        
        # 3. 获取游戏状态
        await client.get_game_state()
        
        # 4. 创建规则
        await client.create_rule(
            name="午夜禁言",
            description="午夜时分，任何说话的人都会受到惩罚",
            cost=100
        )
        
        # 5. 推进回合
        await client.advance_turn()
        
        # 6. 尝试AI功能（如果配置了API密钥）
        print("\n" + "=" * 60)
        print("🤖 测试AI功能")
        print("=" * 60)
        
        if await client.init_ai():
            await client.run_ai_turn()
        else:
            print("⚠️ AI功能未配置或初始化失败")
        
        # 7. 最终状态
        print("\n" + "=" * 60)
        print("📊 最终游戏状态")
        print("=" * 60)
        await client.get_game_state()
        
        print("\n" + "=" * 60)
        print("✅ 测试完成!")
        print(f"🎮 游戏ID: {client.game_id}")
        print("💡 你可以使用这个ID继续测试其他功能")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
    finally:
        await client.close()


async def quick_fix_test(game_id: str = None):
    """快速修复测试 - 针对已知的游戏ID"""
    client = RuleKAPIClient()
    
    try:
        if not await client.check_server():
            print("\n⚠️ 请先启动服务器")
            return
        
        if game_id:
            # 尝试获取现有游戏
            state = await client.get_game_state(game_id)
            if state:
                client.game_id = game_id
                print(f"\n✅ 使用现有游戏: {game_id}")
            else:
                print(f"\n⚠️ 游戏 {game_id} 不存在，创建新游戏...")
                await client.create_game()
        else:
            # 创建新游戏
            await client.create_game()
        
        # 执行基本操作
        await client.create_rule("测试规则", "这是一个测试规则")
        await client.advance_turn()
        
    finally:
        await client.close()


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        # 如果提供了游戏ID，使用快速测试
        game_id = sys.argv[1]
        print(f"使用游戏ID: {game_id}")
        asyncio.run(quick_fix_test(game_id))
    else:
        # 否则运行完整测试
        asyncio.run(run_complete_test())


if __name__ == "__main__":
    main()
