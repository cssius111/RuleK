"""
规则怪谈游戏 - 最小可运行演示
这是一个简化版的游戏循环，展示核心机制
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, List

# 导入我们的模型（假设已经创建）
try:
    from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType
except ImportError:
    print("请先运行 quick_start.py 创建项目结构")
    exit(1)


class SimpleGameDemo:
    """简化版游戏演示"""
    
    def __init__(self):
        self.fear_points = 1000
        self.turn = 0
        self.npcs = []
        self.rules = []
        self.game_log = []
        
    def log(self, message: str):
        """记录游戏日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.game_log.append(log_entry)
        print(log_entry)
        
    async def create_demo_rule(self):
        """创建一个演示规则"""
        rule = Rule(
            id="demo_rule_001",
            name="禁止回头",
            description="在走廊里回头会看到不该看到的东西",
            trigger=TriggerCondition(
                action="turn_around",
                location=["corridor"],
                probability=0.7
            ),
            effect=RuleEffect(
                type=EffectType.FEAR_GAIN,
                fear_gain=50,
                side_effects=["see_shadow", "hear_whisper"]
            ),
            base_cost=100
        )
        
        cost = rule.calculate_total_cost()
        if self.fear_points >= cost:
            self.fear_points -= cost
            self.rules.append(rule)
            self.log(f"✨ 创建规则 [{rule.name}]，花费 {cost} 恐惧点数")
        else:
            self.log("❌ 恐惧点数不足！")
            
    def create_demo_npcs(self):
        """创建演示NPC"""
        npc_names = ["小明", "小红", "老王", "阿姨"]
        for name in npc_names:
            npc = {
                "name": name,
                "hp": 100,
                "sanity": random.randint(70, 100),
                "location": random.choice(["living_room", "corridor", "bedroom"]),
                "fear": 0
            }
            self.npcs.append(npc)
            self.log(f"👤 {name} 进入了游戏")
            
    async def simulate_turn(self):
        """模拟一个回合"""
        self.turn += 1
        self.log(f"\n{'='*50}")
        self.log(f"🌙 第 {self.turn} 回合开始")
        self.log(f"💰 当前恐惧点数: {self.fear_points}")
        
        # 模拟NPC行动
        for npc in self.npcs:
            if npc["hp"] <= 0:
                continue
                
            # 随机行动
            actions = ["move", "investigate", "talk", "turn_around"]
            action = random.choice(actions)
            
            # 检查是否触发规则
            for rule in self.rules:
                if rule.active and action == rule.trigger.action:
                    if random.random() < rule.trigger.probability:
                        self.log(f"⚡ {npc['name']} 触发了规则 [{rule.name}]!")
                        
                        # 应用效果
                        if rule.effect.type == EffectType.FEAR_GAIN:
                            gained = rule.effect.fear_gain
                            self.fear_points += gained
                            npc["fear"] += 20
                            self.log(f"😱 获得 {gained} 恐惧点数！")
                            
                        # 副作用
                        for side_effect in rule.effect.side_effects:
                            self.log(f"   💀 {side_effect}")
                            
            # 更新NPC状态
            if npc["fear"] > 50:
                npc["sanity"] -= 10
                if npc["sanity"] <= 0:
                    self.log(f"🤯 {npc['name']} 精神崩溃了！")
                    npc["hp"] = 0
                    
    async def run_game(self, turns: int = 5):
        """运行游戏"""
        self.log("🎮 游戏开始！")
        self.log("📖 这是一个简化的规则怪谈游戏演示")
        
        # 初始化
        self.create_demo_npcs()
        await self.create_demo_rule()
        
        # 游戏循环
        for _ in range(turns):
            await self.simulate_turn()
            await asyncio.sleep(1)  # 模拟延迟
            
            # 检查游戏结束条件
            alive_npcs = [npc for npc in self.npcs if npc["hp"] > 0]
            if not alive_npcs:
                self.log("\n💀 所有NPC都已经倒下，游戏结束！")
                break
                
        # 游戏总结
        self.log(f"\n{'='*50}")
        self.log("📊 游戏总结")
        self.log(f"   总回合数: {self.turn}")
        self.log(f"   最终恐惧点数: {self.fear_points}")
        self.log(f"   存活NPC: {len([n for n in self.npcs if n['hp'] > 0])}/{len(self.npcs)}")
        

async def main():
    """主函数"""
    print("\n" + "="*60)
    print("🎭 规则怪谈管理者 - 游戏演示")
    print("="*60 + "\n")
    
    game = SimpleGameDemo()
    await game.run_game(turns=5)
    
    print("\n演示结束！下一步：")
    print("1. 查看 src/models/rule.py 了解规则系统")
    print("2. 运行 pip install -r requirements.txt 安装依赖")
    print("3. 开始构建完整的游戏系统")


if __name__ == "__main__":
    asyncio.run(main())
