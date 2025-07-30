#!/usr/bin/env python3
"""
import datetime
RuleK AI功能优化工具
专门优化和调试AI相关功能
"""

import os
import sys
from pathlib import Path
import json
import asyncio
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class AIOptimizer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.issues = []
        self.optimizations = []
        
    async def optimize_ai(self):
        """优化AI功能"""
        print("🤖 RuleK AI功能优化工具")
        print("=" * 50)
        
        # 1. 检查AI配置
        self.check_ai_config()
        
        # 2. 测试AI连接
        await self.test_ai_connection()
        
        # 3. 优化AI调用
        self.optimize_ai_calls()
        
        # 4. 创建Mock模式增强
        self.enhance_mock_mode()
        
        # 5. 生成优化报告
        self.generate_optimization_report()
        
    def check_ai_config(self):
        """检查AI配置"""
        print("\n📋 检查AI配置...")
        
        # 检查环境变量
        api_key = os.getenv('DEEPSEEK_API_KEY', '').strip()
        if not api_key:
            print("⚠️  未设置DEEPSEEK_API_KEY，将使用Mock模式")
            self.issues.append("未设置API密钥")
        else:
            print("✅ 已配置API密钥")
            
        # 检查配置文件
        config_file = self.project_root / "config" / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    
                ai_enabled = config.get('game', {}).get('ai_enabled', False)
                if not ai_enabled:
                    print("⚠️  配置文件中AI功能未启用")
                    self.optimizations.append({
                        "type": "config",
                        "action": "启用AI功能",
                        "file": "config/config.json",
                        "change": "设置 game.ai_enabled = true"
                    })
                else:
                    print("✅ AI功能已启用")
                    
            except Exception as e:
                self.issues.append(f"配置文件读取错误: {e}")
                
    async def test_ai_connection(self):
        """测试AI连接"""
        print("\n🔌 测试AI连接...")
        
        try:
            from src.api.deepseek_client import DeepSeekClient
            from src.config import APIConfig
            
            # 创建配置
            api_config = APIConfig(
                deepseek_api_key=os.getenv('DEEPSEEK_API_KEY', 'mock'),
                model="deepseek-chat",
                timeout=10,
                max_retries=1
            )
            
            # 如果没有真实API密钥，使用Mock模式
            if api_config.deepseek_api_key == 'mock':
                print("ℹ️  使用Mock模式测试")
                self.create_enhanced_mock()
            else:
                # 尝试真实连接
                try:
                    async with DeepSeekClient(api_config) as client:
                        # 简单测试
                        result = await client.evaluate_rule_nl(
                            "测试规则",
                            {"rule_count": 0, "avg_fear": 50, "places": ["客厅"]}
                        )
                        print("✅ AI连接成功")
                except Exception as e:
                    print(f"❌ AI连接失败: {e}")
                    self.issues.append(f"AI连接失败: {e}")
                    self.create_enhanced_mock()
                    
        except ImportError as e:
            print(f"❌ 导入失败: {e}")
            self.issues.append(f"AI模块导入失败: {e}")
            
    def optimize_ai_calls(self):
        """优化AI调用"""
        print("\n⚡ 优化AI调用...")
        
        # 检查并优化AI相关文件
        ai_files = [
            "src/api/deepseek_client.py",
            "src/ai/turn_pipeline.py",
            "src/core/game_state.py"
        ]
        
        for file_path in ai_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.optimize_file(full_path)
                
    def optimize_file(self, file_path: Path):
        """优化单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查常见问题
            optimizations = []
            
            # 1. 添加超时处理
            if "timeout" not in content and "deepseek" in file_path.name:
                optimizations.append("添加超时处理")
                
            # 2. 添加重试机制
            if "retry" not in content and "api" in str(file_path):
                optimizations.append("添加重试机制")
                
            # 3. 添加错误降级
            if "try:" in content and "except:" in content:
                if "logger.error" not in content:
                    optimizations.append("添加错误日志")
                    
            if optimizations:
                self.optimizations.append({
                    "type": "code",
                    "file": str(file_path.relative_to(self.project_root)),
                    "suggestions": optimizations
                })
                
        except Exception as e:
            self.issues.append(f"无法优化{file_path}: {e}")
            
    def create_enhanced_mock(self):
        """创建增强的Mock模式"""
        print("\n🎭 创建增强Mock模式...")
        
        mock_file = self.project_root / "src" / "api" / "mock_ai.py"
        
        mock_content = '''"""
增强的Mock AI模式
在没有API密钥时提供基础AI功能
"""

import random
from typing import List, Dict, Any
from src.api.schemas import TurnPlan, DialogueTurn, PlannedAction, RuleEvalResult, RuleTrigger, RuleEffect

class MockAI:
    """Mock AI实现"""
    
    def __init__(self):
        self.dialogue_templates = [
            "我感觉这里不太对劲...",
            "刚才好像听到了什么声音",
            "我们应该小心一点",
            "这个地方让人毛骨悚然",
            "快看，那是什么？",
            "我觉得我们应该分头行动",
            "不，我们应该待在一起",
            "这里的规则太诡异了"
        ]
        
        self.action_types = ["move", "search", "wait", "investigate"]
        
    async def generate_turn_plan(self, npcs: List[Dict], context: Dict) -> TurnPlan:
        """生成回合计划"""
        dialogues = []
        actions = []
        
        # 生成对话
        for i, npc in enumerate(npcs[:3]):  # 最多3个NPC对话
            if npc.get('is_alive', True):
                dialogue = DialogueTurn(
                    speaker=npc['name'],
                    text=random.choice(self.dialogue_templates)
                )
                dialogues.append(dialogue)
                
        # 生成行动
        for npc in npcs:
            if npc.get('is_alive', True) and random.random() > 0.3:
                action = PlannedAction(
                    npc=npc['name'],
                    action=random.choice(self.action_types),
                    target=random.choice(context.get('available_places', ['客厅'])),
                    reason="直觉告诉我应该这么做"
                )
                actions.append(action)
                
        return TurnPlan(dialogue=dialogues, actions=actions)
        
    async def generate_narrative(self, events: List[Dict]) -> str:
        """生成叙事"""
        templates = [
            "夜幕降临，恐惧在空气中蔓延。{}",
            "诡异的氛围笼罩着整个空间。{}",
            "时间仿佛凝固了，每个人都感到不安。{}"
        ]
        
        event_text = "发生了一些诡异的事情。"
        if events:
            event_text = f"{events[0].get('description', '未知事件')}。"
            
        return random.choice(templates).format(event_text)
        
    async def evaluate_rule(self, rule_text: str, context: Dict) -> RuleEvalResult:
        """评估规则"""
        # 简单的规则解析
        cost = random.randint(100, 300)
        difficulty = random.randint(3, 7)
        
        return RuleEvalResult(
            name=f"规则: {rule_text[:20]}...",
            trigger=RuleTrigger(type="action", conditions=["触发条件"]),
            effect=RuleEffect(type="fear", params={"amount": 20}),
            cost=cost,
            difficulty=difficulty,
            loopholes=["可能的破绽"],
            suggestion="这是一个有趣的规则"
        )

# 全局Mock实例
mock_ai = MockAI()
'''
        
        try:
            # 确保目录存在
            mock_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(mock_file, 'w', encoding='utf-8') as f:
                f.write(mock_content)
                
            print("✅ 创建了增强Mock模式")
            self.optimizations.append({
                "type": "feature",
                "action": "创建Mock AI",
                "file": "src/api/mock_ai.py",
                "benefit": "无需API密钥也能测试AI功能"
            })
            
        except Exception as e:
            self.issues.append(f"创建Mock模式失败: {e}")
            
    def enhance_mock_mode(self):
        """增强Mock模式集成"""
        print("\n🔧 增强Mock模式集成...")
        
        # 修改DeepSeekClient以支持Mock模式
        client_file = self.project_root / "src" / "api" / "deepseek_client.py"
        
        if client_file.exists():
            try:
                with open(client_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否已有Mock支持
                if "mock_ai" not in content:
                    print("  添加Mock模式支持到DeepSeekClient...")
                    self.optimizations.append({
                        "type": "integration",
                        "action": "集成Mock模式",
                        "file": "src/api/deepseek_client.py",
                        "change": "在API调用失败时自动切换到Mock模式"
                    })
                    
            except Exception as e:
                self.issues.append(f"无法增强Mock模式: {e}")
                
    def generate_optimization_report(self):
        """生成优化报告"""
        print("\n" + "=" * 50)
        print("📊 AI优化报告")
        print("=" * 50)
        
        if not self.issues and not self.optimizations:
            print("\n✅ AI功能状态良好，无需优化！")
        else:
            if self.issues:
                print(f"\n发现的问题 ({len(self.issues)}个):")
                for issue in self.issues:
                    print(f"  ❌ {issue}")
                    
            if self.optimizations:
                print(f"\n建议的优化 ({len(self.optimizations)}个):")
                for opt in self.optimizations:
                    print(f"\n  📌 {opt['type'].upper()}: {opt.get('action', opt.get('file'))}")
                    if 'suggestions' in opt:
                        for sug in opt['suggestions']:
                            print(f"     - {sug}")
                    if 'change' in opt:
                        print(f"     → {opt['change']}")
                    if 'benefit' in opt:
                        print(f"     ✨ {opt['benefit']}")
                        
        # 保存报告
        self.save_optimization_report()
        
    def save_optimization_report(self):
        """保存优化报告"""
        report_file = self.project_root / "ai_optimization_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# RuleK AI优化报告\n\n")
            f.write(f"生成时间: {datetime.datetime.now()}\n\n")
            
            if self.issues:
                f.write("## 发现的问题\n\n")
                for i, issue in enumerate(self.issues, 1):
                    f.write(f"{i}. {issue}\n")
                f.write("\n")
                
            if self.optimizations:
                f.write("## 优化建议\n\n")
                for opt in self.optimizations:
                    f.write(f"### {opt['type'].upper()}: {opt.get('action', opt.get('file'))}\n")
                    if 'suggestions' in opt:
                        f.write("建议:\n")
                        for sug in opt['suggestions']:
                            f.write(f"- {sug}\n")
                    if 'change' in opt:
                        f.write(f"\n变更: {opt['change']}\n")
                    if 'benefit' in opt:
                        f.write(f"\n好处: {opt['benefit']}\n")
                    f.write("\n")
                    
        print(f"\n详细报告已保存到: ai_optimization_report.md")

async def main():
    optimizer = AIOptimizer()
    await optimizer.optimize_ai()

if __name__ == "__main__":
    asyncio.run(main())
