#!/usr/bin/env python3
"""
快速验证测试修复
"""

import os
import sys
from pathlib import Path

# 设置环境变量
os.environ["PYTEST_RUNNING"] = "1"

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

def check_fixes():
    """检查关键修复"""
    print("🔍 检查修复...")
    
    # 1. 检查 game_state.py 的修复
    print("\n1️⃣ 检查 save_game 方法修复...")
    with open("src/core/game_state.py", "r") as f:
        content = f.read()
        if 'if not filename.endswith(\'.json\'):' in content:
            print("✅ save_game 方法已修复")
        else:
            print("❌ save_game 方法未修复")
            return False
    
    # 2. 检查 API 方法
    print("\n2️⃣ 检查 DeepSeek API 方法...")
    with open("src/api/deepseek_client.py", "r") as f:
        content = f.read()
        methods = [
            "evaluate_rule_async",
            "generate_narrative_async", 
            "generate_npc_batch_async"
        ]
        for method in methods:
            if f"async def {method}" in content:
                print(f"✅ {method} 方法存在")
            else:
                print(f"❌ {method} 方法缺失")
                return False
    
    # 3. 检查 rule_executor.py
    print("\n3️⃣ 检查 rule_executor 修复...")
    with open("src/core/rule_executor.py", "r") as f:
        content = f.read()
        if "self.game_manager.add_fear_points(" in content:
            print("✅ add_fear_points 方法调用已修复")
        else:
            print("❌ 仍在使用 gain_fear_points")
            return False
    
    return True


def test_save_functionality():
    """测试保存功能"""
    print("\n🧪 测试保存功能...")
    
    try:
        from src.core.game_state import GameStateManager
        
        gsm = GameStateManager()
        gsm.new_game("quick_test")
        
        # 测试保存
        test_files = []
        for name in ["test1", "test2.json"]:
            path = gsm.save_game(name)
            if path and Path(path).exists():
                test_files.append(path)
                expected = "test1.json" if name == "test1" else "test2.json"
                actual = Path(path).name
                if actual == expected:
                    print(f"✅ 保存 '{name}' -> '{actual}'")
                else:
                    print(f"❌ 保存 '{name}' -> '{actual}' (期望 '{expected}')")
            else:
                print(f"❌ 保存失败: {name}")
                return False
        
        # 清理
        for path in test_files:
            Path(path).unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """主函数"""
    print("="*50)
    print("RuleK 快速修复验证")
    print("="*50)
    
    # 检查修复
    if not check_fixes():
        print("\n❌ 代码修复检查失败")
        return False
    
    # 测试功能
    if not test_save_functionality():
        print("\n❌ 功能测试失败")
        return False
    
    print("\n✅ 所有修复验证通过！")
    print("\n可以运行以下命令进行完整测试：")
    print("1. 运行特定测试: PYTEST_RUNNING=1 pytest tests/cli/test_cli_game.py::TestSaveLoad -v")
    print("2. 运行所有测试: python rulek.py test")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
