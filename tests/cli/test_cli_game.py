"""
CLI游戏界面完整测试套件
"""
import pytest
import asyncio
from pathlib import Path
import json
import os
from unittest.mock import patch, MagicMock, AsyncMock, call

from src.cli_game import CLIGame
from src.core.enums import GamePhase, GameMode
from src.core.game_state import GameStateManager
from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType, RULE_TEMPLATES


@pytest.fixture
def cli_game():
    """创建CLI游戏实例"""
    game = CLIGame()
    # 禁用清屏
    game.clear_screen = lambda: None
    return game


@pytest.fixture
def initialized_game(cli_game):
    """创建已初始化的游戏"""
    cli_game.game_manager.new_game("test_game")
    from src.core.rule_executor import RuleExecutor
    from src.core.npc_behavior import NPCBehavior
    cli_game.rule_executor = RuleExecutor(cli_game.game_manager)
    cli_game.npc_behavior = NPCBehavior(cli_game.game_manager)
    return cli_game


class TestMainMenu:
    """主菜单测试"""
    
    @pytest.mark.asyncio
    async def test_new_game_creation_success(self, cli_game, mock_input_sequence):
        """测试成功创建新游戏 - 验证游戏状态正确初始化"""
        mock_input_sequence.add("y", "6")  # 确认创建，然后返回主菜单
        
        with patch.object(cli_game, "game_loop", new_callable=AsyncMock) as mock_loop:
            await cli_game.new_game()
            
        assert cli_game.game_manager.state is not None
        assert cli_game.game_manager.state.fear_points == 1000
        assert len(cli_game.game_manager.state.npcs) > 0
        assert cli_game.rule_executor is not None
        assert cli_game.npc_behavior is not None
        mock_loop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_new_game_cancel(self, cli_game, mock_input_sequence):
        """测试取消创建新游戏 - 验证状态保持未初始化"""
        mock_input_sequence.add("n")
        
        await cli_game.new_game()
        
        assert cli_game.game_manager.state is None
        assert cli_game.rule_executor is None
    
    @pytest.mark.asyncio
    async def test_main_menu_exit(self, cli_game, mock_input_sequence):
        """测试主菜单退出选项 - 验证程序正常退出"""
        mock_input_sequence.add("3")
        
        await cli_game.main_menu()
        
        assert cli_game.running is False
    
    @pytest.mark.asyncio
    async def test_main_menu_invalid_choice(self, cli_game, mock_input_sequence):
        """测试主菜单无效选择 - 验证错误处理"""
        mock_input_sequence.add("999", "3")  # 无效选择，然后退出
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await cli_game.main_menu()
            # 第二次调用应该退出
            await cli_game.main_menu()
        
        assert cli_game.running is False


class TestGameStateDisplay:
    """游戏状态显示测试"""
    
    def test_print_game_status_full(self, initialized_game, capsys):
        """测试完整游戏状态显示 - 验证所有信息正确显示"""
        initialized_game.print_game_status()
        
        captured = capsys.readouterr()
        assert "游戏状态" in captured.out
        assert "回合: 0" in captured.out
        assert "第1天" in captured.out
        assert "恐惧积分: 1000" in captured.out
        assert "阶段: setup" in captured.out
        assert "模式: 幕后管理" in captured.out
    
    def test_print_game_status_no_state(self, cli_game, capsys):
        """测试无游戏状态时的显示 - 验证不输出任何内容"""
        cli_game.print_game_status()
        
        captured = capsys.readouterr()
        assert captured.out == ""
    
    def test_print_npcs_with_data(self, initialized_game, capsys):
        """测试NPC列表显示 - 验证NPC信息正确格式化"""
        initialized_game.print_npcs()
        
        captured = capsys.readouterr()
        assert "NPC状态" in captured.out
        assert "名字" in captured.out
        assert "HP" in captured.out
        assert "理智" in captured.out
        assert "恐惧" in captured.out
    
    def test_print_rules_empty(self, initialized_game, capsys):
        """测试空规则列表显示 - 验证正确提示无规则"""
        initialized_game.print_rules()
        
        captured = capsys.readouterr()
        assert "当前没有激活的规则" in captured.out
    
    def test_print_rules_with_data(self, initialized_game, capsys):
        """测试规则列表显示 - 验证规则信息正确格式化"""
        # 添加一个测试规则
        rule = Rule(
            id="test_rule",
            name="测试规则",
            description="这是一个测试规则的描述",
            level=1,
            trigger=TriggerCondition(action="test"),
            effect=RuleEffect(type=EffectType.FEAR_GAIN)
        )
        initialized_game.game_manager.add_rule(rule)
        
        initialized_game.print_rules()
        
        captured = capsys.readouterr()
        assert "激活的规则" in captured.out
        assert "测试规则" in captured.out
        assert "等级1" in captured.out
    
    def test_print_recent_events(self, initialized_game, capsys):
        """测试最近事件显示 - 验证事件正确格式化"""
        # 添加测试事件
        initialized_game.game_manager.state.event_log.append({
            "game_time": "00:00",
            "type": "rule_triggered",
            "actor": "测试NPC",
            "rule_name": "测试规则"
        })
        
        initialized_game.print_recent_events()
        
        captured = capsys.readouterr()
        assert "最近事件" in captured.out
        assert "触发了" in captured.out


class TestSetupPhase:
    """准备阶段测试"""
    
    @pytest.mark.asyncio
    async def test_setup_phase_view_npcs(self, initialized_game, mock_input_sequence):
        """测试查看NPC状态选项 - 验证正确显示NPC信息"""
        mock_input_sequence.add("2", "")  # 查看NPC，按回车继续
        
        with patch.object(initialized_game, 'game_loop', new_callable=AsyncMock):
            await initialized_game.setup_phase()
    
    @pytest.mark.asyncio
    async def test_setup_phase_switch_mode(self, initialized_game, mock_input_sequence):
        """测试切换控制模式 - 验证模式正确切换"""
        mock_input_sequence.add("3")  # 切换模式
        original_mode = initialized_game.game_manager.state.mode
        
        with patch.object(initialized_game, 'game_loop', new_callable=AsyncMock):
            await initialized_game.setup_phase()
        
        assert initialized_game.game_manager.state.mode != original_mode
    
    @pytest.mark.asyncio
    async def test_setup_phase_start_turn(self, initialized_game, mock_input_sequence):
        """测试开始回合 - 验证阶段切换和回合推进"""
        mock_input_sequence.add("4")  # 开始回合
        
        with patch.object(initialized_game, 'game_loop', new_callable=AsyncMock):
            await initialized_game.setup_phase()
        
        assert initialized_game.game_manager.state.phase == GamePhase.ACTION
        assert initialized_game.game_manager.state.current_turn == 1
    
    @pytest.mark.asyncio
    async def test_setup_phase_save_game(self, initialized_game, mock_input_sequence, temp_save_dir):
        """测试保存游戏 - 验证存档文件正确创建"""
        initialized_game.game_manager.save_dir = temp_save_dir
        mock_input_sequence.add("5", "test_save", "")  # 保存游戏
        
        with patch.object(initialized_game, 'game_loop', new_callable=AsyncMock):
            await initialized_game.setup_phase()
        
        save_file = temp_save_dir / "test_save.json"
        assert save_file.exists()
    
    @pytest.mark.asyncio
    async def test_setup_phase_return_menu(self, initialized_game, mock_input_sequence):
        """测试返回主菜单 - 验证退出游戏循环"""
        mock_input_sequence.add("6")  # 返回主菜单
        
        await initialized_game.setup_phase()
        
        assert initialized_game.running is False


class TestRuleManagement:
    """规则管理测试"""
    
    @pytest.mark.asyncio
    async def test_create_custom_rule_placeholder(self, initialized_game, mock_input_sequence, capsys):
        """测试自定义规则创建占位功能 - 验证显示提示信息"""
        mock_input_sequence.add("1")  # 选择自定义规则
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await initialized_game.manage_rules()
        
        captured = capsys.readouterr()
        assert "自定义规则创建" in captured.out
        assert "当前版本请使用模板创建规则" in captured.out
    
    @pytest.mark.asyncio
    async def test_create_rule_from_template_success(self, initialized_game, mock_input_sequence):
        """测试从模板成功创建规则 - 验证规则添加和积分扣除"""
        initial_points = initialized_game.game_manager.state.fear_points
        mock_input_sequence.add("2", "1", "y")  # 使用模板，选择第一个，确认
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await initialized_game.manage_rules()
        
        assert len(initialized_game.game_manager.rules) == 1
        assert len(initialized_game.game_manager.state.active_rules) == 1
        assert initialized_game.game_manager.state.fear_points < initial_points
    
    @pytest.mark.asyncio
    async def test_create_rule_insufficient_points(self, initialized_game, mock_input_sequence, capsys):
        """测试积分不足时创建规则 - 验证拒绝创建并提示"""
        initialized_game.game_manager.state.fear_points = 10
        mock_input_sequence.add("2", "1")  # 使用模板，选择第一个
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await initialized_game.manage_rules()
        
        assert len(initialized_game.game_manager.rules) == 0
        captured = capsys.readouterr()
        assert "恐惧积分不足" in captured.out
    
    @pytest.mark.asyncio
    async def test_create_rule_invalid_template(self, initialized_game, mock_input_sequence, capsys):
        """测试选择无效模板 - 验证错误处理"""
        mock_input_sequence.add("2", "999")  # 无效索引
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await initialized_game.manage_rules()
        
        assert len(initialized_game.game_manager.rules) == 0
        captured = capsys.readouterr()
        assert "无效选择" in captured.out
    
    @pytest.mark.asyncio
    async def test_upgrade_rule_not_implemented(self, initialized_game, mock_input_sequence, capsys):
        """测试升级规则未实现功能 - 验证显示提示"""
        mock_input_sequence.add("3")  # 选择升级
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await initialized_game.manage_rules()
        
        captured = capsys.readouterr()
        assert "升级功能尚未实现" in captured.out


class TestActionPhase:
    """行动阶段测试"""
    
    @pytest.mark.asyncio
    async def test_action_phase_with_npcs(self, initialized_game, mock_input_sequence):
        """测试NPC行动阶段 - 验证NPC行动和规则触发"""
        mock_input_sequence.add("")  # 按回车继续
        
        # 添加一个规则
        rule = Rule(
            id="test_rule",
            name="测试规则",
            trigger=TriggerCondition(action="move", probability=1.0),
            effect=RuleEffect(type=EffectType.FEAR_GAIN, fear_gain=10)
        )
        initialized_game.game_manager.add_rule(rule)
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await initialized_game.action_phase()
        
        assert initialized_game.game_manager.state.phase == GamePhase.RESOLUTION
    
    @pytest.mark.asyncio
    async def test_action_phase_no_alive_npcs(self, initialized_game, mock_input_sequence):
        """测试无存活NPC时的行动阶段 - 验证跳过NPC行动"""
        # 杀死所有NPC
        for npc_id, npc in initialized_game.game_manager.state.npcs.items():
            npc['alive'] = False
            npc['hp'] = 0
        
        mock_input_sequence.add("")
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await initialized_game.action_phase()
        
        assert initialized_game.game_manager.state.phase == GamePhase.RESOLUTION
    
    @pytest.mark.asyncio
    async def test_action_phase_rule_trigger(self, initialized_game, mock_input_sequence, capsys):
        """测试规则触发 - 验证规则执行和消息显示"""
        mock_input_sequence.add("")
        
        # Mock规则执行器返回触发的规则
        mock_rule = MagicMock()
        mock_rule.name = "测试触发规则"
        initialized_game.rule_executor.check_all_rules = MagicMock(return_value=[(mock_rule, 1.0)])
        initialized_game.rule_executor.execute_rule = MagicMock(return_value={
            "messages": ["规则效果已应用"]
        })
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch('random.random', return_value=0.5):  # 确保触发
                await initialized_game.action_phase()
        
        captured = capsys.readouterr()
        assert "触发了规则" in captured.out
        assert "测试触发规则" in captured.out


class TestResolutionPhase:
    """结算阶段测试"""
    
    @pytest.mark.asyncio
    async def test_resolution_phase(self, initialized_game, mock_input_sequence, capsys):
        """测试回合结算 - 验证统计显示和阶段切换"""
        mock_input_sequence.add("")  # 按回车继续
        
        # Mock执行统计
        initialized_game.rule_executor.get_execution_stats = MagicMock(return_value={
            'total_executions': 5
        })
        
        await initialized_game.resolution_phase()
        
        captured = capsys.readouterr()
        assert "回合结算" in captured.out
        assert "规则触发次数: 5" in captured.out
        assert initialized_game.game_manager.state.phase == GamePhase.SETUP


class TestDialoguePhase:
    """对话阶段测试"""
    
    @pytest.mark.asyncio
    async def test_dialogue_phase_with_npcs(self, initialized_game, mock_input_sequence, capsys):
        """测试有足够NPC时的对话 - 验证生成模拟对话"""
        mock_input_sequence.add("")
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch('random.sample') as mock_sample:
                # 确保有足够的NPC
                npcs = list(initialized_game.game_manager.get_alive_npcs())
                if len(npcs) >= 2:
                    mock_sample.return_value = npcs[:2]
                    await initialized_game.dialogue_phase()
        
        captured = capsys.readouterr()
        assert "对话阶段" in captured.out
        
        if len(npcs) >= 2:
            assert "这地方感觉不太对劲" in captured.out
    
    @pytest.mark.asyncio
    async def test_dialogue_phase_insufficient_npcs(self, initialized_game, mock_input_sequence):
        """测试NPC不足时的对话 - 验证跳过对话生成"""
        # 只保留一个NPC
        npc_ids = list(initialized_game.game_manager.state.npcs.keys())
        for npc_id in npc_ids[1:]:
            initialized_game.game_manager.state.npcs[npc_id]['alive'] = False
        
        mock_input_sequence.add("")
        
        await initialized_game.dialogue_phase()
        
        assert initialized_game.game_manager.state.phase == GamePhase.ACTION


class TestSaveLoad:
    """存档和加载测试"""
    
    def test_save_game_success(self, initialized_game, mock_input_sequence, temp_save_dir):
        """测试成功保存游戏 - 验证文件创建和内容"""
        initialized_game.game_manager.save_dir = temp_save_dir
        mock_input_sequence.add("test_save", "")
        
        initialized_game.save_game()
        
        save_file = temp_save_dir / "test_save.json"
        assert save_file.exists()
        
        # 验证存档内容
        with open(save_file) as f:
            data = json.load(f)
            assert data['state']['game_id'] == 'test_game'
            assert data['state']['fear_points'] == 1000
    
    def test_save_game_empty_name(self, initialized_game, mock_input_sequence, capsys):
        """测试空存档名 - 验证错误提示"""
        mock_input_sequence.add("", "")
        
        initialized_game.save_game()
        
        captured = capsys.readouterr()
        assert "存档名称不能为空" in captured.out
    
    @pytest.mark.asyncio
    async def test_load_game_success(self, cli_game, mock_input_sequence, temp_save_dir):
        """测试成功加载游戏 - 验证状态恢复"""
        # 创建测试存档
        save_data = {
            "state": {
                "game_id": "loaded_game",
                "started_at": "2024-01-01T00:00:00",
                "current_turn": 10,
                "fear_points": 500,
                "phase": "setup",
                "time_of_day": "evening",
                "mode": "backstage",
                "total_fear_gained": 500,
                "npcs_died": 2,
                "rules_triggered": 15,
                "difficulty": "hard",
                "day": 3,
                "npcs": {},
                "active_rules": ["rule_001"],
                "events_history": []
            },
            "rules": [],
            "npcs": [],
            "spirits": [],
            "game_log": ["游戏开始"]
        }
        
        save_file = temp_save_dir / "loaded_game.json"
        with open(save_file, "w") as f:
            json.dump(save_data, f)
        
        cli_game.game_manager.save_dir = temp_save_dir
        mock_input_sequence.add("1", "6")  # 选择第一个存档，然后退出
        
        with patch.object(cli_game, 'game_loop', new_callable=AsyncMock):
            await cli_game.load_game_menu()
        
        assert cli_game.game_manager.state is not None
        assert cli_game.game_manager.state.current_turn == 10
        assert cli_game.game_manager.state.fear_points == 500
        assert cli_game.game_manager.state.day == 3
    
    @pytest.mark.asyncio
    async def test_load_game_no_saves(self, cli_game, capsys):
        """测试无存档时加载 - 验证提示信息"""
        # 不使用temp_save_dir，使用一个确实不存在的目录
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_dir = Path(temp_dir) / "empty_saves"
            cli_game.game_manager.save_dir = empty_dir
            
            with patch('asyncio.sleep', new_callable=AsyncMock):
                await cli_game.load_game_menu()
            
            captured = capsys.readouterr()
            assert "没有找到任何存档" in captured.out
    
    @pytest.mark.asyncio
    async def test_load_game_cancel(self, cli_game, mock_input_sequence, temp_save_dir):
        """测试取消加载 - 验证返回主菜单"""
        # 创建一个存档
        (temp_save_dir / "test.json").touch()
        cli_game.game_manager.save_dir = temp_save_dir
        
        mock_input_sequence.add("0")  # 取消
        
        await cli_game.load_game_menu()
        
        assert cli_game.game_manager.state is None


class TestGameOver:
    """游戏结束测试"""
    
    @pytest.mark.asyncio
    async def test_game_over_display(self, initialized_game, mock_input_sequence, capsys):
        """测试游戏结束显示 - 验证统计信息"""
        initialized_game.game_manager.state.current_turn = 20
        initialized_game.game_manager.state.day = 5
        mock_input_sequence.add("")
        
        await initialized_game.game_over("测试结束")
        
        captured = capsys.readouterr()
        assert "游戏结束" in captured.out
        assert "测试结束" in captured.out
        assert "总回合数: 20" in captured.out
        assert "存活天数: 5" in captured.out
    
    @pytest.mark.asyncio
    async def test_game_loop_all_npcs_dead(self, initialized_game, mock_input_sequence):
        """测试所有NPC死亡导致游戏结束 - 验证游戏循环退出"""
        # 杀死所有NPC
        for npc in initialized_game.game_manager.state.npcs.values():
            npc['alive'] = False
            npc['hp'] = 0
        
        initialized_game.game_manager.npcs = []
        
        mock_input_sequence.add("")  # game over时按回车
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await initialized_game.game_loop()
        
        # 游戏应该结束


class TestEdgeCasesAndErrors:
    """边界情况和错误处理测试"""
    
    def test_print_rules_with_no_description(self, initialized_game, capsys):
        """测试显示无描述的规则 - 验证不崩溃"""
        rule = Rule(
            id="no_desc_rule",
            name="无描述规则",
            description="",  # 空字符串而不是None
            trigger=TriggerCondition(action="test"),
            effect=RuleEffect(type=EffectType.FEAR_GAIN)
        )
        initialized_game.game_manager.add_rule(rule)
        
        initialized_game.print_rules()
        
        captured = capsys.readouterr()
        assert "无描述规则" in captured.out
        assert "..." in captured.out  # 应该显示省略号
    
    @pytest.mark.asyncio
    async def test_switch_mode_toggle(self, initialized_game):
        """测试模式切换来回切换 - 验证状态正确"""
        original = initialized_game.game_manager.state.mode
        
        await initialized_game.switch_mode()
        first_switch = initialized_game.game_manager.state.mode
        assert first_switch != original
        
        await initialized_game.switch_mode()
        assert initialized_game.game_manager.state.mode == original
    
    @pytest.mark.asyncio
    async def test_keyboard_interrupt_handling(self, cli_game, mock_input_sequence):
        """测试键盘中断处理 - 验证优雅退出"""
        mock_input_sequence.add("1")  # 尝试创建新游戏
        
        with patch.object(cli_game, 'main_menu', side_effect=KeyboardInterrupt):
            await cli_game.run()
        
        # 应该正常退出，不崩溃
    
    def test_save_game_exception_handling(self, initialized_game, mock_input_sequence, capsys):
        """测试保存游戏异常处理 - 验证错误提示"""
        mock_input_sequence.add("test_save", "")
        
        with patch.object(initialized_game.game_manager, 'save_game', side_effect=Exception("磁盘错误")):
            initialized_game.save_game()
        
        captured = capsys.readouterr()
        assert "保存失败" in captured.out
    
    @pytest.mark.asyncio
    async def test_load_corrupted_save(self, cli_game, mock_input_sequence, temp_save_dir, capsys):
        """测试加载损坏的存档 - 验证错误处理"""
        # 创建损坏的存档
        save_file = temp_save_dir / "corrupted.json"
        save_file.write_text("{ invalid json")
        
        cli_game.game_manager.save_dir = temp_save_dir
        mock_input_sequence.add("1")
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await cli_game.load_game_menu()
        
        captured = capsys.readouterr()
        assert "加载失败" in captured.out


class TestIntegration:
    """集成测试 - 测试完整流程"""
    
    @pytest.mark.asyncio
    async def test_complete_game_flow(self, cli_game, mock_input_sequence, temp_save_dir):
        """测试完整游戏流程 - 新建/规则/回合/保存/加载"""
        cli_game.game_manager.save_dir = temp_save_dir
        
        # 完整流程输入序列
        mock_input_sequence.add(
            "1",        # 主菜单 - 新游戏
            "y",        # 确认创建
            "1",        # 准备阶段 - 创建规则
            "2",        # 规则管理 - 使用模板
            "1",        # 选择第一个模板
            "y",        # 确认创建
            "4",        # 返回规则管理
            "4",        # 准备阶段 - 开始回合
            "",         # 行动阶段 - 按回车
            "",         # 结算阶段 - 按回车
            "5",        # 准备阶段 - 保存游戏
            "integration_test",  # 存档名
            "",         # 按回车继续
            "6"         # 返回主菜单
        )
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await cli_game.run()
        
        # 验证存档创建
        save_file = temp_save_dir / "integration_test.json"
        assert save_file.exists()
        
        # 验证游戏状态
        with open(save_file) as f:
            data = json.load(f)
            assert data['state']['current_turn'] == 1
            assert len(data['rules']) == 1
