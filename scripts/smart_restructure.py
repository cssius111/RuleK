#!/usr/bin/env python3
"""
RuleK 渐进式重构工具
遵循MAIN_AGENT规则，缝缝补补而不是推倒重来
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class SmartRestructure:
    """智能重构工具 - 遵循Agent规则"""
    
    def __init__(self, dry_run: bool = False):
        self.root = Path.cwd()
        self.dry_run = dry_run
        self.backup_dir = self.root / ".backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.changes = []
        
        # 根目录应该保留的文件
        self.root_keep = [
            "README.md",
            "LICENSE",
            "requirements.txt",
            ".env",
            ".env.example",
            ".gitignore",
            "pyproject.toml",
            "Makefile",
            "rulek.py",  # 统一入口
            "MAIN_AGENT.md",  # Agent规则
            "AGENT.md",
            "PROJECT_PLAN.md",
            "PROJECT_STRUCTURE.md",
            "package.json",  # 前端依赖
            "package-lock.json",
            "start.sh",  # 快速启动
            "start.bat",
            ".pre-commit-config.yaml",
        ]
        
        # 文件移动规则
        self.move_rules = [
            # 管理工具 -> scripts/
            ("manage.py", "scripts/manage.py"),
            ("start_web_server.py", "scripts/startup/start_web_server.py"),
            
            # 测试脚本 -> scripts/test/
            ("test_*.py", "scripts/test/"),
            ("verify_*.py", "scripts/test/"),
            
            # 修复脚本 -> scripts/fix/
            ("fix_*.py", "scripts/fix/"),
            ("quick_*.py", "scripts/fix/"),
            
            # 工具 -> tools/
            ("tools/*.py", "scripts/utils/"),
        ]
    
    def analyze(self) -> Dict:
        """分析需要重构的内容"""
        analysis = {
            "root_files_to_move": [],
            "empty_dirs": [],
            "duplicate_files": [],
            "wrong_location": [],
        }
        
        # 检查根目录文件
        for item in self.root.iterdir():
            if item.is_file() and item.name not in self.root_keep:
                if item.suffix in [".py", ".sh", ".bat"]:
                    analysis["root_files_to_move"].append(item.name)
        
        # 检查空目录
        for dir_path in ["rulek", ".agents", "test-results"]:
            full_path = self.root / dir_path
            if full_path.exists() and full_path.is_dir():
                if not list(full_path.rglob("*")):
                    analysis["empty_dirs"].append(dir_path)
        
        return analysis
    
    def backup_file(self, file_path: Path) -> bool:
        """备份文件"""
        if not file_path.exists():
            return False
            
        if not self.dry_run:
            backup_path = self.backup_dir / file_path.relative_to(self.root)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
        
        return True
    
    def move_file(self, source: Path, dest: Path) -> bool:
        """移动文件（遵循Agent规则）"""
        if not source.exists():
            return False
            
        # 记录操作
        self.changes.append(f"移动: {source} -> {dest}")
        
        if not self.dry_run:
            # 备份
            self.backup_file(source)
            
            # 创建目标目录
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # 移动文件
            shutil.move(str(source), str(dest))
        
        return True
    
    def clean_root_directory(self) -> int:
        """清理根目录（保守方式）"""
        moved = 0
        
        # 移动manage.py
        if (self.root / "manage.py").exists():
            self.move_file(
                self.root / "manage.py",
                self.root / "scripts" / "manage.py"
            )
            moved += 1
        
        # 移动start_web_server.py
        if (self.root / "start_web_server.py").exists():
            startup_dir = self.root / "scripts" / "startup"
            if not self.dry_run:
                startup_dir.mkdir(parents=True, exist_ok=True)
            self.move_file(
                self.root / "start_web_server.py",
                startup_dir / "start_web_server.py"
            )
            moved += 1
        
        return moved
    
    def remove_empty_directories(self) -> int:
        """删除空目录"""
        removed = 0
        
        for dir_name in ["rulek", ".agents", "test-results"]:
            dir_path = self.root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                if not list(dir_path.rglob("*")):
                    self.changes.append(f"删除空目录: {dir_name}")
                    if not self.dry_run:
                        shutil.rmtree(dir_path)
                    removed += 1
        
        return removed
    
    def update_imports(self) -> int:
        """更新导入路径（TODO）"""
        # 这个功能稍后实现
        return 0
    
    def run(self) -> Dict:
        """执行重构"""
        print("🔧 RuleK 渐进式重构")
        print("=" * 50)
        
        if self.dry_run:
            print("⚠️  预览模式 - 不会实际修改文件")
        else:
            print("💾 备份目录: {}".format(self.backup_dir.relative_to(self.root)))
        
        print()
        
        # 分析
        print("🔍 分析项目结构...")
        analysis = self.analyze()
        
        if analysis["root_files_to_move"]:
            print(f"  根目录需要移动的文件: {len(analysis['root_files_to_move'])}")
            for f in analysis["root_files_to_move"]:
                print(f"    - {f}")
        
        if analysis["empty_dirs"]:
            print(f"  空目录: {len(analysis['empty_dirs'])}")
            for d in analysis["empty_dirs"]:
                print(f"    - {d}/")
        
        print()
        
        # 执行重构
        results = {
            "files_moved": 0,
            "dirs_removed": 0,
            "errors": [],
        }
        
        # 1. 清理根目录
        print("🧹 清理根目录...")
        results["files_moved"] = self.clean_root_directory()
        
        # 2. 删除空目录
        print("🗑️  删除空目录...")
        results["dirs_removed"] = self.remove_empty_directories()
        
        # 显示结果
        print()
        print("✅ 重构完成！")
        print("=" * 50)
        print(f"  移动文件: {results['files_moved']}")
        print(f"  删除目录: {results['dirs_removed']}")
        
        if self.changes:
            print("\n📋 变更记录：")
            for change in self.changes:
                print(f"  - {change}")
        
        if self.dry_run:
            print("\n💡 这是预览模式，使用 --execute 执行实际重构")
        
        return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="RuleK渐进式重构工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python restructure.py          # 预览模式
  python restructure.py --execute # 执行重构
"""
    )
    
    parser.add_argument(
        "--execute",
        action="store_true",
        help="执行实际重构（默认是预览模式）"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式（默认）"
    )
    
    args = parser.parse_args()
    
    # 默认是预览模式
    dry_run = not args.execute
    
    restructure = SmartRestructure(dry_run=dry_run)
    restructure.run()


if __name__ == "__main__":
    main()
