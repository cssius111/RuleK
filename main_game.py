#!/usr/bin/env python
"""
[DEPRECATED] 这个文件已被弃用，请使用 rulek.py 作为统一入口

运行游戏：
  python rulek.py          # 运行CLI游戏
  python rulek.py demo     # 运行演示
  python rulek.py web      # 启动Web服务器
"""
import warnings
warnings.warn(
    "main_game.py 已被弃用，请使用 'python rulek.py' 启动游戏",
    DeprecationWarning,
    stacklevel=2
)

import subprocess
import sys

# 重定向到新的入口
subprocess.run([sys.executable, "rulek.py"] + sys.argv[1:])3
"""
规则怪谈管理者 - 主游戏文件
整合所有组件，提供完整的游戏体验
"""
import asyncio
import sys
import os
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入游戏组件
from src.core.game_state import GameStateManager
from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType, RULE_TEMPLATES
from src.models.npc import NPC, generate_random_npc, NPCAction
from src.ui.cli import CLI

# 如果缺少colorama，使用简单的打印
try:
    from colorama import init
    init()
except ImportError:
    print("提示: 安装 colorama 以获得更好的显示效果 (pip install colorama)")


class RuleKGame:
    """主游戏类"""
    
    def __init__(self):
        self.cli = CLI()
        self.game_state = GameStateManager()
        self.current_game_id = None
        self.running = True
        
    async def main_menu(self):
        """主菜单"""
        while self.running:
            self.cli.clear_screen()
            self.cli.print_header("🎭 规则怪谈管理者 🎭")
            
            print("欢迎来到规则怪谈的世界！")
            print("在这里，你将扮演规则的制定者...")
            print("通过创造诡异的规则来收集恐惧点数！\n")
            
            self.cli.print_menu([
                ("1", "开始新游戏"),
                ("2", "继续游戏"),
                ("3", "游戏说明"),
                ("4", "关于")
            ])
            
            choice = self.cli.get_input()
            
            if choice == "1":
                await self.new_game()
            elif choice == "2":
                await self.load_game()
            elif choice == "3":
                self.cli.show_help()
                self.cli.get_input("\n按回车继续...")
            elif choice == "4":
                self.cli.show_credits()
            elif choice == "0":
                if self.cli.confirm("确定要退出游戏吗？"):
                    self.running = False
                    print("\n感谢游玩！再见！👻")
                    break
                    
    async def new_game(self):
        """开始新游戏"""
        self.cli.clear_screen()
        self.cli.print_header("新游戏设置")
        
        # 选择难度
        print("选择游戏难度:")
        difficulties = [
            ("easy", "简单 - 1500初始点数，NPC不太聪明"),
            ("normal", "普通 - 1000初始点数，标准难度"),
            ("hard", "困难 - 500初始点数，NPC更加警觉")
        ]
        
        diff_choice = self.cli.select_from_list(difficulties, lambda x: x[1])
        if not diff_choice:
            return
            
        difficulty = diff_choice[0]
        
        # 配置游戏
        config = {
            "difficulty": difficulty,
            "initial_fear_points": {"easy": 1500, "normal": 1000, "hard": 500}[difficulty]
        }
        
        # 创建游戏
        game_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.game_state.new_game(game_id, config)
        self.current_game_id = game_id
        
        # 初始化NPC
        npc_count = 4 if difficulty != "hard" else 6
        for i in range(npc_count):
            npc = generate_random_npc()
            # 转换为字典格式（临时解决方案）
            npc_dict = {
                "id": npc.id,
                "name": npc.name,
                "hp": npc.hp,
                "sanity": npc.sanity,
                "fear": npc.fear,
                "location": npc.location,
                "status": npc.status
            }
            self.game_state.add_npc(npc_dict)
            
        self.cli.print_success(f"新游戏创建成功！")
        await asyncio.sleep(1)
        
        # 显示开场
        await self.show_intro()
        
        # 进入游戏循环
        await self.game_loop()
        
    async def show_intro(self):
        """显示游戏开场"""
        self.cli.clear_screen()
        intro_text = """
        深夜，一栋废弃的公寓楼...
        
        几个不相识的人因为各种原因聚集在这里。
        他们不知道的是，这里即将成为恐怖规则的试验场。
        
        而你，作为规则的制定者，将决定他们的命运...
        """
        
        await self.cli.animated_text(intro_text, 0.05)
        self.cli.get_input("\n按回车开始游戏...")
        
    async def load_game(self):
        """加载游戏"""
        self.cli.clear_screen()
        self.cli.print_header("继续游戏")
        
        # 列出存档
        save_dir = self.game_state.save_dir
        saves = list(save_dir.glob("*.json"))
        
        if not saves:
            self.cli.print_warning("没有找到存档文件")
            self.cli.get_input("\n按回车返回...")
            return
            
        # 选择存档
        save_choice = self.cli.select_from_list(
            saves, 
            lambda x: x.stem.replace("game_", "").replace("_", " ")
        )
        
        if save_choice:
            game_id = save_choice.stem
            if self.game_state.load_game(game_id):
                self.current_game_id = game_id
                self.cli.print_success("游戏加载成功！")
                await asyncio.sleep(1)
                await self.game_loop()
            else:
                self.cli.print_error("加载失败！")
                self.cli.get_input("\n按回车返回...")
                
    async def game_loop(self):
        """游戏主循环"""
        while not self.game_state.is_game_over:
            self.cli.clear_screen()
            
            # 显示游戏状态
            self.cli.print_header(f"第 {self.game_state.current_turn} 回合")
            self.cli.print_fear_points(self.game_state.state.fear_points)
            self.cli.print_turn_info(
                self.game_state.current_turn, 
                self.game_state.get_time_display()
            )
            self.cli.print_separator()
            
            # 显示NPC简要状态
            active_npcs = self.game_state.get_active_npcs()
            print(f"\n存活NPC: {len(active_npcs)}")
            for npc in active_npcs[:3]:  # 只显示前3个
                self.cli.print_npc_status(npc)
            if len(active_npcs) > 3:
                print(f"   ... 还有 {len(active_npcs) - 3} 个NPC")
                
            # 游戏菜单
            self.cli.print_menu([
                ("1", "创建规则"),
                ("2", "查看详细状态"),
                ("3", "推进回合"),
                ("4", "查看游戏日志"),
                ("5", "保存游戏")
            ])
            
            choice = self.cli.get_input()
            
            if choice == "1":
                await self.create_rule()
            elif choice == "2":
                await self.view_status()
            elif choice == "3":
                await self.advance_turn()
            elif choice == "4":
                self.view_logs()
            elif choice == "5":
                self.save_game()
            elif choice == "0":
                if self.cli.confirm("要返回主菜单吗？(未保存的进度将丢失)"):
                    break
                    
        # 游戏结束
        if self.game_state.is_game_over:
            await self.game_over()
            
    async def create_rule(self):
        """创建规则"""
        rule_data = self.cli.create_rule_wizard()
        if not rule_data:
            return
            
        # 创建规则对象
        try:
            rule = Rule(
                id=f"rule_{len(self.game_state.rules) + 1:03d}",
                name=rule_data["name"],
                trigger=TriggerCondition(**rule_data["trigger"]),
                effect=RuleEffect(**rule_data["effect"])
            )
            
            # 计算成本
            cost = rule.calculate_total_cost()
            
            print(f"\n规则成本: {cost} 恐惧点数")
            
            if self.game_state.state.fear_points < cost:
                self.cli.print_error("恐惧点数不足！")
            elif self.cli.confirm(f"确认花费 {cost} 点创建此规则？"):
                if self.game_state.spend_fear_points(cost):
                    self.game_state.add_rule(rule)
                    self.cli.print_success("规则创建成功！")
                    
                    # 展示规则效果预览
                    print(f"\n当NPC {rule.trigger.action} 时...")
                    if rule.effect.type == EffectType.INSTANT_DEATH:
                        print("💀 将会立即死亡！")
                    elif rule.effect.type == EffectType.FEAR_GAIN:
                        print(f"😱 你将获得 {rule.effect.fear_gain} 恐惧点数！")
                        
        except Exception as e:
            self.cli.print_error(f"创建规则失败: {e}")
            
        self.cli.get_input("\n按回车继续...")
        
    async def view_status(self):
        """查看详细状态"""
        self.cli.clear_screen()
        self.cli.print_header("游戏详细状态")
        
        # NPC状态
        print("\n📊 NPC状态:")
        self.cli.print_separator()
        for npc in self.game_state.npcs:
            self.cli.print_npc_status(npc)
            
        # 规则状态
        print("\n📜 活跃规则:")
        self.cli.print_separator()
        if self.game_state.rules:
            for rule in self.game_state.rules:
                # 临时处理规则显示
                rule_dict = {
                    "name": rule.name,
                    "trigger": {"action": rule.trigger.action},
                    "effect": {"type": rule.effect.type},
                    "base_cost": rule.base_cost
                }
                self.cli.print_rule(rule_dict)
        else:
            print("还没有创建任何规则")
            
        # 统计信息
        print("\n📈 游戏统计:")
        self.cli.print_separator()
        print(f"总恐惧值获得: {self.game_state.state.total_fear_gained}")
        print(f"NPC死亡数: {self.game_state.state.npcs_died}")
        print(f"规则触发次数: {self.game_state.state.rules_triggered}")
        
        self.cli.get_input("\n按回车返回...")
        
    async def advance_turn(self):
        """推进回合"""
        self.cli.clear_screen()
        self.cli.print_header(f"回合 {self.game_state.current_turn + 1}")
        
        # 推进回合
        self.game_state.advance_turn()
        
        # NPC行动阶段
        print("\n🎭 NPC行动阶段:")
        self.cli.print_separator()
        
        active_npcs = self.game_state.get_active_npcs()
        events = []
        
        for npc in active_npcs:
            # 模拟NPC行动（简化版）
            actions = ["move", "investigate", "look_around", "look_mirror", "turn_around"]
            action = random.choice(actions)
            
            print(f"\n{npc['name']} 决定 {action}...")
            
            # 检查是否触发规则
            for rule in self.game_state.get_active_rules():
                if action == rule.trigger.action:
                    # 概率判定
                    if random.random() < rule.trigger.probability:
                        # 触发规则！
                        print(f"\n⚡ {npc['name']} 触发了规则 [{rule.name}]!")
                        
                        # 应用效果
                        result = rule.apply_effect(npc)
                        
                        # 更新游戏状态
                        self.game_state.state.rules_triggered += 1
                        
                        if result.get('target_died'):
                            npc['hp'] = 0
                            self.game_state.remove_npc(npc['id'])
                            events.append(f"{npc['name']} 死亡了！")
                            
                        if result.get('fear_gained', 0) > 0:
                            self.game_state.add_fear_points(
                                result['fear_gained'], 
                                f"规则 {rule.name}"
                            )
                            
                        # 显示消息
                        for msg in result.get('messages', []):
                            self.cli.print_warning(msg)
                            
                        await asyncio.sleep(1)  # 戏剧效果
                        break
                        
            # 随机事件
            if random.random() < 0.1:  # 10%概率
                event_types = ["strange_sound", "cold_wind", "shadow_movement"]
                event = random.choice(event_types)
                events.append(f"{npc['name']} 感觉到了{event}")
                npc['fear'] = min(100, npc.get('fear', 0) + 10)
                
        # 结算阶段
        print("\n📊 回合结算:")
        self.cli.print_separator()
        
        if events:
            for event in events:
                print(f"• {event}")
        else:
            print("这个回合相对平静...")
            
        # 检查游戏结束
        if self.game_state.is_game_over:
            return
            
        self.cli.get_input("\n按回车继续...")
        
    def view_logs(self):
        """查看游戏日志"""
        self.cli.clear_screen()
        self.cli.print_header("游戏日志")
        self.cli.print_game_log(self.game_state.game_log, limit=20)
        self.cli.get_input("\n按回车返回...")
        
    def save_game(self):
        """保存游戏"""
        if self.game_state.save_game():
            self.cli.print_success("游戏已保存！")
        else:
            self.cli.print_error("保存失败！")
        self.cli.get_input("\n按回车继续...")
        
    async def game_over(self):
        """游戏结束"""
        self.cli.clear_screen()
        self.cli.print_header("游戏结束")
        
        # 显示结束原因
        if len(self.game_state.get_active_npcs()) == 0:
            print("所有NPC都已经死亡...")
            print("没有人能够继续为你提供恐惧...")
        else:
            print("游戏时间结束...")
            
        # 显示最终统计
        summary = self.game_state.get_summary()
        print("\n📊 最终统计:")
        self.cli.print_separator()
        print(f"游戏回合: {summary['turns_played']}")
        print(f"最终恐惧点数: {summary['fear_points_final']}")
        print(f"总计获得恐惧: {summary['total_fear_gained']}")
        print(f"NPC存活率: {summary['survival_rate']}")
        print(f"规则触发次数: {summary['rules_triggered']}")
        
        # 评分
        score = summary['total_fear_gained'] - summary['npcs_died'] * 100
        print(f"\n最终得分: {score}")
        
        if score > 1000:
            print("\n🏆 完美的恐怖管理者！")
        elif score > 500:
            print("\n👍 不错的表现！")
        else:
            print("\n💀 还需要更多练习...")
            
        self.cli.get_input("\n按回车返回主菜单...")


async def main():
    """程序入口"""
    game = RuleKGame()
    
    try:
        await game.main_menu()
    except KeyboardInterrupt:
        print("\n\n游戏被中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        

if __name__ == "__main__":
    # Windows下的事件循环策略
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())
