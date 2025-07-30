#!/usr/bin/env python3
"""
检查项目中的备份和临时文件
"""
import os
from pathlib import Path
import json

def analyze_project_files():
    """分析项目文件结构"""
    root = Path(".")
    
    # 统计信息
    stats = {
        'backup_files': [],
        'temp_files': [],
        'fix_scripts': [],
        'test_scripts': [],
        'docs_in_root': [],
        'backups_dir_size': 0,
        'cache_dirs': []
    }
    
    # 检查.backups目录
    backups_dir = root / ".backups"
    if backups_dir.exists():
        print(f"\n✓ 发现 .backups 目录")
        backup_files = list(backups_dir.rglob("*"))
        if backup_files:
            print(f"  包含 {len(backup_files)} 个文件/目录:")
            for f in backup_files[:10]:  # 只显示前10个
                if f.is_file():
                    size = f.stat().st_size / 1024  # KB
                    print(f"  - {f.relative_to(root)} ({size:.1f} KB)")
                    stats['backups_dir_size'] += f.stat().st_size
            if len(backup_files) > 10:
                print(f"  ... 还有 {len(backup_files) - 10} 个文件")
        else:
            print("  目录为空")
    else:
        print("\n✗ 未发现 .backups 目录")
    
    # 检查根目录中的文件
    print("\n--- 根目录散乱文件 ---")
    
    # 备份文件
    for pattern in ["*.backup", "*.bak", "*~"]:
        for f in root.glob(pattern):
            stats['backup_files'].append(str(f))
            print(f"备份文件: {f}")
    
    # 修复脚本
    fix_patterns = ["fix_*.py", "quick_fix*.py", "auto_test_fix*.py", "optimize_*.py"]
    for pattern in fix_patterns:
        for f in root.glob(pattern):
            stats['fix_scripts'].append(str(f))
            print(f"修复脚本: {f}")
    
    # 测试脚本
    test_patterns = ["*test*.py", "play*.py", "debug*.py", "smart_debug*.py"]
    for pattern in test_patterns:
        for f in root.glob(pattern):
            if f.name not in ["pytest.ini", "setup.py"] and "test" in f.name or "play" in f.name or "debug" in f.name:
                stats['test_scripts'].append(str(f))
                print(f"测试/调试脚本: {f}")
    
    # 文档文件
    for f in root.glob("*.md"):
        if f.name not in ["README.md", "LICENSE", "CONTRIBUTING.md"]:
            stats['docs_in_root'].append(str(f))
            print(f"文档文件: {f}")
    
    # 缓存目录
    cache_patterns = [".pytest_cache", "__pycache__", "htmlcov", ".coverage"]
    for pattern in cache_patterns:
        for d in root.rglob(pattern):
            stats['cache_dirs'].append(str(d))
    
    # 统计汇总
    print("\n=== 统计汇总 ===")
    print(f"备份文件: {len(stats['backup_files'])} 个")
    print(f"修复脚本: {len(stats['fix_scripts'])} 个")
    print(f"测试脚本: {len(stats['test_scripts'])} 个")
    print(f"根目录文档: {len(stats['docs_in_root'])} 个")
    print(f"缓存目录: {len(stats['cache_dirs'])} 个")
    if stats['backups_dir_size'] > 0:
        size_mb = stats['backups_dir_size'] / (1024 * 1024)
        print(f".backups 目录大小: {size_mb:.1f} MB")
    
    # 建议
    print("\n=== 建议 ===")
    if backups_dir.exists() and stats['backups_dir_size'] > 0:
        print("• .backups 目录占用空间，如果已有 Git 版本控制，建议删除")
    if stats['backup_files']:
        print("• 发现备份文件，建议清理")
    if stats['fix_scripts']:
        print("• 发现多个修复脚本，建议移到 scripts/fixes/ 或删除")
    if stats['test_scripts']:
        print("• 发现多个测试脚本，建议移到 scripts/test/")
    if stats['cache_dirs']:
        print("• 发现缓存目录，建议定期清理")
    
    # 保存分析结果
    with open("project_analysis.json", "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\n分析结果已保存到: project_analysis.json")

if __name__ == "__main__":
    print("=== RuleK 项目文件分析 ===")
    analyze_project_files()
