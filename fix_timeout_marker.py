#!/usr/bin/env python3
"""快速修复pytest timeout marker问题"""
import re
from pathlib import Path

def remove_timeout_markers():
    """移除测试文件中的timeout标记"""
    test_file = Path("tests/cli/test_cli_game.py")
    
    if not test_file.exists():
        print("❌ 测试文件不存在")
        return False
    
    content = test_file.read_text(encoding='utf-8')
    original = content
    
    # 移除所有timeout相关的标记
    patterns = [
        r'@pytest\.mark\.timeout\([^)]+\).*\n\s*',  # 移除整行
        r'@pytest\.mark\.timeout.*\n\s*',           # 移除整行（简化版）
        r'# 注意：如果使用timeout，需要安装pytest-timeout\n',  # 移除注释
    ]
    
    for pattern in patterns:
        content = re.sub(pattern, '', content)
    
    if content != original:
        # 备份原文件
        backup_file = test_file.with_suffix('.py.backup_timeout')
        backup_file.write_text(original, encoding='utf-8')
        
        # 写入修改后的内容
        test_file.write_text(content, encoding='utf-8')
        
        print("✅ 已移除timeout标记")
        print(f"   备份保存在: {backup_file}")
        return True
    else:
        print("ℹ️  没有找到timeout标记")
        return False

def fix_pyproject_toml():
    """在pyproject.toml中添加timeout marker"""
    pyproject_file = Path("pyproject.toml")
    
    if not pyproject_file.exists():
        print("⚠️  pyproject.toml 不存在")
        return False
    
    content = pyproject_file.read_text(encoding='utf-8')
    
    # 检查是否已经有timeout marker
    if 'timeout:' in content:
        print("ℹ️  timeout marker 已存在")
        return False
    
    # 在markers列表中添加timeout
    pattern = r'(markers = \[)(.*?)(\])'
    
    def replacer(match):
        markers = match.group(2)
        if markers.strip() and not markers.strip().endswith(','):
            markers = markers.rstrip() + ','
        markers += '\n    "timeout: marks tests with timeout limit",'
        return match.group(1) + markers + match.group(3)
    
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    if new_content != content:
        # 备份
        backup_file = pyproject_file.with_suffix('.toml.backup')
        backup_file.write_text(content, encoding='utf-8')
        
        # 写入
        pyproject_file.write_text(new_content, encoding='utf-8')
        
        print("✅ 已在pyproject.toml中添加timeout marker")
        return True
    
    return False

def main():
    """主函数"""
    print("🔧 修复pytest timeout marker问题...")
    print("=" * 60)
    
    print("\n选择修复方式：")
    print("1. 移除测试文件中的timeout标记（推荐）")
    print("2. 在pyproject.toml中注册timeout marker")
    print("3. 两个都做")
    
    choice = input("\n请选择 (1/2/3) [默认1]: ").strip() or "1"
    
    if choice == "1":
        remove_timeout_markers()
    elif choice == "2":
        fix_pyproject_toml()
    elif choice == "3":
        remove_timeout_markers()
        fix_pyproject_toml()
    else:
        print("无效选择")
        return
    
    print("\n✅ 修复完成！")
    print("\n下一步：")
    print("1. 运行: python quick_test_cli.py")
    print("2. 或运行: pytest tests/cli/test_cli_game.py -v")

if __name__ == "__main__":
    main()
