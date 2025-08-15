#!/usr/bin/env python3
"""项目状态检查脚本"""
import os
from pathlib import Path

def check_status():
    """检查项目状态"""
    print("📊 RuleK 项目状态")
    print("=" * 40)
    
    # 检查关键文件
    files = [
        'rulek.py',
        'start_web_server.py',
        'requirements.txt',
        'Makefile',
        'README.md'
    ]
    
    print("📁 关键文件检查:")
    for file in files:
        status = "✅" if Path(file).exists() else "❌"
        print(f"  {status} {file}")
    
    # 检查目录
    dirs = ['src', 'web', 'tests', 'docs', 'config', 'scripts']
    print("\n📂 目录结构检查:")
    for dir_name in dirs:
        status = "✅" if Path(dir_name).exists() else "❌"
        print(f"  {status} {dir_name}/")
    
    # 统计Python文件
    py_files = list(Path(".").rglob("*.py"))
    print(f"\n📊 Python文件数量: {len(py_files)}")
    
    # 检查缓存文件
    cache_dirs = list(Path(".").rglob("__pycache__"))
    print(f"🗑️  缓存目录数量: {len(cache_dirs)}")
    
    if cache_dirs:
        print("   提示: 运行 'make clean' 清理缓存")

if __name__ == "__main__":
    check_status()
