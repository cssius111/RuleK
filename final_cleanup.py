#!/usr/bin/env python3
"""
最终清理脚本 - 删除所有临时和测试文件
"""
import os
import shutil
from pathlib import Path

# 要删除的文件列表
DELETE_FILES = [
    "cleanup_project.py",  # 之前的清理脚本
    "start_web_server.py",  # 已有 web 模块
]

# 要移动到 scripts/test/ 的文件
MOVE_TO_SCRIPTS_TEST = [
    "check_missing_modules.py",
    "fix_ai_issues.py",
    "minimal_test.py",
    "quick_verify.py",
    "test_all_fixes.py",
    "test_fixes.py",
    "verify_ai_integration.py",
    "verify_final.py",
    "verify_fix.py",
    "verify_fix_v2.py",
    "verify_fixes.py",
]

# 要移动到 docs/ 的文件
MOVE_TO_DOCS = [
    "AI_Integration_Phase3_Complete_Report.md",
    "AI_Integration_Phase3_Summary.md",
    "AI_Integration_Progress_Report_Phase3_Complete.md",
    "CLI_TEST_FIX_REPORT.md",
    "NEXT_STEPS.md",
    "QUICK_START_FIXED.md",
    "QUICK_START_GAME.md",
    "RUN_GAME_NOW.md",
    "TEST_FIX_SUMMARY.md",
]

def main():
    print("🧹 最终清理...")
    
    # 创建目录
    Path("scripts/test").mkdir(parents=True, exist_ok=True)
    
    # 移动测试脚本
    for file in MOVE_TO_SCRIPTS_TEST:
        if os.path.exists(file):
            try:
                shutil.move(file, f"scripts/test/{file}")
                print(f"✅ 移动 {file} 到 scripts/test/")
            except:
                pass
    
    # 移动文档
    for file in MOVE_TO_DOCS:
        if os.path.exists(file):
            try:
                shutil.move(file, f"docs/{file}")
                print(f"✅ 移动 {file} 到 docs/")
            except:
                pass
    
    # 删除临时文件
    for file in DELETE_FILES:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️  删除 {file}")
            except:
                pass
    
    # 清理缓存
    cache_dirs = [".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__"]
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"🗑️  清理 {cache_dir}")
            except:
                pass
    
    # 递归清理所有 __pycache__
    for pycache in Path(".").rglob("__pycache__"):
        try:
            shutil.rmtree(pycache)
        except:
            pass
    
    print("\n✅ 清理完成！")
    print("\n项目现在应该是干净的状态了。")
    print("运行 'python rulek.py test' 来验证一切正常。")

if __name__ == "__main__":
    main()
