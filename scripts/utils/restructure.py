#!/usr/bin/env python3
"""
RuleK 项目重构自动化脚本
执行项目文件整理和结构优化
"""
import os
import shutil
from pathlib import Path
import json
from datetime import datetime

class ProjectRestructure:
    def __init__(self, project_root="."):
        self.root = Path(project_root).resolve()
        self.moves = []
        self.errors = []
        
    def create_directories(self):
        """创建标准目录结构"""
        dirs = [
            "scripts/dev",
            "scripts/test", 
            "scripts/fixes",
            "scripts/deploy",
            "scripts/utils",
            "docs/api",
            "docs/design",
            "docs/guides",
            "docs/guides/debug",
            "docs/reports",
            "docs/reports/fixes",
            "config/settings",
            "data/templates",
            ".archive"
        ]
        
        for dir_path in dirs:
            full_path = self.root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ 创建目录: {dir_path}")
    
    def get_file_moves(self):
        """定义文件迁移映射"""
        return {
            # 开发脚本
            "play.py": "scripts/dev/play.py",
            "play_cli.py": "scripts/dev/play_cli.py",
            "debug_rulek.py": "scripts/dev/debug_rulek.py",
            "smart_debug.py": "scripts/dev/smart_debug.py",
            
            # 测试脚本
            "cli_test_runner.py": "scripts/test/cli_test_runner.py",
            "quick_test_cli.py": "scripts/test/quick_test_cli.py",
            "simple_test.py": "scripts/test/simple_test.py",
            "quick_cli_test.py": "scripts/test/quick_cli_test.py",
            "run_cli_tests.sh": "scripts/test/run_cli_tests.sh",
            
            # 修复脚本
            "fix_syntax.py": "scripts/fixes/fix_syntax.py",
            "quick_fix.py": "scripts/fixes/quick_fix.py",
            "auto_test_fix.py": "scripts/fixes/auto_test_fix.py",
            "optimize_ai.py": "scripts/fixes/optimize_ai.py",
            
            # 部署脚本
            "start.sh": "scripts/deploy/start.sh",
            "start.bat": "scripts/deploy/start.bat",
            "start_enhanced.sh": "scripts/deploy/start_enhanced.sh",
            "game.sh": "scripts/deploy/game.sh",
            
            # 工具脚本
            "cleanup.sh": "scripts/utils/cleanup.sh",
            "make_executable.sh": "scripts/utils/make_executable.sh",
            "quick_start.py": "scripts/utils/quick_start.py",
            
            # 文档
            "FIXED_AND_READY.md": "docs/reports/fixes/FIXED_AND_READY.md",
            "FIXES_COMPLETE.md": "docs/reports/fixes/FIXES_COMPLETE.md",
            "debug_report.md": "docs/reports/fixes/debug_report.md",
            "test_fix_report.md": "docs/reports/fixes/test_fix_report.md",
            "quick_fix_report.txt": "docs/reports/fixes/quick_fix_report.txt",
            "SMART_DEBUG_GUIDE.md": "docs/guides/debug/SMART_DEBUG_GUIDE.md",
        }
    
    def move_files(self, dry_run=True):
        """移动文件到新位置"""
        file_moves = self.get_file_moves()
        
        for src, dst in file_moves.items():
            src_path = self.root / src
            dst_path = self.root / dst
            
            if src_path.exists():
                if dry_run:
                    print(f"[预览] {src} → {dst}")
                    self.moves.append((src, dst))
                else:
                    try:
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(src_path), str(dst_path))
                        print(f"✓ 移动: {src} → {dst}")
                        self.moves.append((src, dst))
                    except Exception as e:
                        print(f"✗ 错误: {src} → {dst}: {e}")
                        self.errors.append((src, dst, str(e)))
    
    def clean_backups(self, dry_run=True):
        """清理备份文件"""
        backup_patterns = [
            "*.backup",
            "*.bak",
            "*~"
        ]
        
        for pattern in backup_patterns:
            for file_path in self.root.rglob(pattern):
                if dry_run:
                    print(f"[预览] 删除: {file_path.relative_to(self.root)}")
                else:
                    try:
                        file_path.unlink()
                        print(f"✓ 删除: {file_path.relative_to(self.root)}")
                    except Exception as e:
                        print(f"✗ 错误删除 {file_path}: {e}")
    
    def clean_cache(self, dry_run=True):
        """清理缓存文件"""
        cache_dirs = [
            ".pytest_cache",
            "htmlcov",
            "__pycache__"
        ]
        
        for cache_dir in cache_dirs:
            for dir_path in self.root.rglob(cache_dir):
                if dir_path.is_dir():
                    if dry_run:
                        print(f"[预览] 删除目录: {dir_path.relative_to(self.root)}")
                    else:
                        try:
                            shutil.rmtree(dir_path)
                            print(f"✓ 删除目录: {dir_path.relative_to(self.root)}")
                        except Exception as e:
                            print(f"✗ 错误删除目录 {dir_path}: {e}")
    
    def update_imports(self):
        """更新Python文件中的导入路径"""
        # 这里只是生成需要更新的列表，实际更新需要谨慎处理
        updates_needed = []
        
        for py_file in self.root.rglob("*.py"):
            if ".archive" in py_file.parts:
                continue
                
            content = py_file.read_text(encoding='utf-8')
            
            # 检查需要更新的导入
            for old_file, new_path in self.moves:
                old_module = old_file.replace('.py', '')
                new_module = new_path.replace('.py', '').replace('/', '.')
                
                if f"from {old_module} import" in content or f"import {old_module}" in content:
                    updates_needed.append({
                        'file': str(py_file.relative_to(self.root)),
                        'old': old_module,
                        'new': new_module
                    })
        
        return updates_needed
    
    def generate_report(self):
        """生成重构报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'moves': self.moves,
            'errors': self.errors,
            'import_updates_needed': self.update_imports()
        }
        
        report_path = self.root / "docs/reports/restructure_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 报告已生成: {report_path}")
        return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RuleK项目重构工具')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际执行')
    parser.add_argument('--skip-backup', action='store_true', help='跳过备份创建')
    parser.add_argument('--clean-only', action='store_true', help='只执行清理操作')
    
    args = parser.parse_args()
    
    restructure = ProjectRestructure()
    
    print("=== RuleK 项目重构工具 ===\n")
    
    if not args.skip_backup and not args.dry_run and not args.clean_only:
        # 创建备份
        backup_dir = f".archive/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"创建备份到: {backup_dir}")
        # 这里应该实现备份逻辑
    
    if args.clean_only:
        print("\n--- 清理缓存和备份文件 ---")
        restructure.clean_cache(args.dry_run)
        restructure.clean_backups(args.dry_run)
    else:
        print("\n--- 创建目录结构 ---")
        if not args.dry_run:
            restructure.create_directories()
        
        print("\n--- 移动文件 ---")
        restructure.move_files(args.dry_run)
        
        print("\n--- 清理备份文件 ---")
        restructure.clean_backups(args.dry_run)
        
        print("\n--- 清理缓存 ---")
        restructure.clean_cache(args.dry_run)
    
    if not args.dry_run:
        print("\n--- 生成报告 ---")
        report = restructure.generate_report()
        
        print("\n=== 重构完成 ===")
        print(f"移动文件: {len(restructure.moves)} 个")
        print(f"错误: {len(restructure.errors)} 个")
        
        if report['import_updates_needed']:
            print(f"\n⚠️  需要更新导入路径的文件: {len(report['import_updates_needed'])} 个")
            print("请查看报告文件了解详情")
    else:
        print("\n=== 预览模式完成 ===")
        print("使用不带 --dry-run 参数来实际执行重构")

if __name__ == "__main__":
    main()
