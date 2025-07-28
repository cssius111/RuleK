#!/usr/bin/env python3
"""
验证修复是否成功
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_imports():
    """验证导入是否正常"""
    print("🔍 验证导入...")
    
    try:
        # 测试 map 模块
        from src.models.map import MapManager, Area, create_default_map
        print("✅ map 模块导入成功")
        
        # 测试 dialogue_system 模块
        from src.core.dialogue_system import DialogueSystem, DialogueType, DialogueContext
        print("✅ dialogue_system 模块导入成功")
        
        # 测试 schemas 模块（Pydantic v2）
        from src.api.schemas import TurnPlan, DialogueTurn, PlannedAction
        print("✅ schemas 模块导入成功（Pydantic v2）")
        
        # 测试 turn_pipeline
        from src.ai.turn_pipeline import AITurnPipeline
        print("✅ turn_pipeline 模块导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False

def verify_classes():
    """验证类是否正常工作"""
    print("\n🔍 验证类功能...")
    
    try:
        # 测试 MapManager
        from src.models.map import create_default_map
        map_mgr = create_default_map()
        assert len(map_mgr.areas) > 0
        print("✅ MapManager 工作正常")
        
        # 测试 DialogueType
        from src.core.dialogue_system import DialogueType
        assert DialogueType.FEAR.value == "fear"
        print("✅ DialogueType 枚举正常")
        
        # 测试 Pydantic 模型
        from src.api.schemas import DialogueTurn
        dialogue = DialogueTurn(speaker="测试", text="测试对话")
        assert dialogue.speaker == "测试"
        print("✅ Pydantic 模型正常")
        
        return True
    except Exception as e:
        print(f"❌ 类测试失败: {e}")
        return False

def verify_game_state():
    """验证 GameState 访问"""
    print("\n🔍 验证 GameState 访问...")
    
    try:
        from src.core.game_state import GameStateManager
        
        # 创建游戏管理器
        game_mgr = GameStateManager()
        game_mgr.new_game("test")
        
        # 测试正确的访问方式
        assert hasattr(game_mgr, 'rules')  # 规则在 game_mgr 上
        assert hasattr(game_mgr, 'state')  # 状态在 game_mgr.state 上
        assert not hasattr(game_mgr.state, 'rules')  # state 没有 rules 属性
        
        print("✅ GameState 属性访问正常")
        return True
    except Exception as e:
        print(f"❌ GameState 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🧪 RuleK 修复验证脚本")
    print("=" * 50)
    
    results = []
    
    # 运行各项验证
    results.append(verify_imports())
    results.append(verify_classes())
    results.append(verify_game_state())
    
    # 总结
    print("\n" + "=" * 50)
    if all(results):
        print("✅ 所有验证通过！项目修复成功！")
        print("\n下一步：")
        print("1. 运行完整测试: python rulek.py test")
        print("2. 测试游戏: python rulek.py cli")
        return 0
    else:
        print("❌ 部分验证失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())
