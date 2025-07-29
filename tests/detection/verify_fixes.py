#!/usr/bin/env python3
"""
测试修复的验证脚本
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_fixes():
    """测试所有修复是否正常工作"""
    print("🧪 验证修复...")
    
    success = True
    
    # 测试1: 验证 gain_fear_points 已修复为 add_fear_points
    print("\n1️⃣ 检查 rule_executor.py 中的方法名修复...")
    with open("src/core/rule_executor.py", "r") as f:
        content = f.read()
        if "gain_fear_points" in content:
            print("❌ 仍然存在 gain_fear_points 方法调用")
            success = False
        elif "add_fear_points" in content:
            print("✅ 已正确修改为 add_fear_points")
        else:
            print("⚠️ 未找到相关方法调用")
    
    # 测试2: 验证 game_state.py 的序列化方法
    print("\n2️⃣ 检查 game_state.py 的序列化方法...")
    try:
        from src.core.game_state import GameStateManager
        gsm = GameStateManager()
        
        # 测试序列化
        test_npc = {
            "id": "test_npc",
            "name": "测试NPC",
            "hp": 100,
            "nested": {
                "value": 123
            }
        }
        serialized = gsm._serialize_npc(test_npc)
        print(f"✅ NPC序列化成功: {serialized}")
        
        # 测试规则序列化
        class TestRule:
            def __init__(self):
                self.id = "test_rule"
                self.name = "测试规则"
                self.active = True
        
        test_rule = TestRule()
        serialized_rule = gsm._serialize_rule(test_rule)
        print(f"✅ 规则序列化成功: {serialized_rule}")
        
    except Exception as e:
        print(f"❌ 序列化测试失败: {e}")
        success = False
    
    # 测试3: 验证存档功能
    print("\n3️⃣ 测试存档和加载功能...")
    try:
        from src.core.game_state import GameStateManager
        from src.models.rule import Rule, RuleTrigger, RuleEffect, EffectType
        
        gsm = GameStateManager()
        
        # 创建测试游戏
        gsm.new_game("test_save_game")
        
        # 添加一个规则（测试规则序列化）
        test_rule = Rule(
            id="test_rule_1",
            name="测试规则",
            trigger=RuleTrigger(action="move", probability=0.5),
            effect=RuleEffect(type=EffectType.INSTANT_DEATH)
        )
        gsm.add_rule(test_rule)
        
        # 保存游戏
        save_path = gsm.save_game("test_save")
        if save_path:
            print(f"✅ 游戏保存成功: {save_path}")
            
            # 检查保存的文件
            with open(save_path, "r") as f:
                save_data = json.load(f)
                if "saved_at" in save_data:
                    print("✅ 保存数据包含时间戳")
                if "rules" in save_data and len(save_data["rules"]) > 0:
                    print("✅ 规则已正确序列化")
        else:
            print("❌ 游戏保存失败")
            success = False
            
        # 测试加载
        gsm2 = GameStateManager()
        if gsm2.load_game("test_save"):
            print("✅ 游戏加载成功")
            if gsm2.state is not None:
                print(f"✅ 游戏状态已恢复: 回合 {gsm2.state.current_turn}")
            else:
                print("❌ 游戏状态为空")
                success = False
        else:
            print("❌ 游戏加载失败")
            success = False
            
    except Exception as e:
        print(f"❌ 存档测试失败: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    # 测试4: 验证预创建的存档加载
    print("\n4️⃣ 测试预创建的存档加载...")
    try:
        from src.core.game_state import GameStateManager
        
        gsm3 = GameStateManager()
        if gsm3.load_game("loaded_game"):
            print("✅ 预创建的存档加载成功")
            if gsm3.state and gsm3.state.fear_points == 1200:
                print("✅ 游戏数据正确恢复")
            else:
                print("❌ 游戏数据恢复不正确")
                success = False
        else:
            print("❌ 无法加载预创建的存档")
            success = False
            
    except Exception as e:
        print(f"❌ 预创建存档测试失败: {e}")
        success = False
    
    # 清理测试文件
    try:
        test_save_path = Path("data/saves/test_save.json")
        if test_save_path.exists():
            test_save_path.unlink()
            print("\n🧹 清理测试文件完成")
    except:
        pass
    
    return success


if __name__ == "__main__":
    print("="*50)
    print("RuleK 测试修复验证脚本")
    print("="*50)
    
    # 设置环境变量
    os.environ["PYTEST_RUNNING"] = "1"
    
    if test_fixes():
        print("\n✅ 所有修复验证通过！")
        print("\n现在可以运行测试：")
        print("PYTEST_RUNNING=1 pytest tests/cli/test_cli_game.py -v")
        sys.exit(0)
    else:
        print("\n❌ 某些修复验证失败，请检查上面的错误信息")
        sys.exit(1)
