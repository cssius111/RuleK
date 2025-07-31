"""
CLI测试配置和fixtures
"""
import pytest
import asyncio
from pathlib import Path
import shutil
from src.cli_game import CLIGame
from src.core.rule_executor import RuleExecutor
from src.core.npc_behavior import NPCBehavior


@pytest.fixture
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_save_dir(tmp_path):
    """创建临时存档目录"""
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    
    # 设置环境变量或配置
    original_dir = Path("data/saves")
    
    # 备份原目录
    if original_dir.exists():
        backup_dir = tmp_path / "saves_backup"
        shutil.copytree(original_dir, backup_dir)
    
    yield save_dir
    
    # 恢复原目录
    if (tmp_path / "saves_backup").exists():
        if original_dir.exists():
            shutil.rmtree(original_dir)
        shutil.copytree(tmp_path / "saves_backup", original_dir)


@pytest.fixture
def mock_input_sequence(monkeypatch):
    """创建可配置的输入序列"""
    class InputSequence:
        def __init__(self):
            self.inputs = []
            self.index = 0
        
        def add(self, *inputs):
            self.inputs.extend(inputs)
        
        def __call__(self, prompt=""):
            if self.index < len(self.inputs):
                value = self.inputs[self.index]
                self.index += 1
                return value
            return ""
    
    sequence = InputSequence()
    monkeypatch.setattr("builtins.input", sequence)
    return sequence


@pytest.fixture
def cli_game():
    """创建CLI游戏实例，测试模式下运行"""
    game = CLIGame()
    game.clear_screen = lambda: None
    return game


@pytest.fixture
def initialized_game(cli_game):
    """创建已初始化的游戏实例"""
    cli_game.game_manager.new_game("test_game")
    cli_game.rule_executor = RuleExecutor(cli_game.game_manager)
    cli_game.npc_behavior = NPCBehavior(cli_game.game_manager)
    return cli_game


# 确保测试时不清屏
import os
os.environ['PYTEST_RUNNING'] = '1'
