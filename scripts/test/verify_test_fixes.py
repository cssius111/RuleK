#!/usr/bin/env python3
"""
测试修复验证脚本
验证移除默认NPC后的测试是否正常工作
"""
import subprocess
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置测试环境变量
os.environ['PYTEST_RUNNING'] = '1'

def run_test(test_path):
    """运行单个测试并返回结果"""
    cmd = ['pytest', test_path, '-v']
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    """主函数"""
    print("="*60)
    print("测试修复验证")
    print("="*60)
    
    # 需要验证的测试
    tests_to_verify = [
        ('tests/cli/test_cli_game.py::TestMainMenu::test_new_game_creation_success', 'CLI新游戏创建'),
        ('tests/cli/test_cli_game.py::TestActionPhase::test_action_phase_rule_trigger', '规则触发测试'),
        ('tests/cli/test_cli_game.py::TestDialoguePhase::test_dialogue_phase_with_npcs', '对话阶段测试'),
        ('tests/unit/test_core.py::test_game_state_manager', '游戏状态管理'),
        ('tests/unit/test_core.py::test_npc_behavior', 'NPC行为测试'),
        ('tests/unit/test_core.py::test_rule_executor', '规则执行器测试'),
    ]
    
    results = []
    for test_path, description in tests_to_verify:
        print(f"\n测试: {description}")
        print(f"路径: {test_path}")
        print("-"*40)
        
        success, stdout, stderr = run_test(test_path)
        
        if success:
            print("✅ 通过")
        else:
            print("❌ 失败")
            # 打印错误信息
            if "FAILED" in stdout:
                # 提取失败信息
                lines = stdout.split('\n')
                for i, line in enumerate(lines):
                    if "FAILED" in line:
                        print(f"  错误: {line}")
                        # 打印接下来的几行错误详情
                        for j in range(i+1, min(i+5, len(lines))):
                            if lines[j].strip():
                                print(f"  {lines[j]}")
        
        results.append((description, success))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{description:30} {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试都通过了！")
    else:
        print(f"\n⚠️  还有 {total - passed} 个测试需要修复")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
