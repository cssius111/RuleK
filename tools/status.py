#!/usr/bin/env python3
"""
项目状态检查
"""
import os
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent

def analyze_project():
    """分析项目结构"""
    stats = defaultdict(int)
    file_types = defaultdict(list)
    
    # 临时文件列表
    temp_patterns = [
        "fix_", "test_", "verify_", "check", "auto_", "smart_", 
        "safe_", "quick_", "simple_", "basic_", "final_", "emergency_"
    ]
    
    for item in PROJECT_ROOT.iterdir():
        if item.is_file():
            # 统计文件类型
            if item.suffix == '.py':
                # 检查是否是临时脚本
                is_temp = any(item.name.startswith(p) for p in temp_patterns)
                if is_temp:
                    file_types['临时脚本'].append(item.name)
                else:
                    file_types['Python文件'].append(item.name)
                    
            elif item.suffix == '.md':
                # 检查是否是临时文档
                temp_docs = ['FIX', 'FIXED', 'SOLUTION', 'START_NOW', 'TEST_', 'FINAL_']
                is_temp_doc = any(item.name.startswith(p) for p in temp_docs)
                if is_temp_doc:
                    file_types['临时文档'].append(item.name)
                else:
                    file_types['文档'].append(item.name)
                    
            elif item.suffix in ['.sh', '.bat']:
                file_types['脚本'].append(item.name)
            else:
                file_types['其他'].append(item.name)
    
    # 统计目录
    dirs = [d.name for d in PROJECT_ROOT.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    # 计算缓存大小
    cache_count = 0
    for root, dirnames, filenames in os.walk(PROJECT_ROOT):
        cache_count += dirnames.count('__pycache__')
    
    return {
        'file_types': dict(file_types),
        'directories': dirs,
        'cache_dirs': cache_count
    }

def print_report(stats):
    """打印分析报告"""
    print("""
╔══════════════════════════════════════════════════╗
║           RuleK 项目状态分析                    ║
╚══════════════════════════════════════════════════╝
    """)
    
    # 打印文件统计
    for category, files in stats['file_types'].items():
        if files:
            print(f"\n📁 {category} ({len(files)}个):")
            if category in ['临时脚本', '临时文档']:
                # 临时文件显示详细列表
                for f in sorted(files)[:10]:  # 最多显示10个
                    print(f"   ⚠️  {f}")
                if len(files) > 10:
                    print(f"   ... 还有 {len(files)-10} 个")
            else:
                # 正常文件只显示数量
                if len(files) <= 5:
                    for f in sorted(files):
                        print(f"   ✅ {f}")
                else:
                    print(f"   ✅ {len(files)} 个文件")
    
    # 打印目录
    print(f"\n📂 核心目录 ({len(stats['directories'])}个):")
    core_dirs = ['src', 'web', 'config', 'tests', 'docs', 'scripts', 'data', 'logs']
    for d in core_dirs:
        if d in stats['directories']:
            print(f"   ✅ {d}/")
    
    other_dirs = [d for d in stats['directories'] if d not in core_dirs]
    if other_dirs:
        print("\n📂 其他目录:")
        for d in other_dirs:
            print(f"   📁 {d}/")
    
    # 缓存统计
    if stats['cache_dirs'] > 0:
        print(f"\n🗑️  Python缓存: {stats['cache_dirs']} 个 __pycache__ 目录")
    
    # 建议
    temp_count = len(stats['file_types'].get('临时脚本', [])) + len(stats['file_types'].get('临时文档', []))
    if temp_count > 0:
        print(f"\n💡 建议:")
        print(f"   发现 {temp_count} 个临时文件可以清理")
        print(f"   运行 'python clean.py' 进行清理")
    else:
        print("\n✅ 项目结构清晰，无需清理")
    
    # 启动提示
    print("\n🚀 启动服务器:")
    print("   python start_web_server.py")
    print("   或: python rulek.py web")

def main():
    stats = analyze_project()
    print_report(stats)

if __name__ == "__main__":
    main()
