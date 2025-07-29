#!/usr/bin/env python3
"""超级简单的修复脚本 - 只做必要的修改"""
from pathlib import Path

print("🔧 应用修复...")

# 1. 修复测试文件
test_file = Path("tests/cli/test_cli_game.py")
if test_file.exists():
    content = test_file.read_text()
    # 修复test_new_game_creation_success的输入
    content = content.replace(
        'mock_input_sequence.add("n", "6")  # 选择不启用AI  # 确认创建，然后返回主菜单',
        'mock_input_sequence.add("n", "y", "6")  # 不启用AI，确认创建，返回主菜单'
    )
    # 备用模式
    content = content.replace(
        'mock_input_sequence.add("n", "6")',
        'mock_input_sequence.add("n", "y", "6")'
    )
    test_file.write_text(content)
    print("✓ 修复了测试输入序列")

# 2. 修复CLI游戏文件
cli_file = Path("src/cli_game.py")
if cli_file.exists():
    content = cli_file.read_text()
    # 修复Rule创建
    old = '''                rule = Rule(
                    id=f"rule_{len(self.game_manager.rules) + 1:03d}",
                    **template
                )'''
    new = '''                # 避免id重复
                template_copy = template.copy()
                template_copy.pop('id', None)
                
                rule = Rule(
                    id=f"rule_{len(self.game_manager.rules) + 1:03d}",
                    **template_copy
                )'''
    
    if old in content:
        content = content.replace(old, new)
        cli_file.write_text(content)
        print("✓ 修复了Rule创建问题")

print("\n✅ 修复完成！")
print("\n运行测试：")
print("pytest tests/cli/test_cli_game.py -v -x")
