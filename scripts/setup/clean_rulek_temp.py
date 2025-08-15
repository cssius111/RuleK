#!/usr/bin/env python3
"""
RuleK 临时清理脚本
运行后自动删除自身
"""

import os
import sys
import shutil
from pathlib import Path
import time

def clean_temp_files():
    """清理所有临时文件"""
    print("=" * 50)
    print("🧹 RuleK 项目临时文件清理器")
    print("=" * 50)
    print()
    
    # 要删除的临时脚本列表
    temp_scripts = [
        # 修复类脚本
        "fix_*.py",
        "auto_fix*.py",
        "emergency_*.py",
        "quick_fix*.py",
        "smart_*.py",
        "safe_*.py",
        
        # 测试类脚本
        "test_*.py",
        "verify_*.py",
        "quick_test*.py",
        "simple_test*.py",
        "basic_test*.py",
        
        # 临时运行脚本
        "go.py",
        "run.py",
        "check.py",
        "play.py",
        "play_cli.py",
        "debug_*.py",
        "quick_*.py",
        "simple_*.py",
        "basic_*.py",
        
        # 临时启动脚本
        "start_now.py",
        "start_enhanced.py",
        "auto_start.py",
        
        # 清理类脚本
        "cleanup_*.py",
        "clean_*.py",
        "*_cleanup.py",
        
        # 其他临时文件
        "temp_*.py",
        "tmp_*.py",
        "old_*.py",
        "backup_*.py",
    ]
    
    # 要删除的临时文档
    temp_docs = [
        "*_COMPLETE.md",
        "*_REPORT.md",
        "*_FIXED.md",
        "*_SUMMARY.md",
        "FIX_*.md",
        "FIXED_*.md",
        "TEST_*.md",
        "TEMP_*.md",
        "OLD_*.md",
        "BACKUP_*.md",
        "START_NOW.md",
        "QUICK_*.md",
    ]
    
    # 要删除的缓存目录和文件
    cache_patterns = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "*.pyc",
        "*.pyo",
        ".DS_Store",
        "*~",
        "*.backup",
        ".coverage",
        "htmlcov",
        "test_results",
    ]
    
    # 要保留的重要文件（白名单）
    keep_files = {
        "rulek.py",
        "start_web_server.py",
        "requirements.txt",
        "README.md",
        "LICENSE",
        "Makefile",
        "setup.py",
        ".env",
        ".gitignore",
        "PROJECT_PLAN.md",
        "AGENT.md",
    }
    
    deleted_count = 0
    deleted_files = []
    
    print("🔍 扫描临时脚本...")
    # 删除临时Python脚本
    for pattern in temp_scripts:
        for file_path in Path(".").glob(pattern):
            if file_path.name not in keep_files and file_path.name != os.path.basename(__file__):
                try:
                    file_path.unlink()
                    deleted_files.append(str(file_path))
                    deleted_count += 1
                    print(f"  ❌ 删除: {file_path}")
                except Exception as e:
                    print(f"  ⚠️  无法删除 {file_path}: {e}")
    
    print("\n🔍 扫描临时文档...")
    # 删除临时文档
    for pattern in temp_docs:
        for file_path in Path(".").glob(pattern):
            if file_path.name not in keep_files:
                try:
                    file_path.unlink()
                    deleted_files.append(str(file_path))
                    deleted_count += 1
                    print(f"  ❌ 删除: {file_path}")
                except Exception as e:
                    print(f"  ⚠️  无法删除 {file_path}: {e}")
    
    print("\n🔍 清理缓存文件...")
    # 删除缓存文件和目录
    for pattern in cache_patterns:
        for path in Path(".").rglob(pattern):
            if path.name not in keep_files:
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    deleted_count += 1
                    print(f"  🗑️  清理: {path}")
                except Exception:
                    pass
    
    # 清理空目录
    print("\n🔍 清理空目录...")
    for root, dirs, files in os.walk(".", topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            # 跳过重要目录
            if dir_name in {'.git', 'src', 'web', 'tests', 'docs', 'config', 'scripts', 'data', 'logs'}:
                continue
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    deleted_count += 1
                    print(f"  📁 删除空目录: {dir_path}")
            except:
                pass
    
    # 清理 .backups 目录（如果存在）
    backups_dir = Path(".backups")
    if backups_dir.exists():
        print("\n🔍 发现 .backups 目录")
        response = input("  是否删除 .backups 目录？[y/N]: ")
        if response.lower() == 'y':
            try:
                shutil.rmtree(backups_dir)
                deleted_count += 1
                print("  ✅ .backups 目录已删除")
            except Exception as e:
                print(f"  ❌ 无法删除 .backups: {e}")
    
    print("\n" + "=" * 50)
    print(f"✅ 清理完成！")
    print(f"📊 统计：")
    print(f"  - 删除了 {deleted_count} 个文件/目录")
    
    if deleted_files:
        print(f"\n📝 删除的主要文件：")
        for f in deleted_files[:10]:  # 只显示前10个
            print(f"  - {f}")
        if len(deleted_files) > 10:
            print(f"  ... 还有 {len(deleted_files) - 10} 个文件")
    
    print("\n💡 建议：")
    print("  - 运行 'make help' 查看可用命令")
    print("  - 运行 'python scripts/status.py' 检查项目状态")
    print("  - 使用 'make clean' 定期清理缓存")
    
    return deleted_count

def delete_self():
    """删除脚本自身"""
    script_path = Path(__file__)
    script_name = script_path.name
    
    print("\n" + "=" * 50)
    print("🔥 自毁程序启动...")
    print(f"📄 脚本名称: {script_name}")
    
    # 倒计时效果
    for i in range(3, 0, -1):
        print(f"  {i}...", end='', flush=True)
        time.sleep(0.5)
    
    print("\n💥 正在删除自身...", end='', flush=True)
    
    try:
        # Windows 和 Unix 系统的不同处理
        if sys.platform == "win32":
            # Windows: 创建批处理文件来删除
            batch_content = f"""@echo off
timeout /t 1 /nobreak > nul
del "{script_path.absolute()}"
del "%~f0"
"""
            batch_file = Path("_self_delete.bat")
            batch_file.write_text(batch_content)
            os.system(f'start /b "" "{batch_file.absolute()}"')
        else:
            # Unix/Linux/Mac: 使用shell命令
            os.system(f'(sleep 1 && rm -f "{script_path.absolute()}") &')
        
        print(" ✅")
        print(f"🎉 清理脚本 '{script_name}' 已完成任务并自毁！")
        print("\n👋 再见！")
        
    except Exception as e:
        print(f" ❌")
        print(f"⚠️  无法自动删除脚本: {e}")
        print(f"📝 请手动删除: rm {script_name}")

def main():
    """主函数"""
    try:
        # 显示警告
        print("⚠️  警告：此脚本将清理所有临时文件并删除自身！")
        print("📁 当前目录:", os.getcwd())
        print()
        
        # 检查是否在正确的目录
        if not Path("rulek.py").exists():
            print("❌ 错误：请在 RuleK 项目根目录运行此脚本！")
            print("   需要文件: rulek.py")
            sys.exit(1)
        
        # 确认执行
        response = input("确定要继续吗？[y/N]: ")
        if response.lower() != 'y':
            print("❌ 已取消")
            sys.exit(0)
        
        print()
        
        # 执行清理
        deleted_count = clean_temp_files()
        
        # 如果清理了文件，则删除自身
        if deleted_count > 0 or True:  # 总是删除自身
            delete_self()
        
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
