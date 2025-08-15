#!/usr/bin/env python
"""
test_ai_core_optimization.py - AI核心化优化测试脚本
用于验证Web端AI核心化改造的功能和性能
"""

import asyncio
import time
import json
import statistics
from typing import List, Dict, Any
import aiohttp
from datetime import datetime
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 测试配置
API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
TEST_RESULTS_DIR = Path("test_results/ai_core")

# 确保测试结果目录存在
TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


class AIOptimizationTester:
    """AI核心化优化测试器"""
    
    def __init__(self):
        self.session = None
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "performance_metrics": {},
            "summary": {}
        }
    
    async def setup(self):
        """初始化测试环境"""
        self.session = aiohttp.ClientSession()
        print("🚀 AI核心化优化测试开始")
        print(f"   API地址: {API_BASE_URL}")
        print("-" * 50)
    
    async def teardown(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
        
        # 保存测试结果
        result_file = TEST_RESULTS_DIR / f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 50)
        print(f"📊 测试结果已保存到: {result_file}")
    
    async def test_api_health(self) -> bool:
        """测试1: API健康检查"""
        test_name = "API健康检查"
        print(f"\n📌 {test_name}")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # 验证AI核心化标识
                    assert data.get("ai_core") == True, "AI核心化未启用"
                    assert data.get("cache_enabled") == True, "缓存未启用"
                    assert data.get("streaming_enabled") == True, "流式推送未启用"
                    
                    self.add_test_result(test_name, True, "API健康检查通过")
                    print(f"   ✅ 通过 - AI核心化已启用")
                    return True
                else:
                    self.add_test_result(test_name, False, f"状态码: {resp.status}")
                    print(f"   ❌ 失败 - 状态码: {resp.status}")
                    return False
                    
        except Exception as e:
            self.add_test_result(test_name, False, str(e))
            print(f"   ❌ 失败 - {e}")
            return False
    
    async def test_game_creation_with_auto_ai(self) -> str:
        """测试2: 游戏创建自动启用AI"""
        test_name = "游戏创建（自动AI）"
        print(f"\n📌 {test_name}")
        
        try:
            payload = {
                "difficulty": "normal",
                "npc_count": 4
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{API_BASE_URL}/api/games",
                json=payload
            ) as resp:
                response_time = time.time() - start_time
                
                if resp.status == 200:
                    data = await resp.json()
                    game_id = data.get("game_id")
                    
                    # 验证AI自动启用
                    assert data.get("ai_enabled") == True, "AI未自动启用"
                    assert data.get("ai_initialized") == True, "AI未自动初始化"
                    
                    self.add_test_result(test_name, True, f"游戏ID: {game_id}")
                    self.add_performance_metric("game_creation_time", response_time)
                    
                    print(f"   ✅ 通过 - 游戏创建成功")
                    print(f"   📊 响应时间: {response_time:.3f}秒")
                    print(f"   🎮 游戏ID: {game_id}")
                    
                    return game_id
                else:
                    self.add_test_result(test_name, False, f"状态码: {resp.status}")
                    print(f"   ❌ 失败 - 状态码: {resp.status}")
                    return None
                    
        except Exception as e:
            self.add_test_result(test_name, False, str(e))
            print(f"   ❌ 失败 - {e}")
            return None
    
    async def test_smart_turn_response_time(self, game_id: str) -> bool:
        """测试3: 智能回合响应时间"""
        test_name = "智能回合响应时间"
        print(f"\n📌 {test_name}")
        
        if not game_id:
            print("   ⚠️  跳过 - 无有效游戏ID")
            return False
        
        try:
            payload = {"action": "advance"}
            response_times = []
            
            # 执行5次测试取平均值
            for i in range(5):
                start_time = time.time()
                
                async with self.session.post(
                    f"{API_BASE_URL}/api/games/{game_id}/turn",
                    json=payload
                ) as resp:
                    # 测量到第一个字节的时间（TTFB）
                    first_byte_time = time.time() - start_time
                    
                    # 读取完整响应
                    data = await resp.json()
                    full_response_time = time.time() - start_time
                    
                    if resp.status == 200:
                        response_times.append(first_byte_time)
                        
                        # 检查分层响应
                        assert "basic_update" in data, "缺少基础更新"
                        assert "ai_content" in data, "缺少AI内容"
                        
                        print(f"   测试 {i+1}/5:")
                        print(f"     首字节时间: {first_byte_time:.3f}秒")
                        print(f"     完整响应时间: {full_response_time:.3f}秒")
                        print(f"     缓存命中: {data.get('cache_hit', False)}")
            
            # 计算统计数据
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            # 验证性能目标
            success = avg_time < 0.5  # 目标：<0.5秒
            
            self.add_test_result(test_name, success, f"平均: {avg_time:.3f}s")
            self.add_performance_metric("smart_turn_avg_time", avg_time)
            self.add_performance_metric("smart_turn_min_time", min_time)
            self.add_performance_metric("smart_turn_max_time", max_time)
            
            print(f"\n   📊 性能统计:")
            print(f"     平均响应时间: {avg_time:.3f}秒")
            print(f"     最快响应时间: {min_time:.3f}秒")
            print(f"     最慢响应时间: {max_time:.3f}秒")
            
            if success:
                print(f"   ✅ 通过 - 达到性能目标(<0.5秒)")
            else:
                print(f"   ⚠️  警告 - 未达到性能目标")
            
            return success
            
        except Exception as e:
            self.add_test_result(test_name, False, str(e))
            print(f"   ❌ 失败 - {e}")
            return False
    
    async def test_smart_rule_creation(self, game_id: str) -> bool:
        """测试4: 智能规则创建"""
        test_name = "智能规则创建"
        print(f"\n📌 {test_name}")
        
        if not game_id:
            print("   ⚠️  跳过 - 无有效游戏ID")
            return False
        
        try:
            payload = {
                "description": "晚上10点后在走廊说话的人会被传送到地下室",
                "auto_create": False
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{API_BASE_URL}/api/games/{game_id}/rules/smart",
                json=payload
            ) as resp:
                response_time = time.time() - start_time
                
                if resp.status == 200:
                    data = await resp.json()
                    
                    # 验证解析结果
                    assert "parsed_rule" in data, "缺少解析结果"
                    assert "estimated_cost" in data, "缺少成本估算"
                    assert "suggestions" in data, "缺少优化建议"
                    
                    self.add_test_result(test_name, True, "规则解析成功")
                    self.add_performance_metric("rule_parsing_time", response_time)
                    
                    print(f"   ✅ 通过 - 规则解析成功")
                    print(f"   📊 解析时间: {response_time:.3f}秒")
                    print(f"   💰 估算成本: {data['estimated_cost']}")
                    print(f"   💡 建议数量: {len(data['suggestions'])}")
                    
                    return True
                else:
                    self.add_test_result(test_name, False, f"状态码: {resp.status}")
                    print(f"   ❌ 失败 - 状态码: {resp.status}")
                    return False
                    
        except Exception as e:
            self.add_test_result(test_name, False, str(e))
            print(f"   ❌ 失败 - {e}")
            return False
    
    async def test_websocket_streaming(self, game_id: str) -> bool:
        """测试5: WebSocket流式推送"""
        test_name = "WebSocket流式推送"
        print(f"\n📌 {test_name}")
        
        if not game_id:
            print("   ⚠️  跳过 - 无有效游戏ID")
            return False
        
        try:
            ws_url = f"{WS_BASE_URL}/ws/{game_id}"
            
            async with self.session.ws_connect(ws_url) as ws:
                # 发送订阅消息
                await ws.send_json({
                    "type": "subscribe_streaming"
                })
                
                # 接收连接确认
                msg = await ws.receive_json()
                assert msg.get("type") == "connected", "连接确认失败"
                assert msg.get("streaming_supported") == True, "流式推送未支持"
                
                # 测试ping-pong
                await ws.send_json({"type": "ping"})
                msg = await ws.receive_json()
                assert msg.get("type") == "pong", "Ping-pong测试失败"
                
                await ws.close()
                
                self.add_test_result(test_name, True, "WebSocket连接成功")
                print(f"   ✅ 通过 - WebSocket流式推送可用")
                return True
                
        except Exception as e:
            self.add_test_result(test_name, False, str(e))
            print(f"   ❌ 失败 - {e}")
            return False
    
    async def test_cache_performance(self, game_id: str) -> bool:
        """测试6: 缓存性能"""
        test_name = "缓存性能"
        print(f"\n📌 {test_name}")
        
        if not game_id:
            print("   ⚠️  跳过 - 无有效游戏ID")
            return False
        
        try:
            # 执行多次相同请求测试缓存
            cache_hits = 0
            total_requests = 10
            
            for i in range(total_requests):
                async with self.session.post(
                    f"{API_BASE_URL}/api/games/{game_id}/turn",
                    json={"action": "test"}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("cache_hit", False):
                            cache_hits += 1
                        
                        print(f"   请求 {i+1}/{total_requests}: {'缓存命中' if data.get('cache_hit') else '缓存未命中'}")
            
            # 计算缓存命中率
            hit_rate = cache_hits / total_requests
            success = hit_rate >= 0.5  # 目标：>50%（考虑到冷启动）
            
            self.add_test_result(test_name, success, f"命中率: {hit_rate:.1%}")
            self.add_performance_metric("cache_hit_rate", hit_rate)
            
            print(f"\n   📊 缓存统计:")
            print(f"     总请求数: {total_requests}")
            print(f"     缓存命中: {cache_hits}")
            print(f"     命中率: {hit_rate:.1%}")
            
            if success:
                print(f"   ✅ 通过 - 缓存性能良好")
            else:
                print(f"   ⚠️  警告 - 缓存命中率偏低")
            
            return success
            
        except Exception as e:
            self.add_test_result(test_name, False, str(e))
            print(f"   ❌ 失败 - {e}")
            return False
    
    async def test_fallback_mechanism(self, game_id: str) -> bool:
        """测试7: 降级机制"""
        test_name = "降级机制"
        print(f"\n📌 {test_name}")
        
        # 这个测试需要模拟AI失败的情况
        # 实际测试中可能需要特殊的测试端点
        print("   ℹ️  降级机制需要特殊测试环境")
        self.add_test_result(test_name, None, "需要特殊测试环境")
        return True
    
    def add_test_result(self, name: str, success: bool, details: str = ""):
        """添加测试结果"""
        self.results["tests"].append({
            "name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_performance_metric(self, metric_name: str, value: float):
        """添加性能指标"""
        self.results["performance_metrics"][metric_name] = value
    
    def generate_summary(self):
        """生成测试摘要"""
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for t in self.results["tests"] if t["success"] == True)
        failed_tests = sum(1 for t in self.results["tests"] if t["success"] == False)
        skipped_tests = sum(1 for t in self.results["tests"] if t["success"] is None)
        
        self.results["summary"] = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "pass_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
        }
        
        print("\n" + "=" * 50)
        print("📊 测试总结")
        print(f"   总测试数: {total_tests}")
        print(f"   ✅ 通过: {passed_tests}")
        print(f"   ❌ 失败: {failed_tests}")
        print(f"   ⚠️  跳过: {skipped_tests}")
        print(f"   通过率: {self.results['summary']['pass_rate']}")
        
        if self.results["performance_metrics"]:
            print("\n📈 性能指标")
            for metric, value in self.results["performance_metrics"].items():
                if isinstance(value, float):
                    if "time" in metric:
                        print(f"   {metric}: {value:.3f}秒")
                    elif "rate" in metric:
                        print(f"   {metric}: {value:.1%}")
                    else:
                        print(f"   {metric}: {value:.3f}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        await self.setup()
        
        try:
            # 基础测试
            await self.test_api_health()
            
            # 创建游戏并获取ID
            game_id = await self.test_game_creation_with_auto_ai()
            
            if game_id:
                # 功能测试
                await self.test_smart_turn_response_time(game_id)
                await self.test_smart_rule_creation(game_id)
                await self.test_websocket_streaming(game_id)
                await self.test_cache_performance(game_id)
                await self.test_fallback_mechanism(game_id)
            
            # 生成摘要
            self.generate_summary()
            
        finally:
            await self.teardown()


async def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════╗
║         RuleK AI核心化优化测试套件               ║
║                                                  ║
║  测试内容：                                      ║
║  1. API健康检查                                  ║
║  2. 游戏创建（自动AI）                           ║
║  3. 智能回合响应时间                             ║
║  4. 智能规则创建                                 ║
║  5. WebSocket流式推送                            ║
║  6. 缓存性能                                     ║
║  7. 降级机制                                     ║
╚══════════════════════════════════════════════════╝
    """)
    
    tester = AIOptimizationTester()
    await tester.run_all_tests()
    
    print("\n✨ 测试完成！")


if __name__ == "__main__":
    # 确保服务器正在运行
    print("⚠️  请确保Web服务器正在运行（http://localhost:8000）")
    print("   如未运行，请先执行: python web/backend/app.py")
    print("")
    
    input("按Enter键开始测试...")
    
    asyncio.run(main())
