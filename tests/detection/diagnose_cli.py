#!/usr/bin/env python3
"""快速诊断CLI测试问题"""
import sys
import os
from pathlib import Path

# 设置环境
os.environ['PYTEST_RUNNING'] = '1'
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔍 诊断CLI测试问题...")
print("=" * 60)

# 1. 测试Event导入
print("\n1. 测试Event类导入...")
try:
    from src.models.event import Event, EventType
    print("  ✅ Event类导入成功")
    
    # 尝试创建Event实例
    event = Event(
        type=EventType.SYSTEM,
        description="测试事件",
        turn=1
    )
    print("  ✅ Event实例创建成功")
    print(f"     ID: {event.id}")
    print(f"     Created: {event.created_at}")
except Exception as e:
    print(f"  ❌ Event类问题: {e}")

# 2. 测试CLI游戏导入
print("\n2. 测试CLIGame导入...")
try:
    from src.cli_game import CLIGame
    print("  ✅ CLIGame导入成功")
except Exception as e:
    print(f"  ❌ CLIGame导入失败: {e}")

# 3. 测试核心模块
print("\n3. 测试核心模块导入...")
modules = [
    "src.core.game_state",
    "src.core.rule_executor",
    "src.core.npc_behavior",
    "src.models.rule",
]

for module in modules:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except Exception as e:
        print(f"  ❌ {module}: {e}")

# 4. 测试pytest
print("\n4. 测试pytest环境...")
try:
    import pytest
    print(f"  ✅ pytest版本: {pytest.__version__}")
    
    # 检查插件
    plugins = ['pytest_asyncio', 'pytest_mock', 'pytest_cov']
    for plugin in plugins:
        try:
            __import__(plugin)
            print(f"  ✅ {plugin}")
        except ImportError:
            print(f"  ⚠️  {plugin} 未安装")
except ImportError:
    print("  ❌ pytest未安装")

# 5. 运行一个简单测试
print("\n5. 运行简单测试...")
try:
    from src.cli_game import CLIGame
    game = CLIGame()
    game.clear_screen = lambda: None  # 禁用清屏
    print("  ✅ CLIGame实例创建成功")
    
    # 测试基本方法
    game.print_game_status()  # 应该不输出任何内容（没有游戏状态）
    print("  ✅ 基本方法调用成功")
except Exception as e:
    print(f"  ❌ 运行时错误: {e}")

print("\n" + "=" * 60)
print("诊断完成！")

# 提供建议
print("\n💡 建议：")
if "Event类问题" in locals():
    print("- Event类已修复，请确保清理了__pycache__")
print("- 运行: python fix_cli_issues.py")
print("- 然后: python simple_cli_test.py")
