#!/usr/bin/env python3
"""
RuleK API 修复验证脚本 - 第二轮
验证所有新修复是否成功
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


async def verify_remaining_fixes():
    """验证剩余问题的修复"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         RuleK API 第二轮修复验证                           ║
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
        
        print("\n📝 测试剩余的3个问题...")
        
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
            
            # 创建一个规则（为了让游戏更有内容）
            print("\n1️⃣ 测试规则创建...")
            response = await client.post(f"/api/games/{game_id}/rules", json={
                "name": "测试规则",
                "description": "验证修复",
                "cost": 100,
                "trigger": {
                    "type": "time",
                    "conditions": {"time": "night"}
                },
                "effect": {
                    "type": "fear_increase",
                    "value": 20
                },
                "requirements": {}
            })
            
            if response.status_code == 200:
                print("✅ 规则创建成功")
            else:
                print(f"❌ 规则创建失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
            
            # 测试问题1：规则成本计算（之前RuleTrigger未定义）
            print("\n2️⃣ 测试规则成本计算（修复RuleTrigger问题）...")
            response = await client.post("/api/rules/calculate-cost", json={
                "name": "成本测试",
                "trigger": {"type": "time", "probability": 0.5},
                "effects": [{"type": "fear_increase", "value": 50}]
            })
            
            if response.status_code == 200:
                cost_data = response.json()
                print(f"✅ 成本计算成功: {cost_data.get('cost')}点 - RuleTrigger问题已修复")
            else:
                print(f"❌ 成本计算失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return False
            
            # 测试问题2：推进回合（之前NPC object has no attribute 'get'）
            print("\n3️⃣ 测试推进回合（修复NPC.get问题）...")
            response = await client.post(f"/api/games/{game_id}/turn")
            
            if response.status_code == 200:
                turn_data = response.json()
                print(f"✅ 推进回合成功 - 回合{turn_data.get('turn', 0)} - NPC处理问题已修复")
            else:
                print(f"❌ 推进回合失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return False
            
            # 测试问题3：保存游戏（之前NPCPersonality序列化问题）
            print("\n4️⃣ 测试保存游戏（修复序列化问题）...")
            response = await client.post(f"/api/games/{game_id}/save")
            
            if response.status_code == 200:
                save_data = response.json()
                filename = save_data.get('filename')
                print(f"✅ 保存游戏成功: {filename} - 序列化问题已修复")
                
                # 额外测试：尝试加载保存的游戏
                print("\n5️⃣ 额外测试：加载游戏...")
                response = await client.post("/api/games/load", params={"filename": filename})
                if response.status_code == 200:
                    print(f"✅ 加载游戏成功")
                else:
                    print(f"⚠️ 加载游戏失败（非关键）: {response.status_code}")
                    
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


async def run_complete_test():
    """运行完整测试"""
    success = await verify_remaining_fixes()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有剩余问题修复验证通过！")
        print("\n📊 修复总结:")
        print("  ✅ RuleTrigger未定义 -> 改用TriggerCondition")
        print("  ✅ NPC.get错误 -> 修复NPC对象创建")
        print("  ✅ NPCPersonality序列化 -> 使用model_dump(mode='json')")
        print("\n✨ 现在运行完整测试应该100%通过")
        print("\n建议:")
        print("  1. 运行完整测试: python scripts/test/test_api_comprehensive.py")
        print("  2. 或使用一键测试: python scripts/test/restart_and_test.py")
    else:
        print("⚠️ 仍有问题需要解决")
        print("请检查服务器日志获取更多信息")
    print("=" * 60)
    
    return success


def main():
    """主函数"""
    try:
        success = asyncio.run(run_complete_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)


if __name__ == "__main__":
    main()
