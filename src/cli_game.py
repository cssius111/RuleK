"""
命令行游戏界面
提供简单的CLI界面来玩游戏
"""
# --- test-friendly pause helper ---
import os

def _pause():
    """Pause execution until the user presses Enter.

    If running under pytest (``PYTEST_RUNNING=1``), this returns immediately
    without waiting for input.
    """
    if os.getenv("PYTEST_RUNNING") == "1":
        return
    input("\n按回车继续...")
# --- end helper ---
import sys
import asyncio

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.game_state import GameStateManager
from src.core.enums import GamePhase, GameMode
from src.core.rule_executor import RuleExecutor, RuleContext
from src.core.npc_behavior import NPCBehavior
from src.models.rule import Rule, RULE_TEMPLATES
from src.utils.logger import get_logger
from src.utils.config import config as global_config

logger = get_logger(__name__)


class CLIGame:
    """命令行游戏界面"""
    
    def __init__(self):
        # 检查AI配置
        ai_config = global_config.get("ai_enabled", False)
        self.game_manager = GameStateManager(config={"ai_enabled": ai_config})
        self.rule_executor = None
        self.npc_behavior = None
        self.running = True
        self.ai_enabled = ai_config
        
    def clear_screen(self):
        """清屏"""
        # 在测试环境中不清屏
        if os.environ.get('PYTEST_RUNNING'):
            return
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """打印游戏头部"""
        print("=" * 60)
        print("🎭 规则怪谈管理者 - Rules of Horror Manager 🎭".center(60))
        print("=" * 60)
        if self.ai_enabled:
            print("🤖 AI模式已启用".center(60))
        
    def print_game_status(self):
        """打印游戏状态"""
        if not self.game_manager.state:
            return
            
        state = self.game_manager.state
        print("\n📊 游戏状态")
        print(f"├─ 回合: {state.current_turn} | 第{state.day}天 {state.current_time}")
        print(f"├─ 阶段: {state.phase.value}")
        print(f"├─ 模式: {'幕后管理' if state.mode == GameMode.BACKSTAGE else '亲自下场'}")
        print(f"├─ 恐惧积分: {state.fear_points} 💀")
        print(f"├─ 活跃规则: {len(state.active_rules)}")
        print(f"└─ 存活NPC: {len(self.game_manager.get_alive_npcs())}/{len(state.npcs)}")
        
    def print_npcs(self):
        """打印NPC状态"""
        print("\n👥 NPC状态:")
        print("-" * 60)
        print(f"{'名字':^8} {'位置':^12} {'HP':^6} {'理智':^6} {'恐惧':^6} {'状态':^8}")
        print("-" * 60)
        
        for npc in self.game_manager.state.npcs.values():
            status = "存活" if npc.get("alive", True) else "死亡"
            print(f"{npc['name']:^8} {npc['location']:^12} "
                  f"{npc['hp']:^6} {npc['sanity']:^6} {npc['fear']:^6} {status:^8}")
                  
    def print_rules(self):
        """打印规则列表"""
        if not self.game_manager.rules:
            print("\n📜 当前没有激活的规则")
            return
            
        print("\n📜 激活的规则:")
        for i, rule in enumerate(self.game_manager.rules, 1):
            print(f"{i}. {rule.name} (等级{rule.level}) - {(rule.description or '')[:30]}...")
            
    def print_recent_events(self, limit=5):
        """打印最近的事件"""
        events = self.game_manager.state.event_log[-limit:]
        if not events:
            return
            
        print("\n📋 最近事件:")
        for event in events:
            if hasattr(event, "to_dict"):
                event = event.to_dict()
            elif not isinstance(event, dict):
                event = {"description": str(event)}

            time = event.get("game_time", "")
            type_ = event.get("type", "unknown")
            
            if type_ == "rule_triggered":
                print(f"  [{time}] ⚡ {event.get('actor')} 触发了 {event.get('rule_name')}")
            elif type_ == "fear_gained":
                print(f"  [{time}] 💀 获得 {event.get('amount')} 恐惧积分")
            elif type_ == "rule_created":
                print(f"  [{time}] ✨ 创建规则 {event.get('rule_name')}")
            else:
                print(f"  [{time}] 📌 {type_}")
                
    async def main_menu(self):
        """主菜单"""
        self.clear_screen()
        self.print_header()
        
        print("\n🎮 主菜单")
        print("1. 新游戏")
        print("2. 加载游戏")
        print("3. 退出")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            await self.new_game()
        elif choice == "2":
            await self.load_game_menu()
        elif choice == "3":
            self.running = False
        else:
            print("无效选择！")
            await asyncio.sleep(1)
            
    async def new_game(self):
        """开始新游戏"""
        self.clear_screen()
        print("🎮 创建新游戏\n")
        
        # 可以让玩家自定义设置
        config = {
            "initial_fear_points": 1000,
            "starting_npcs": 4,
            "difficulty": "normal"
        }
        
        # 询问AI启用
        ai_choice = input("\n启用AI功能？(y/n): ").strip().lower()
        self.ai_enabled = ai_choice == 'y'
        self.game_manager.ai_enabled = self.ai_enabled
        
        print("\n使用默认设置:")
        print(f"- 初始恐惧积分: {config['initial_fear_points']}")
        print(f"- NPC数量: {config['starting_npcs']}")
        print(f"- 难度: {config['difficulty']}")
        print(f"- AI模式: {'启用' if self.ai_enabled else '关闭'}")
        
        confirm = input("\n确认开始? (y/n): ").strip().lower()
        if confirm != 'y':
            return
            
        # 创建游戏
        self.game_manager.new_game(config=config)
        self.rule_executor = RuleExecutor(self.game_manager)
        self.npc_behavior = NPCBehavior(self.game_manager)
        
        # 初始化AI管线
        if self.ai_enabled:
            print("\n🤖 初始化AI系统...")
            success = await self.game_manager.init_ai_pipeline()
            if success:
                print("✅ AI系统就绪！")
            else:
                print("⚠️  AI初始化失败，使用本地模式")
                self.ai_enabled = False
        
        print("\n✅ 游戏创建成功！")
        await asyncio.sleep(1)
        
        # 显示初始NPC
        print(f"\n已创建 {len(self.game_manager.state.npcs)} 个NPC")
        
        # 进入游戏循环
        await self.game_loop()
        
    async def game_loop(self):
        """游戏主循环"""
        while self.running and self.game_manager.state:
            self.clear_screen()
            self.print_header()
            self.print_game_status()
            self.print_recent_events()
            
            # 检查游戏结束条件
            if len(self.game_manager.get_alive_npcs()) == 0:
                await self.game_over("所有NPC都已死亡！")
                break
                
            # 根据阶段显示不同菜单
            if self.game_manager.state.phase == GamePhase.SETUP:
                await self.setup_phase()
            elif self.game_manager.state.phase in [GamePhase.MORNING_DIALOGUE, GamePhase.EVENING_DIALOGUE]:
                await self.dialogue_phase()
            elif self.game_manager.state.phase == GamePhase.ACTION:
                await self.action_phase()
            elif self.game_manager.state.phase == GamePhase.RESOLUTION:
                await self.resolution_phase()
                
    async def setup_phase(self):
        """准备阶段"""
        print("\n⚙️  准备阶段")
        print("1. 创建/管理规则")
        print("2. 查看NPC状态")
        print("3. 切换控制模式")
        print("4. 开始回合")
        if self.ai_enabled:
            print("5. AI模式回合")
            print("6. 保存游戏")
            print("7. 返回主菜单")
        else:
            print("5. 保存游戏")
            print("6. 返回主菜单")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            await self.manage_rules()
        elif choice == "2":
            self.print_npcs()
            _pause()
        elif choice == "3":
            await self.switch_mode()
        elif choice == "4":
            self.game_manager.change_phase(GamePhase.ACTION)
            self.game_manager.advance_turn()
        elif choice == "5" and self.ai_enabled:
            await self.ai_turn_phase()
        elif choice == "5" and not self.ai_enabled:
            self.save_game()
        elif choice == "6" and self.ai_enabled:
            self.save_game()
        elif (choice == "6" and not self.ai_enabled) or (choice == "7" and self.ai_enabled):
            self.running = False
            
    async def manage_rules(self):
        """管理规则"""
        self.clear_screen()
        print("📜 规则管理\n")
        
        self.print_rules()
        
        print("\n1. 创建新规则")
        print("2. 使用模板创建")
        if self.ai_enabled:
            print("3. 🤖 AI解析规则")
            print("4. 升级规则")
            print("5. 返回")
        else:
            print("3. 升级规则")
            print("4. 返回")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            await self.create_custom_rule()
        elif choice == "2":
            await self.create_rule_from_template()
        elif choice == "3" and self.ai_enabled:
            await self.create_rule_with_ai()
        elif (choice == "3" and not self.ai_enabled) or (choice == "4" and self.ai_enabled):
            print("升级功能尚未实现")
            await asyncio.sleep(1)
            
    async def create_custom_rule(self):
        """创建自定义规则"""
        try:
            from src.custom_rule_creator import create_custom_rule_enhanced
            
            rule = await create_custom_rule_enhanced()
            if rule:
                # 检查积分
                cost = rule.calculate_total_cost()
                if self.game_manager.state.fear_points >= cost:
                    confirm = input(f"\n确认花费 {cost} 恐惧积分创建此规则? (y/n): ").strip().lower()
                    if confirm == 'y':
                        if self.game_manager.add_rule(rule):
                            self.game_manager.spend_fear_points(cost)
                            print("✅ 规则创建成功！")
                        else:
                            print("❌ 规则创建失败！")
                else:
                    print(f"❌ 恐惧积分不足！需要 {cost}，当前只有 {self.game_manager.state.fear_points}")
            
            await asyncio.sleep(2)
        except ImportError:
            # 如果没有自定义规则创建器，使用原来的提示
            print("\n🔧 自定义规则创建")
            print("（此功能需要详细的规则参数输入界面）")
            print("\n当前版本请使用模板创建规则")
            await asyncio.sleep(3)
        
    async def create_rule_from_template(self):
        """从模板创建规则"""
        print("\n可用模板:")
        templates = list(RULE_TEMPLATES.items())
        for i, (key, template) in enumerate(templates, 1):
            print(f"{i}. {template['name']} - 成本: {template['base_cost']}")
            print(f"   {template['description']}")
            
        choice = input("\n选择模板 (输入编号): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(templates):
                template_key, template = templates[idx]
                
                # 创建规则
                rule = Rule(
                    id=f"rule_{len(self.game_manager.rules) + 1:03d}",
                    **template
                )
                
                # 显示成本
                cost = rule.calculate_total_cost()
                print(f"\n规则 '{rule.name}' 需要 {cost} 恐惧积分")
                print(f"当前积分: {self.game_manager.state.fear_points}")
                
                if self.game_manager.state.fear_points >= cost:
                    confirm = input("确认创建? (y/n): ").strip().lower()
                    if confirm == 'y':
                        if self.game_manager.add_rule(rule):
                            # 扣除恐惧积分
                            self.game_manager.spend_fear_points(cost)
                            print("✅ 规则创建成功！")
                        else:
                            print("❌ 规则创建失败！")
                else:
                    print("❌ 恐惧积分不足！")
                    
                await asyncio.sleep(2)
            else:
                print("无效选择！")
                await asyncio.sleep(1)
            
        except (ValueError, IndexError):
            print("无效选择！")
            await asyncio.sleep(1)
            
    async def create_rule_with_ai(self):
        """使用AI创建规则"""
        print("\n🤖 AI规则解析")
        print("请用自然语言描述你想要的规则：")
        print("例如：'晚上10点后不能开灯，否则会吸引怪物'")
        
        rule_description = input("\n规则描述: ").strip()
        if not rule_description:
            return
            
        print("\n🤖 AI正在解析规则...")
        try:
            result = await self.game_manager.evaluate_rule_nl(rule_description)
            
            if "error" in result:
                print(f"❌ 解析失败: {result['error']}")
                print(f"💡 建议: {result.get('suggestion', '请尝试更清晰地描述规则')}")
                await asyncio.sleep(3)
                return
                
            # 显示解析结果
            print("\n📊 解析结果:")
            print(f"规则名称: {result['name']}")
            print(f"预估成本: {result['cost']} 恐惧积分")
            print(f"难度等级: {result['difficulty']}/10")
            print(f"预计恐惧收益: {result.get('estimated_fear_gain', '未知')}")
            
            if result['loopholes']:
                print("\n⚠️ 潜在漏洞:")
                for loophole in result['loopholes']:
                    print(f"  - {loophole}")
                    
            print(f"\n💡 改进建议: {result['suggestion']}")
            
            # 询问是否创建
            if self.game_manager.state.fear_points >= result['cost']:
                confirm = input("\n确认创建此规则? (y/n): ").strip().lower()
                if confirm == 'y':
                    # TODO: 实现规则创建逻辑
                    print("✅ 规则创建功能即将实现！")
            else:
                print(f"\n❌ 恐惧积分不足！需要 {result['cost']}，当前只有 {self.game_manager.state.fear_points}")
                
        except Exception as e:
            print(f"❌ AI解析失败: {e}")
            
        await asyncio.sleep(3)
            
    async def ai_turn_phase(self):
        """AI驱动的回合"""
        print("\n🤖 AI回合模式")
        print("AI将生成NPC对话和行动计划")
        
        confirm = input("\n开始AI回合? (y/n): ").strip().lower()
        if confirm != 'y':
            return
            
        try:
            # 执行AI回合
            print("\n🤖 AI正在生成回合内容...")
            plan = await self.game_manager.run_ai_turn()
            
            if plan:
                # 显示对话
                if plan.dialogue:
                    print("\n【NPC对话】")
                    for d in plan.dialogue:
                        print(f"{d.speaker}: {d.text}")
                        if d.emotion:
                            print(f"  (情绪: {d.emotion})")
                    
                # 显示行动计划
                if plan.actions:
                    print("\n【行动计划】")
                    for a in plan.actions:
                        action_desc = f"{a.npc} → {a.action}"
                        if a.target:
                            action_desc += f" {a.target}"
                        if a.reason:
                            action_desc += f" ({a.reason})"
                        print(f"- {action_desc}")
                        
                # 询问是否执行
                execute = input("\n执行这些行动? (y/n): ").strip().lower()
                if execute == 'y':
                    # 执行行动会在AI管线中完成
                    print("✅ 行动已执行")
                    
                    # 进入结算阶段
                    self.game_manager.change_phase(GamePhase.RESOLUTION)
                    await self.resolution_phase()
            else:
                print("⚠️ AI回合生成失败")
                
        except Exception as e:
            print(f"❌ AI回合出错: {e}")
            
        await asyncio.sleep(2)
            
    async def action_phase(self):
        """行动阶段"""
        print("\n🎬 行动阶段")
        
        # NPC自动行动
        print("\nNPC行动中...")
        
        for npc_id, npc in self.game_manager.state.npcs.items():
            if not npc.get("alive", True):
                continue
                
            # 决定行动
            decision = self.npc_behavior.decide_action(npc)
            
            # 执行行动
            result = self.npc_behavior.execute_action(npc, decision)
            
            # 显示行动
            for msg in result["messages"]:
                print(f"  {msg}")
                
            # 创建规则上下文
            context = RuleContext(
                actor=npc,
                action=decision.action.value,
                game_state=self.game_manager.state.to_dict()
            )
            
            # 检查是否触发规则
            triggered_rules = self.rule_executor.check_all_rules(context)
            
            for rule, probability in triggered_rules:
                import random
                if random.random() < probability:
                    print(f"\n⚡ {npc['name']} 触发了规则 [{rule.name}]!")
                    exec_result = self.rule_executor.execute_rule(rule, context)
                    
                    for msg in exec_result.get("messages", []) or []:
                        print(f"   {msg}")
                        
            await asyncio.sleep(0.5)  # 短暂延迟，让玩家能看清
            
        print("\n行动阶段结束")
        input("按回车继续...")
        
        # 进入结算阶段
        self.game_manager.change_phase(GamePhase.RESOLUTION)
        
    async def resolution_phase(self):
        """结算阶段"""
        print("\n📊 回合结算")
        
        # 更新规则冷却
        self.rule_executor.update_cooldowns()
        
        # 显示统计
        stats = self.rule_executor.get_execution_stats()
        print("\n本回合统计:")
        print(f"- 规则触发次数: {stats['total_executions']}")
        print(f"- 存活NPC: {len(self.game_manager.get_alive_npcs())}")
        print(f"- 当前恐惧积分: {self.game_manager.state.fear_points}")
        
        # AI叙事生成
        if self.ai_enabled and self.game_manager.ai_pipeline:
            choice = input("\n生成本回合叙事？(y/n): ").strip().lower()
            if choice == 'y':
                print("\n📖 生成叙事中...")
                try:
                    narrative = await self.game_manager.generate_narrative()
                    print("\n【回合叙事】")
                    print("-" * 60)
                    print(narrative)
                    print("-" * 60)
                except Exception as e:
                    print(f"⚠️ 叙事生成失败: {e}")
        
        input("\n按回车进入下一回合...")
        
        # 回到准备阶段
        self.game_manager.change_phase(GamePhase.SETUP)
        
    async def dialogue_phase(self):
        """对话阶段"""
        print("\n💬 对话阶段")
        
        if self.ai_enabled and self.game_manager.ai_pipeline:
            # 使用AI生成对话
            print("🤖 AI正在生成对话...")
            try:
                plan = await self.game_manager.run_ai_turn(force_dialogue=True)
                if plan and plan.dialogue:
                    print("\n[对话内容]")
                    for d in plan.dialogue:
                        print(f"  {d.speaker}: {d.text}")
                        if d.emotion:
                            print(f"    (情绪: {d.emotion})")
                        await asyncio.sleep(1.5)
                else:
                    print("⚠️ AI未生成对话")
            except Exception as e:
                print(f"⚠️ AI对话生成失败: {e}")
                await self._fallback_dialogue()
        else:
            # 退化到简单对话
            await self._fallback_dialogue()
                
        _pause()
        # 进入下一个阶段
        self.game_manager.change_phase(GamePhase.ACTION)
    
    async def _fallback_dialogue(self):
        """备用对话生成"""
        npcs = self.game_manager.get_alive_npcs()
        if len(npcs) >= 2:
            import random
            npc1, npc2 = random.sample(npcs, 2)
            
            dialogues = [
                f"{npc1['name']}: 这地方感觉不太对劲...",
                f"{npc2['name']}: 是啊，我也有这种感觉。",
                f"{npc1['name']}: 我们应该小心一点。",
            ]
            
            for dialogue in dialogues:
                print(f"  {dialogue}")
                await asyncio.sleep(1)
        
    async def switch_mode(self):
        """切换控制模式"""
        current = self.game_manager.state.mode
        new_mode = GameMode.IN_SCENE if current == GameMode.BACKSTAGE else GameMode.BACKSTAGE
        
        self.game_manager.state.mode = new_mode
        print(f"\n已切换到: {'亲自下场' if new_mode == GameMode.IN_SCENE else '幕后管理'} 模式")
        await asyncio.sleep(1)
        
    def save_game(self):
        """保存游戏"""
        save_name = input("输入存档名称: ").strip()
        if save_name:
            try:
                path = self.game_manager.save_game(save_name)
                if path:
                    print(f"✅ 游戏已保存到: {path}")
                else:
                    print("❌ 保存游戏失败")
            except Exception as e:
                print(f"❌ 保存失败: {e}")
        else:
            print("❌ 存档名称不能为空")
        _pause()
        
    async def load_game_menu(self):
        """加载游戏菜单"""
        from pathlib import Path
        
        self.clear_screen()
        print("📂 加载游戏\n")
        
        # 使用data/saves作为存档目录
        save_dir = self.game_manager.save_dir
        if not save_dir.exists():
            print("没有找到任何存档")
            await asyncio.sleep(2)
            return
            
        saves = list(save_dir.glob("*.json"))
        if not saves:
            print("没有找到任何存档")
            await asyncio.sleep(2)
            return
            
        print("可用存档:")
        for i, save_file in enumerate(saves, 1):
            print(f"{i}. {save_file.stem}")
            
        choice = input("\n选择存档编号 (0取消): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(saves):
                game_id = saves[idx].stem
                if self.game_manager.load_game(game_id):
                    print("✅ 游戏加载成功！")
                    self.rule_executor = RuleExecutor(self.game_manager)
                    self.npc_behavior = NPCBehavior(self.game_manager)
                    
                    # 如果存档启用了AI，尝试初始化
                    if self.game_manager.ai_enabled:
                        print("🤖 初始化AI系统...")
                        success = await self.game_manager.init_ai_pipeline()
                        if success:
                            print("✅ AI系统就绪！")
                            self.ai_enabled = True
                        else:
                            print("⚠️ AI初始化失败")
                            self.ai_enabled = False
                    
                    await asyncio.sleep(1)
                    await self.game_loop()
                else:
                    print("❌ 加载失败：存档可能已损坏")
                    await asyncio.sleep(2)
            elif choice == "0":
                return
            else:
                print("无效选择")
                await asyncio.sleep(1)
        except ValueError:
            if choice != "0":
                print("请输入数字")
                await asyncio.sleep(1)
        
    async def game_over(self, reason: str):
        """游戏结束"""
        self.clear_screen()
        print("\n" + "="*60)
        print("💀 游戏结束 💀".center(60))
        print("="*60)
        print(f"\n结束原因: {reason}")
        
        summary = self.game_manager.get_summary()
        print("\n游戏统计:")
        print(f"- 总回合数: {summary['turns_played']}")
        print(f"- 存活天数: {self.game_manager.state.day}")
        print(f"- 最终恐惧积分: {summary['fear_points_final']}")
        print(f"- 创建规则数: {summary['rules_created']}")
        
        # 关闭AI客户端
        if self.ai_enabled and self.game_manager.ai_pipeline:
            await self.game_manager.close_ai()
        
        input("\n按回车返回主菜单...")
        
    async def run(self):
        """运行游戏"""
        try:
            while self.running:
                await self.main_menu()
        except KeyboardInterrupt:
            print("\n\n👋 感谢游玩！")
        except Exception as e:
            logger.error(f"游戏出错: {e}", exc_info=True)
            print(f"\n❌ 游戏出错: {e}")
        finally:
            # 确保关闭AI客户端
            if hasattr(self, 'game_manager') and self.game_manager.ai_pipeline:
                await self.game_manager.close_ai()


async def main():
    """主函数"""
    game = CLIGame()
    await game.run()


if __name__ == "__main__":
    # 运行游戏
    asyncio.run(main())
