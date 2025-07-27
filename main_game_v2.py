#!/usr/bin/env python3
"""
规则怪谈管理者 - 主游戏文件 (Sprint 2 版本)
整合所有组件，包括AI对话和叙事系统
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
from src.models.npc import NPC, generate_random_npc, NPCAction, NPCStatus
from src.ui.cli import CLI

# 导入新的AI组件
from src.api.deepseek_client import DeepSeekClient, APIConfig
from src.core.dialogue_system import DialogueSystem, DialogueType, DialogueContext
from src.core.narrator import Narrator, GameEvent, EventSeverity, NarrativeStyle

# 如果缺少colorama，使用简单的打印
try:
    from colorama import init
    init()
except ImportError:
    print("提示: 安装 colorama 以获得更好的显示效果 (pip install colorama)")


class RuleKGame:
    """主游戏类 - Sprint 2 增强版"""
    
    def __init__(self):
        self.cli = CLI()
        self.game_state = GameStateManager()
        self.current_game_id = None
        self.running = True
        
        # 初始化AI系统
        self.api_client = None
        self.dialogue_system = None
        self.narrator = None
        
        # 游戏中的NPC对象（使用新的NPC模型）
        self.npcs: List[NPC] = []
        
        # 游戏事件记录
        self.turn_events: List[GameEvent] = []
        
        # 对话历史
        self.last_dialogue_turn = -1
        
    async def initialize_ai_systems(self):
        """初始化AI系统"""
        # 创建API客户端（默认使用Mock模式）
        config = APIConfig(mock_mode=True)
        
        # 检查是否有配置文件
        config_path = "config/deepseek_config.json"
        if os.path.exists(config_path):
            import json
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                if config_data.get("api_key"):
                    config.api_key = config_data["api_key"]
                    config.mock_mode = False
                    
        self.api_client = DeepSeekClient(config)
        self.dialogue_system = DialogueSystem(self.api_client)
        self.narrator = Narrator(self.api_client)
        
    async def cleanup_ai_systems(self):
        """清理AI系统"""
        if self.api_client:
            await self.api_client.close()
            
    async def main_menu(self):
        """主菜单"""
        # 初始化AI系统
        await self.initialize_ai_systems()
        
        while self.running:
            self.cli.clear_screen()
            self.cli.print_header("🎭 规则怪谈管理者 v2.0 🎭")
            
            print("欢迎来到规则怪谈的世界！")
            print("在这里，你将扮演规则的制定者...")
            print("通过创造诡异的规则来收集恐惧点数！\n")
            print("✨ 新功能：AI驱动的NPC对话和故事叙述")
            
            self.cli.print_menu([
                ("1", "开始新游戏"),
                ("2", "继续游戏"),
                ("3", "游戏说明"),
                ("4", "AI设置"),
                ("5", "关于")
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
                await self.ai_settings()
            elif choice == "5":
                self.cli.show_credits()
            elif choice == "0":
                if self.cli.confirm("确定要退出游戏吗？"):
                    self.running = False
                    await self.cleanup_ai_systems()
                    print("\n感谢游玩！再见！👻")
                    break
                    
    async def ai_settings(self):
        """AI设置"""
        self.cli.clear_screen()
        self.cli.print_header("AI设置")
        
        print("当前AI模式:", "在线" if not self.api_client.config.mock_mode else "离线Mock")
        print("\n1. 切换AI模式")
        print("2. 设置叙事风格")
        print("0. 返回")
        
        choice = self.cli.get_input()
        
        if choice == "1":
            self.api_client.config.mock_mode = not self.api_client.config.mock_mode
            mode = "离线Mock" if self.api_client.config.mock_mode else "在线"
            self.cli.print_success(f"已切换到{mode}模式")
        elif choice == "2":
            styles = [
                (NarrativeStyle.HORROR, "恐怖 - 血腥诡异的描述"),
                (NarrativeStyle.SUSPENSE, "悬疑 - 紧张刺激的氛围"),
                (NarrativeStyle.DARK_HUMOR, "黑色幽默 - 讽刺的恐怖"),
                (NarrativeStyle.PSYCHOLOGICAL, "心理惊悚 - 深入人心的恐惧")
            ]
            style_choice = self.cli.select_from_list(styles, lambda x: x[1])
            if style_choice:
                self.narrator.set_style(style_choice[0])
                self.cli.print_success(f"叙事风格已设置为：{style_choice[1]}")
                
        self.cli.get_input("\n按回车继续...")
        
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
        
        # 初始化NPC（使用新的NPC模型）
        self.npcs = []
        npc_count = 4 if difficulty != "hard" else 6
        for i in range(npc_count):
            npc = generate_random_npc()
            self.npcs.append(npc)
            
            # 同时添加到game_state（保持兼容性）
            npc_dict = {
                "id": npc.id,
                "name": npc.name,
                "hp": npc.hp,
                "sanity": npc.sanity,
                "fear": npc.fear,
                "location": npc.location,
                "status": npc.status.value
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
        
        # 生成开场叙述
        intro_event = GameEvent(
            event_type="game_start",
            severity=EventSeverity.MAJOR,
            actors=[npc.name for npc in self.npcs],
            location="废弃公寓",
            details={"npcs": len(self.npcs)}
        )
        
        chapter = await self.narrator.narrate_turn([intro_event], {"current_turn": 0})
        
        print(chapter.title)
        print()
        await self.cli.animated_text(chapter.content, 0.03)
        
        self.cli.get_input("\n按回车开始游戏...")
        
    async def game_loop(self):
        """游戏主循环"""
        while not self.game_state.is_game_over:
            self.cli.clear_screen()
            
            # 清空本回合事件
            self.turn_events = []
            
            # 显示游戏状态
            self.cli.print_header(f"第 {self.game_state.current_turn} 回合")
            self.cli.print_fear_points(self.game_state.state.fear_points)
            self.cli.print_turn_info(
                self.game_state.current_turn, 
                self.game_state.get_time_display()
            )
            self.cli.print_separator()
            
            # 显示NPC简要状态
            active_npcs = [npc for npc in self.npcs if npc.status != NPCStatus.DEAD]
            print(f"\n存活NPC: {len(active_npcs)}")
            for npc in active_npcs[:3]:
                status_desc = npc.get_status_description()
                print(f"   • {status_desc}")
            if len(active_npcs) > 3:
                print(f"   ... 还有 {len(active_npcs) - 3} 个NPC")
                
            # 检查是否需要对话
            dialogue_type = self.dialogue_system.should_trigger_dialogue(
                {
                    "current_turn": self.game_state.current_turn,
                    "time_of_day": self.game_state.state.time_of_day,
                    "recent_events": self.turn_events
                },
                self.last_dialogue_turn
            )
            
            if dialogue_type:
                await self.run_dialogue(dialogue_type)
                
            # 游戏菜单
            self.cli.print_menu([
                ("1", "创建/管理规则"),
                ("2", "查看详细状态"),
                ("3", "推进回合"),
                ("4", "查看游戏日志"),
                ("5", "查看对话历史"),
                ("6", "保存游戏")
            ])
            
            choice = self.cli.get_input()
            
            if choice == "1":
                await self.manage_rules()
            elif choice == "2":
                await self.view_status()
            elif choice == "3":
                await self.advance_turn()
            elif choice == "4":
                self.view_logs()
            elif choice == "5":
                self.view_dialogue_history()
            elif choice == "6":
                self.save_game()
            elif choice == "0":
                if self.cli.confirm("要返回主菜单吗？(未保存的进度将丢失)"):
                    break
                    
        # 游戏结束
        if self.game_state.is_game_over:
            await self.game_over()
            
    async def run_dialogue(self, dialogue_type: DialogueType):
        """运行对话轮次"""
        self.cli.clear_screen()
        self.cli.print_header("💬 NPC对话")
        
        # 选择参与对话的NPC
        active_npcs = [npc for npc in self.npcs if npc.status != NPCStatus.DEAD]
        if len(active_npcs) < 2:
            return
            
        # 随机选择2-4个NPC参与对话
        participants = random.sample(active_npcs, min(random.randint(2, 4), len(active_npcs)))
        
        # 创建对话上下文
        context = DialogueContext(
            location=participants[0].location,
            time=self.game_state.get_time_display(),
            participants=[npc.id for npc in participants],
            recent_events=[event.__dict__ for event in self.turn_events[-3:]],
            mood="fearful" if any(npc.fear > 50 for npc in participants) else "tense"
        )
        
        # 生成对话
        print("正在生成对话...")
        dialogue_entry = await self.dialogue_system.generate_dialogue_round(
            participants,
            context,
            dialogue_type,
            self.game_state.current_turn
        )
        
        # 显示对话
        self.cli.clear_screen()
        self.cli.print_header(f"💬 {dialogue_type.value.title()}对话")
        print(f"\n地点：{context.location}")
        print(f"时间：{context.time}")
        print()
        
        for dialogue in dialogue_entry.dialogues:
            print(f"{dialogue['speaker']}: {dialogue['text']}")
            await asyncio.sleep(1)  # 逐句显示
            
        # 显示对话效果
        if dialogue_entry.effects:
            print("\n[对话产生了一些影响...]")
            for effect in dialogue_entry.effects:
                if effect['type'] == 'fear_spread':
                    print(f"• 恐慌在蔓延... (+{effect['amount']} 恐惧)")
                elif effect['type'] == 'reduce_fear':
                    print(f"• 相互安慰减少了恐惧")
                    
        self.last_dialogue_turn = self.game_state.current_turn
        self.cli.get_input("\n按回车继续...")
        
    async def manage_rules(self):
        """管理规则"""
        self.cli.clear_screen()
        self.cli.print_header("规则管理")
        
        print("1. 创建新规则")
        print("2. 查看现有规则")
        print("3. 升级规则")
        print("0. 返回")
        
        choice = self.cli.get_input()
        
        if choice == "1":
            await self.create_rule()
        elif choice == "2":
            self.view_rules()
        elif choice == "3":
            self.cli.print_warning("规则升级功能即将推出...")
            self.cli.get_input("\n按回车返回...")
            
    async def create_rule(self):
        """创建规则"""
        rule_data = self.cli.create_rule_wizard()
        if not rule_data:
            return
            
        # 让AI评估规则
        if not self.api_client.config.mock_mode:
            print("\n正在评估规则...")
            evaluation = await self.api_client.evaluate_rule(
                rule_data,
                {
                    "rule_count": len(self.game_state.rules),
                    "avg_fear": sum(npc.fear for npc in self.npcs) / len(self.npcs)
                }
            )
            
            print(f"\nAI评估：")
            print(f"建议成本：{evaluation.get('cost_estimate', 150)}")
            print(f"难度等级：{evaluation.get('difficulty', 5)}/10")
            if evaluation.get('suggestion'):
                print(f"建议：{evaluation['suggestion']}")
                
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
                    
                    # 记录事件
                    self.turn_events.append(GameEvent(
                        event_type="rule_created",
                        severity=EventSeverity.MODERATE,
                        actors=["管理者"],
                        location="系统",
                        details={"rule_name": rule.name, "cost": cost}
                    ))
                    
        except Exception as e:
            self.cli.print_error(f"创建规则失败: {e}")
            
        self.cli.get_input("\n按回车继续...")
        
    def view_rules(self):
        """查看规则列表"""
        self.cli.clear_screen()
        self.cli.print_header("现有规则")
        
        if not self.game_state.rules:
            print("还没有创建任何规则")
        else:
            for i, rule in enumerate(self.game_state.rules, 1):
                print(f"\n{i}. {rule.name}")
                print(f"   触发：{rule.trigger.action}")
                print(f"   效果：{rule.effect.type.value}")
                print(f"   已触发：{rule.times_triggered}次")
                
        self.cli.get_input("\n按回车返回...")
        
    async def view_status(self):
        """查看详细状态"""
        self.cli.clear_screen()
        self.cli.print_header("游戏详细状态")
        
        # NPC状态
        print("\n📊 NPC状态:")
        self.cli.print_separator()
        for npc in self.npcs:
            print(f"\n{npc.get_status_description()}")
            print(f"   HP: {npc.hp}/100 | 理智: {npc.sanity}/100 | 恐惧: {npc.fear}/100")
            print(f"   位置: {npc.location}")
            print(f"   性格: 理性{npc.personality.rationality} 勇气{npc.personality.courage}")
            if npc.memory.known_rules:
                print(f"   已知规则: {len(npc.memory.known_rules)}条")
            if npc.inventory:
                print(f"   物品: {', '.join(npc.inventory)}")
                
        # 规则状态
        print("\n📜 活跃规则:")
        self.cli.print_separator()
        if self.game_state.rules:
            for rule in self.game_state.rules:
                print(f"\n• {rule.name}")
                print(f"  触发条件: {rule.trigger.action}")
                print(f"  效果: {rule.effect.type.value}")
                print(f"  触发次数: {rule.times_triggered}")
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
        
        active_npcs = [npc for npc in self.npcs if npc.status != NPCStatus.DEAD]
        
        for npc in active_npcs:
            # 使用NPC的决策系统
            context = {
                "nearby_npcs": [other.id for other in active_npcs if other.id != npc.id and other.location == npc.location]
            }
            action = npc.decide_action(context)
            
            if action:
                print(f"\n{npc.name} 决定 {action.value}...")
                
                # 检查是否触发规则
                for rule in self.game_state.get_active_rules():
                    if action.value == rule.trigger.action:
                        # 检查其他条件
                        if not rule.can_trigger({"actor_location": npc.location}):
                            continue
                            
                        # 概率判定
                        if random.random() < rule.trigger.probability:
                            # 触发规则！
                            print(f"\n⚡ {npc.name} 触发了规则 [{rule.name}]!")
                            
                            # 应用效果
                            result = rule.apply_effect({"name": npc.name})
                            
                            # 更新游戏状态
                            self.game_state.state.rules_triggered += 1
                            
                            # 记录事件
                            event = GameEvent(
                                event_type="rule_triggered",
                                severity=EventSeverity.MAJOR,
                                actors=[npc.name],
                                location=npc.location,
                                details={
                                    "rule_name": rule.name,
                                    "rule_id": rule.id,
                                    "result": result
                                }
                            )
                            self.turn_events.append(event)
                            
                            if result.get('target_died'):
                                npc.hp = 0
                                npc.update_status()
                                self.game_state.state.npcs_died += 1
                                
                                # 死亡事件
                                death_event = GameEvent(
                                    event_type="npc_death",
                                    severity=EventSeverity.CRITICAL,
                                    actors=[npc.name],
                                    location=npc.location,
                                    details={
                                        "victim": npc.name,
                                        "cause": rule.name
                                    }
                                )
                                self.turn_events.append(death_event)
                                
                                # 其他NPC观察到死亡
                                for other_npc in active_npcs:
                                    if other_npc.id != npc.id:
                                        other_npc.observe_event("npc_death", {
                                            "victim": npc.name,
                                            "location": npc.location,
                                            "turn": self.game_state.current_turn
                                        })
                                
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
                event_type = random.choice(event_types)
                npc.add_fear(10)
                
                event = GameEvent(
                    event_type="environmental",
                    severity=EventSeverity.MINOR,
                    actors=[npc.name],
                    location=npc.location,
                    details={"type": event_type}
                )
                self.turn_events.append(event)
                
        # 生成叙事
        print("\n📖 本回合叙述:")
        self.cli.print_separator()
        
        if self.turn_events:
            chapter = await self.narrator.narrate_turn(
                self.turn_events,
                {
                    "current_turn": self.game_state.current_turn,
                    "time_of_day": self.game_state.state.time_of_day,
                    "average_fear": sum(npc.fear for npc in self.npcs) / len(self.npcs) if self.npcs else 0
                }
            )
            
            print(chapter.title)
            print()
            print(chapter.content)
        else:
            print("这个回合相对平静...")
            
        # 检查游戏结束
        active_count = len([npc for npc in self.npcs if npc.status != NPCStatus.DEAD])
        if active_count == 0:
            self.game_state.is_game_over = True
            
        self.cli.get_input("\n按回车继续...")
        
    def view_dialogue_history(self):
        """查看对话历史"""
        self.cli.clear_screen()
        self.cli.print_header("对话历史")
        
        summary = self.dialogue_system.get_dialogue_summary()
        print(summary)
        
        self.cli.get_input("\n按回车返回...")
        
    def view_logs(self):
        """查看游戏日志"""
        self.cli.clear_screen()
        self.cli.print_header("游戏日志")
        self.cli.print_game_log(self.game_state.game_log, limit=20)
        self.cli.get_input("\n按回车返回...")
        
    def save_game(self):
        """保存游戏"""
        # 保存NPC状态
        npc_data = []
        for npc in self.npcs:
            npc_data.append({
                "model": npc.dict(),
                "id": npc.id
            })
            
        # 保存到额外数据
        self.game_state.extra_data["npcs_full"] = npc_data
        self.game_state.extra_data["last_dialogue_turn"] = self.last_dialogue_turn
        
        if self.game_state.save_game():
            self.cli.print_success("游戏已保存！")
        else:
            self.cli.print_error("保存失败！")
        self.cli.get_input("\n按回车继续...")
        
    async def game_over(self):
        """游戏结束"""
        self.cli.clear_screen()
        self.cli.print_header("游戏结束")
        
        # 生成结局叙述
        final_events = [
            GameEvent(
                event_type="game_end",
                severity=EventSeverity.CRITICAL,
                actors=[npc.name for npc in self.npcs if npc.status == NPCStatus.DEAD],
                location="废弃公寓",
                details={
                    "survivors": len([npc for npc in self.npcs if npc.status != NPCStatus.DEAD]),
                    "total_npcs": len(self.npcs)
                }
            )
        ]
        
        final_chapter = await self.narrator.narrate_turn(final_events, {
            "current_turn": self.game_state.current_turn,
            "time_of_day": "dawn"
        })
        
        print(final_chapter.content)
        print()
        
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
        await game.cleanup_ai_systems()
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        await game.cleanup_ai_systems()
        

if __name__ == "__main__":
    # Windows下的事件循环策略
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())
