#!/usr/bin/env python3
"""
RuleK API 修复验证脚本
验证所有修复是否成功
"""
import asyncio
import httpx
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8000"


async def verify_fixes():
    """验证修复"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         RuleK API 修复验证                                 ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 检查服务器
        try:
            response = await client.get("/health")
            print("✅ 服务器运行正常")
        except:
            print("❌ 服务器未运行！请先启动: python rulek.py web")
            return False
        
        # 创建测试游戏
        print("\n📝 测试修复的功能...")
        
        try:
            # 1. 创建游戏
            response = await client.post("/api/games", json={
                "difficulty": "normal",
                "npc_count": 3
            })
            if response.status_code != 200:
                print("❌ 创建游戏失败")
                return False
            
            game_data = response.json()
            game_id = game_data.get("game_id")
            print(f"✅ 游戏创建成功: {game_id}")
            
            # 2. 测试规则创建（之前失败的）
            print("测试规则创建...")
            response = await client.post(f"/api/games/{game_id}/rules", json={
                "name": "测试规则",
                "description": "验证修复",
                "cost": 100,
                "trigger": {
                    "type": "time",
                    "conditions": {"time": "night"}
                },
                "effect": {  # 使用单数effect
                    "type": "fear_increase",
                    "value": 20
                },
                "requirements": {}
            })
            
            if response.status_code == 200:
                print("✅ 规则创建成功 - 问题1已修复")
            else:
                print(f"❌ 规则创建失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return False
            
            # 3. 测试规则成本计算（之前失败的）
            print("测试规则成本计算...")
            response = await client.post("/api/rules/calculate-cost", json={
                "name": "成本测试",
                "trigger": {"type": "time", "probability": 0.5},
                "effects": [{"type": "fear_increase", "value": 50}]
            })
            
            if response.status_code == 200:
                cost_data = response.json()
                print(f"✅ 成本计算成功: {cost_data.get('cost')}点 - 问题2已修复")
            else:
                print(f"❌ 成本计算失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return False
            
            # 4. 测试推进回合（之前失败的）
            print("测试推进回合...")
            response = await client.post(f"/api/games/{game_id}/turn")
            
            if response.status_code == 200:
                print("✅ 推进回合成功 - 问题3已修复")
            else:
                print(f"❌ 推进回合失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return False
            
            # 5. 测试保存游戏（之前失败的）
            print("测试保存游戏...")
            response = await client.post(f"/api/games/{game_id}/save")
            
            if response.status_code == 200:
                save_data = response.json()
                print(f"✅ 保存游戏成功: {save_data.get('filename')} - 问题4已修复")
            else:
                print(f"❌ 保存游戏失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return False
            
            # 清理
            await client.delete(f"/api/games/{game_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ 测试过程出错: {e}")
            return False


async def run_full_test():
    """运行完整测试"""
    success = await verify_fixes()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有修复验证通过！")
        print("✨ API现在应该100%正常工作")
        print("\n建议运行完整测试套件:")
        print("  python scripts/test/test_api_comprehensive.py")
    else:
        print("⚠️ 仍有问题需要解决")
        print("请检查服务器日志获取更多信息")
    print("=" * 60)
    
    return success


def main():
    """主函数"""
    try:
        success = asyncio.run(run_full_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)


if __name__ == "__main__":
    main()
