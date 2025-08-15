#!/usr/bin/env python3
"""项目清理脚本"""
import os
import shutil
from pathlib import Path

def clean():
    """清理项目临时文件"""
    patterns_to_delete = [
        "__pycache__",
        ".pytest_cache", 
        ".mypy_cache",
        "*.pyc",
        "*.pyo",
        ".coverage",
        "htmlcov",
        ".DS_Store",
        "*~",
        "*.backup"
    ]
    
    print("🧹 开始清理项目...")
    count = 0
    
    for pattern in patterns_to_delete:
        for path in Path(".").rglob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                count += 1
                print(f"  删除: {path}")
            except:
                pass
    
    print(f"✅ 清理完成！删除了 {count} 个文件/目录")

if __name__ == "__main__":
    clean()
