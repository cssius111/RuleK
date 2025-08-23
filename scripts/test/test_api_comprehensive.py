#!/usr/bin/env python3
"""
RuleK API 综合测试脚本
测试所有API端点功能
"""
import asyncio
import httpx
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 配置
BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

class APITester:
    """API测试器"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT)
        self.game_id = None
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log(self, message: str, level: str = "INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbol = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "📝")
        print(f"[{timestamp}] {symbol} {message}")
        
    async def test_endpoint(self, name: str, method: str, path: str, 
                           data: Optional[Dict] = None, 
                           expected_status: int = 200) -> bool:
        """测试单个端点"""
        self.total_tests += 1
        try:
            self.log(f"测试 {name}: {method} {path}")
            
            if method == "GET":
                response = await self.client.get(path)
            elif method == "POST":
                response = await self.client.post(path, json=data)
            elif method == "PUT":
                response = await self.client.put(path, json=data)
            elif method == "DELETE":
                response = await self.client.delete(path)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            if response.status_code == expected_status:
                self.log(f"  状态码: {response.status_code} ✓", "SUCCESS")
                self.passed_tests += 1
                
                # 显示响应内容摘要
                if response.headers.get("content-type", "").startswith("application/json"):
                    data = response.json()
                    if isinstance(data, dict):
                        keys = list(data.keys())[:5]
                        self.log(f"  响应键: {keys}")
                        
                return True
            else:
                self.log(f"  状态码错误: 期望 {expected_status}, 实际 {response.status_code}", "ERROR")
                self.log(f"  响应: {response.text[:200]}", "ERROR")
                self.failed_tests += 1
                return False
                
        except httpx.ConnectError:
            self.log(f"  连接失败 - 服务器未运行？", "ERROR")
            self.failed_tests += 1
            return False
        except Exception as e:
            self.log(f"  异常: {e}", "ERROR")
            self.failed_tests += 1
            return False
    
    async def test_basic_endpoints(self):
        """测试基础端点"""
        self.log("=" * 60)
        self.log("测试基础端点", "INFO")
        self.log("=" * 60)
        
        # 测试根路径
        await self.test_endpoint("根路径", "GET", "/")
        
        # 测试健康检查
        await self.test_endpoint("健康检查", "GET", "/health")
        
    async def test_game_management(self):
        """测试游戏管理"""
        self.log("=" * 60)
        self.log("测试游戏管理", "INFO")
        self.log("=" * 60)
        
        # 创建游戏
        result = await self.test_endpoint(
            "创建游戏", "POST", "/api/games",
            data={"difficulty": "normal", "npc_count": 5}
        )
        
        if result:
            # 获取游戏ID
            response = await self.client.post(
                "/api/games",
                json={"difficulty": "normal", "npc_count": 5}
            )
            if response.status_code == 200:
                game_data = response.json()
                self.game_id = game_data.get("game_id")
                self.log(f"  游戏ID: {self.game_id}")
                
                # 获取游戏状态
                await self.test_endpoint(
                    "获取游戏状态", "GET", f"/api/games/{self.game_id}"
                )
                
                # 获取NPC列表
                await self.test_endpoint(
                    "获取NPC列表", "GET", f"/api/games/{self.game_id}/npcs"
                )
                
                # 获取规则列表
                await self.test_endpoint(
                    "获取规则列表", "GET", f"/api/games/{self.game_id}/rules"
                )
    
    async def test_rule_management(self):
        """测试规则管理"""
        if not self.game_id:
            self.log("跳过规则测试 - 无游戏ID", "WARNING")
            return
            
        self.log("=" * 60)
        self.log("测试规则管理", "INFO")
        self.log("=" * 60)
        
        # 获取规则模板
        await self.test_endpoint("获取规则模板", "GET", "/api/rules/templates")
        
        # 创建自定义规则
        rule_data = {
            "name": "测试规则",
            "description": "这是一个测试规则",
            "cost": 100,
            "trigger": {
                "type": "time",
                "conditions": {"time": "night"}
            },
            "effect": {  # 修改为单数 effect，不是 effects
                "type": "fear_increase",
                "value": 20
            },
            "requirements": {}  # 添加requirements字段
        }
        
        await self.test_endpoint(
            "创建规则", "POST", f"/api/games/{self.game_id}/rules",
            data=rule_data
        )
        
        # 计算规则成本
        await self.test_endpoint(
            "计算规则成本", "POST", "/api/rules/calculate-cost",
            data=rule_data
        )
    
    async def test_ai_features(self):
        """测试AI功能"""
        if not self.game_id:
            self.log("跳过AI测试 - 无游戏ID", "WARNING")
            return
            
        self.log("=" * 60)
        self.log("测试AI功能", "INFO")
        self.log("=" * 60)
        
        # 检查AI状态
        await self.test_endpoint(
            "AI状态", "GET", f"/api/games/{self.game_id}/ai/status"
        )
        
        # 初始化AI
        await self.test_endpoint(
            "初始化AI", "POST", f"/api/games/{self.game_id}/ai/init"
        )
        
        # AI解析规则
        await self.test_endpoint(
            "AI解析规则", "POST", "/api/ai/parse-rule",
            data={
                "description": "当NPC在晚上独处时，恐惧值增加50点",
                "game_id": self.game_id
            }
        )
        
        # AI生成叙事
        await self.test_endpoint(
            "AI生成叙事", "POST", f"/api/games/{self.game_id}/ai/narrative",
            data={
                "include_hidden_events": False,
                "style": "horror"
            }
        )
    
    async def test_turn_management(self):
        """测试回合管理"""
        if not self.game_id:
            self.log("跳过回合测试 - 无游戏ID", "WARNING")
            return
            
        self.log("=" * 60)
        self.log("测试回合管理", "INFO")
        self.log("=" * 60)
        
        # 推进回合
        await self.test_endpoint(
            "推进回合", "POST", f"/api/games/{self.game_id}/turn"
        )
        
        # AI回合
        await self.test_endpoint(
            "AI回合", "POST", f"/api/games/{self.game_id}/ai/turn",
            data={"force_dialogue": False}
        )
    
    async def test_game_persistence(self):
        """测试游戏存储"""
        if not self.game_id:
            self.log("跳过存储测试 - 无游戏ID", "WARNING")
            return
            
        self.log("=" * 60)
        self.log("测试游戏存储", "INFO")
        self.log("=" * 60)
        
        # 保存游戏
        result = await self.test_endpoint(
            "保存游戏", "POST", f"/api/games/{self.game_id}/save"
        )
        
        if result:
            # 获取保存的文件名
            response = await self.client.post(f"/api/games/{self.game_id}/save")
            if response.status_code == 200:
                save_data = response.json()
                filename = save_data.get("filename")
                
                if filename:
                    # 加载游戏
                    await self.test_endpoint(
                        "加载游戏", "POST", "/api/games/load",
                        data={"filename": filename}
                    )
        
        # 删除游戏
        await self.test_endpoint(
            "删除游戏", "DELETE", f"/api/games/{self.game_id}"
        )
    
    def print_summary(self):
        """打印测试摘要"""
        self.log("=" * 60)
        self.log("测试摘要", "INFO")
        self.log("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        self.log(f"总测试数: {self.total_tests}")
        self.log(f"通过: {self.passed_tests} ✅", "SUCCESS")
        self.log(f"失败: {self.failed_tests} ❌", "ERROR" if self.failed_tests > 0 else "INFO")
        self.log(f"成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            self.log("API功能基本正常 ✨", "SUCCESS")
        elif success_rate >= 50:
            self.log("API存在一些问题，需要修复 ⚠️", "WARNING")
        else:
            self.log("API存在严重问题，需要立即修复 🚨", "ERROR")
    
    async def run_all_tests(self):
        """运行所有测试"""
        self.log("🚀 开始API综合测试", "INFO")
        self.log(f"目标服务器: {BASE_URL}")
        self.log("=" * 60)
        
        # 检查服务器是否运行
        try:
            response = await self.client.get("/health")
            self.log("服务器运行中 ✓", "SUCCESS")
        except httpx.ConnectError:
            self.log("服务器未运行！请先启动服务器：", "ERROR")
            self.log("  python rulek.py web", "ERROR")
            return False
        
        # 运行测试组
        await self.test_basic_endpoints()
        await self.test_game_management()
        await self.test_rule_management()
        await self.test_ai_features()
        await self.test_turn_management()
        await self.test_game_persistence()
        
        # 打印摘要
        self.print_summary()
        
        return self.failed_tests == 0

async def main():
    """主函数"""
    async with APITester() as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被中断")
        sys.exit(1)
