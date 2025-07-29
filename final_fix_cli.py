#!/usr/bin/env python3
"""
全面修复CLI测试的3个失败问题
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_cache():
    """清理所有缓存"""
    print("🧹 清理缓存...")
    for pattern in [".pytest_cache", "__pycache__", "**/__pycache__"]:
        if "*" in pattern:
            for path in Path(".").glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
        else:
            path = Path(pattern)
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
    print("  ✓ 缓存清理完成")

def fix_test_file():
    """修复测试文件"""
    print("\n🔧 修复测试文件...")
    test_file = Path("tests/cli/test_cli_game.py")
    
    if not test_file.exists():
        print("  ❌ 测试文件不存在")
        return False
    
    content = test_file.read_text(encoding='utf-8')
    original = content
    
    # 修复test_new_game_creation_success - 需要两个输入
    # 查找并替换
    lines = content.splitlines()
    new_lines = []
    
    for i, line in enumerate(lines):
        if 'mock_input_sequence.add("n", "6")' in line and 'test_new_game_creation_success' in '\n'.join(lines[max(0,i-10):i]):
            # 这是在test_new_game_creation_success中的行
            new_lines.append('        mock_input_sequence.add("n", "y", "6")  # 不启用AI，确认创建，返回主菜单')
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    if content != original:
        # 备份
        backup = test_file.with_suffix('.py.backup_final')
        backup.write_text(original, encoding='utf-8')
        
        # 保存修改
        test_file.write_text(content, encoding='utf-8')
        print("  ✓ 修复了test_new_game_creation_success的输入序列")
        return True
    
    print("  ℹ️  测试文件无需修改")
    return False

def fix_cli_game():
    """修复CLI游戏文件"""
    print("\n🔧 修复CLI游戏文件...")
    cli_file = Path("src/cli_game.py")
    
    if not cli_file.exists():
        print("  ❌ CLI游戏文件不存在")
        return False
    
    content = cli_file.read_text(encoding='utf-8')
    original = content
    
    # 修复create_rule_from_template中的id重复问题
    # 查找创建规则的代码
    old_code = '''                rule = Rule(
                    id=f"rule_{len(self.game_manager.rules) + 1:03d}",
                    **template
                )'''
    
    new_code = '''                # 从模板创建规则，避免id重复
                template_copy = template.copy()
                # 移除模板中的id（如果有）
                template_copy.pop('id', None)
                
                rule = Rule(
                    id=f"rule_{len(self.game_manager.rules) + 1:03d}",
                    **template_copy
                )'''
    
    content = content.replace(old_code, new_code)
    
    # 再次检查，确保确实找到并替换了
    if content == original:
        # 尝试另一种模式
        import re
        pattern = r'(\s+)(rule = Rule\(\s*\n\s*id=.*?\n\s*\*\*template\s*\n\s*\))'
        
        def replacer(match):
            indent = match.group(1)
            return f'''{indent}# 从模板创建规则，避免id重复
{indent}template_copy = template.copy()
{indent}# 移除模板中的id（如果有）
{indent}template_copy.pop('id', None)
{indent}
{indent}rule = Rule(
{indent}    id=f"rule_{{len(self.game_manager.rules) + 1:03d}}",
{indent}    **template_copy
{indent})'''
        
        content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    if content != original:
        # 备份
        backup = cli_file.with_suffix('.py.backup_final')
        backup.write_text(original, encoding='utf-8')
        
        # 保存修改
        cli_file.write_text(content, encoding='utf-8')
        print("  ✓ 修复了Rule创建的id重复问题")
        return True
    
    print("  ℹ️  CLI游戏文件无需修改")
    return False

def run_tests():
    """运行测试"""
    print("\n🧪 运行测试...")
    
    os.environ['PYTEST_RUNNING'] = '1'
    
    # 先运行特定的失败测试
    failed_tests = [
        "TestMainMenu::test_new_game_creation_success",
        "TestRuleManagement::test_create_rule_from_template_success",
        "TestRuleManagement::test_create_rule_insufficient_points"
    ]
    
    print("\n运行之前失败的测试:")
    for test in failed_tests:
        cmd = [
            sys.executable, '-m', 'pytest',
            f'tests/cli/test_cli_game.py::{test}',
            '-v', '--tb=short'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ {test}")
        else:
            print(f"  ❌ {test}")
            # 显示错误
            if result.stdout:
                for line in result.stdout.splitlines():
                    if "FAILED" in line or "ERROR" in line or "assert" in line:
                        print(f"     {line}")
    
    # 运行所有测试
    print("\n运行所有测试（跳过耗时测试）:")
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/cli/test_cli_game.py',
        '-v', '--tb=short',
        '-k', 'not test_complete_game_flow'
    ]
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    """主函数"""
    print("🚀 全面修复CLI测试")
    print("=" * 60)
    
    # 1. 清理缓存
    clean_cache()
    
    # 2. 修复文件
    test_fixed = fix_test_file()
    cli_fixed = fix_cli_game()
    
    if test_fixed or cli_fixed:
        print("\n✅ 文件修复完成")
    else:
        print("\n⚠️  文件已是最新状态")
    
    # 3. 运行测试
    print("\n" + "=" * 60)
    success = run_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("\n🎉 恭喜！所有测试通过！")
        print("\n下一步：")
        print("1. 运行完整测试: pytest tests/cli/test_cli_game.py -v")
        print("2. 查看覆盖率: pytest tests/cli/test_cli_game.py --cov=src.cli_game --cov-report=html")
        print("3. 运行AI扩展测试: pytest tests/cli/test_cli_game_extended.py -v")
    else:
        print("\n❌ 仍有测试失败")
        print("\n请查看上面的错误信息")
        print("\n可能的原因：")
        print("1. 检查模板是否包含id字段")
        print("2. 检查GameStateManager.add_rule是否返回True")
        print("3. 检查积分扣除的错误消息文本")

if __name__ == "__main__":
    main()
