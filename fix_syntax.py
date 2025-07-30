#!/usr/bin/env python3
"""
快速修复RuleK项目中的语法错误
"""

import os
import re

def fix_npc_syntax():
    """修复npc.py中第412行的语法错误"""
    file_path = "src/models/npc.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复model_config的语法错误
        # 查找包含错误的部分
        pattern = r'model_config = ConfigDict\(\s*""".*?"""\s*use_enum_values\s*=\s*True'
        
        if 'model_config = ConfigDict(' in content and '"""Pydantic配置"""' in content:
            # 使用更精确的替换
            lines = content.split('\n')
            fixed_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                if 'model_config = ConfigDict(' in line:
                    # 找到了问题行
                    fixed_lines.append('    model_config = ConfigDict(')
                    fixed_lines.append('        use_enum_values=True')
                    fixed_lines.append('    )')
                    
                    # 跳过问题行
                    i += 1
                    while i < len(lines) and (
                        '"""Pydantic配置"""' in lines[i] or 
                        'use_enum_values' in lines[i] or
                        lines[i].strip() == ''
                    ):
                        i += 1
                    i -= 1  # 回退一步
                else:
                    fixed_lines.append(line)
                i += 1
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
                
            print(f"✅ 已修复 {file_path}")
            return True
        else:
            print(f"⚠️ 在 {file_path} 中未找到预期的错误模式")
            return False
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def fix_fstring_errors():
    """修复f-string中的import错误"""
    files = ["auto_test_fix.py", "optimize_ai.py"]
    
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"⚠️ 文件不存在: {file_path}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否需要修复
            if 'import datetime;datetime.datetime.now()' not in content:
                print(f"⚠️ {file_path} 中未找到需要修复的f-string错误")
                continue
            
            # 添加datetime导入到文件顶部
            lines = content.split('\n')
            
            # 检查是否已经有datetime导入
            has_datetime_import = any('import datetime' in line for line in lines[:20])
            
            if not has_datetime_import:
                # 找到合适的位置插入import
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith('"""') or line.startswith('#'):
                        continue
                    elif line.startswith('import ') or line.startswith('from '):
                        insert_pos = i
                        break
                    elif line.strip() and not line.startswith('#'):
                        insert_pos = i
                        break
                
                lines.insert(insert_pos, 'import datetime')
            
            # 修复f-string中的错误语法
            content = '\n'.join(lines)
            content = re.sub(
                r'f"生成时间: \{import datetime;datetime\.datetime\.now\(\)\}',
                r'f"生成时间: {datetime.datetime.now()}',
                content
            )
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ 已修复 {file_path}")
            
        except Exception as e:
            print(f"❌ 修复 {file_path} 失败: {e}")

def test_syntax():
    """测试关键文件的语法"""
    test_files = [
        "src/models/npc.py",
        "auto_test_fix.py", 
        "optimize_ai.py"
    ]
    
    print("\n🔍 测试语法...")
    all_good = True
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, file_path, 'exec')
                print(f"✅ {file_path}")
            except SyntaxError as e:
                print(f"❌ {file_path} 第{e.lineno}行: {e.msg}")
                if e.text:
                    print(f"   问题代码: {e.text.strip()}")
                all_good = False
            except Exception as e:
                print(f"⚠️ {file_path}: {e}")
    
    return all_good

def main():
    print("🔧 快速修复RuleK语法错误")
    print("=" * 40)
    
    # 确认在正确目录
    if not os.path.exists("src"):
        print("❌ 错误: 请在RuleK项目根目录运行")
        print("当前目录:", os.getcwd())
        return
    
    print("📁 当前目录:", os.getcwd())
    
    # 修复npc.py
    print("\n1. 修复npc.py语法错误...")
    fix_npc_syntax()
    
    # 修复f-string错误
    print("\n2. 修复f-string错误...")
    fix_fstring_errors()
    
    # 测试语法
    if test_syntax():
        print("\n🎉 所有语法错误已修复!")
        print("\n🚀 现在可以运行:")
        print("   python smart_debug.py")
        print("   pytest -v")
        print("   python auto_test_fix.py")
    else:
        print("\n⚠️ 还有一些语法问题需要手动检查")
        print("\n💡 如果问题仍然存在，请:")
        print("   1. 检查src/models/npc.py第412行附近")
        print("   2. 确保所有括号正确配对")
        print("   3. 检查f-string语法")

if __name__ == "__main__":
    main()
