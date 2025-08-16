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
            "restructure_project.py": "scripts/restructure.py",
            
            # 文档 -> docs/
            "*_COMPLETE.md": "docs/archive/",
            "*_REPORT.md": "docs/reports/",
            "*_GUIDE.md": "docs/guides/",
            "*_PLAN.md": "docs/plans/",
            "AGENTS.md": "docs/AGENTS.md",
            "CONTRIBUTING.md": "docs/CONTRIBUTING.md",
            
            # 部署文件 -> deploy/
            "Dockerfile": "deploy/docker/Dockerfile",
            "docker-compose.yml": "deploy/docker/docker-compose.yml",
            "nginx.conf": "deploy/nginx/nginx.conf",
            
            # 启动脚本 -> scripts/
            "start.sh": "scripts/start.sh",
            "start.bat": "scripts/start.bat",
            "start_enhanced.sh": "scripts/start_enhanced.sh",
        }
        
        # 需要创建的目录结构
        self.required_dirs = [
            "rulek",
            "rulek/core",
            "rulek/ai",
            "rulek/api",
            "rulek/cli",
            "rulek/web",
            "rulek/web/backend",
            "rulek/web/frontend",
            "tests",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "docs",
            "docs/api",
            "docs/guides",
            "docs/development",
            "docs/archive",
            "docs/reports",
            "docs/plans",
            "scripts",
            "deploy",
            "deploy/docker",
            "deploy/kubernetes",
            "deploy/nginx",
            ".github",
            ".github/workflows",
            ".github/ISSUE_TEMPLATE",
        ]
        
        # 需要删除的文件模式
        self.delete_patterns = [
            "*.backup",
            "*.pyc",
            "*.pyo",
            ".DS_Store",
            "*~",
            "go.py",
            "run.py",
            "check.py",
            "play.py",
            "play_cli.py",
        ]
        
        # 根目录保留的文件
        self.root_keep = [
            "README.md",
            "LICENSE",
            "requirements.txt",
            "requirements-dev.txt",
            ".env",
            ".env.example",
            ".gitignore",
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "Makefile",
            "rulek.py",  # 临时保留，后续移到rulek/__main__.py
            "start_web_server.py",  # 临时保留，后续整合
            "PROJECT_PLAN.md",
            "AGENT.md",
        ]
    
    def backup_file(self, file_path: Path) -> None:
        """备份文件或目录
        
        Args:
            file_path: 要备份的文件或目录路径
        """
        if not file_path.exists():
            return
            
        backup_path = self.backup_dir / file_path.relative_to(self.root)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.is_file():
            shutil.copy2(file_path, backup_path)
        elif file_path.is_dir():
            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.copytree(file_path, backup_path)
    
    def create_directories(self) -> None:
        """创建必要的目录结构"""
        print("📁 创建目录结构...")
        for dir_path in self.required_dirs:
            full_path = self.root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                self.stats["dirs_created"] += 1
                print(f"  ✅ 创建: {dir_path}")
    
    def move_source_files(self) -> None:
        """移动源代码文件到rulek包"""
        print("📦 整理源代码...")
        
        # 移动src目录内容到rulek
        src_dir = self.root / "src"
        if src_dir.exists():
            for item in src_dir.iterdir():
                if item.is_file() and item.suffix == ".py":
                    dest = self.root / "rulek" / item.name
                    self.backup_file(item)
                    shutil.move(str(item), str(dest))
                    self.stats["files_moved"] += 1
                    print(f"  ➡️  {item.name} -> rulek/{item.name}")
                elif item.is_dir():
                    # 跳过特殊目录
                    if item.name in ['__pycache__', '.pytest_cache']:
                        continue
                        
                    dest = self.root / "rulek" / item.name
                    if not dest.exists():
                        self.backup_file(item)
                        shutil.move(str(item), str(dest))
                        self.stats["files_moved"] += 1
                        print(f"  ➡️  {item.name}/ -> rulek/{item.name}/")
    
    def clean_root_directory(self) -> None:
        """清理根目录"""
        print("🧹 清理根目录...")
        
        for file_path in self.root.iterdir():
            if file_path.is_file():
                file_name = file_path.name
                
                # 检查是否应该保留
                if file_name in self.root_keep:
                    continue
                
                # 检查是否匹配移动规则
                moved = False
                for pattern, dest in self.move_rules.items():
                    if self._match_pattern(file_name, pattern):
                        if dest == "archive":
                            # 归档文件
                            self.backup_file(file_path)
                            file_path.unlink()
                            self.stats["files_deleted"] += 1
                            print(f"  🗄️  归档: {file_name}")
                        else:
                            # 移动文件
                            dest_path = self.root / dest
                            if dest.endswith('/'):
                                dest_path = dest_path / file_name
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            self.backup_file(file_path)
                            shutil.move(str(file_path), str(dest_path))
                            self.stats["files_moved"] += 1
                            print(f"  ➡️  {file_name} -> {dest}")
                        moved = True
                        break
                
                # 检查是否应该删除
                if not moved:
                    for pattern in self.delete_patterns:
                        if self._match_pattern(file_name, pattern):
                            self.backup_file(file_path)
                            file_path.unlink()
                            self.stats["files_deleted"] += 1
                            print(f"  🗑️  删除: {file_name}")
                            break
    
    def create_package_files(self) -> None:
        """创建Python包必需的文件"""
        print("📝 创建包文件...")
        
        # 创建 rulek/__init__.py
        init_file = self.root / "rulek" / "__init__.py"
        if not init_file.exists():
            init_content = '''"""
RuleK - 规则怪谈管理者
A horror survival game based on rule triggers.
"""

__version__ = "0.3.0-alpha"
__author__ = "RuleK Team"

from rulek.core import GameEngine
from rulek.cli import CLIGame

__all__ = ["GameEngine", "CLIGame", "__version__"]
'''
            init_file.write_text(init_content)
            print("  ✅ 创建: rulek/__init__.py")
        
        # 创建 rulek/__main__.py
        main_file = self.root / "rulek" / "__main__.py"
        if not main_file.exists():
            main_content = '''#!/usr/bin/env python3
"""
RuleK 统一入口点
使用: python -m rulek [command] [options]
"""

import sys
import argparse
from pathlib import Path

def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        prog="rulek",
        description="RuleK - 规则怪谈管理者"
    )
    
    parser.add_argument(
        "command",
        choices=["serve", "play", "test", "demo", "clean", "docs"],
        help="要执行的命令"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="服务器主机地址 (默认: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器端口 (默认: 8000)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    args = parser.parse_args()
    
    if args.command == "serve":
        from rulek.web import start_server
        start_server(host=args.host, port=args.port, debug=args.debug)
    
    elif args.command == "play":
        from rulek.cli import CLIGame
        game = CLIGame()
        game.run()
    
    elif args.command == "test":
        import pytest
        sys.exit(pytest.main(["-v", "tests/"]))
    
    elif args.command == "demo":
        print("🎭 演示模式尚未实现")
    
    elif args.command == "clean":
        from rulek.utils import clean_project
        clean_project()
    
    elif args.command == "docs":
        print("📚 文档生成功能尚未实现")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
'''
            main_file.write_text(main_content)
            print("  ✅ 创建: rulek/__main__.py")
        
        # 创建 setup.py
        setup_file = self.root / "setup.py"
        if not setup_file.exists():
            setup_content = '''"""
RuleK 安装配置
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rulek",
    version="0.3.0-alpha",
    author="RuleK Team",
    description="A horror survival game based on rule triggers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rulek",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rulek=rulek.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "rulek": ["data/*.json", "web/frontend/dist/**/*"],
    },
)
'''
            setup_file.write_text(setup_content)
            print("  ✅ 创建: setup.py")
    
    def clean_cache_files(self) -> None:
        """清理缓存文件"""
        print("🗑️  清理缓存...")
        
        cache_patterns = [
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "htmlcov",
            ".coverage",
            "*.egg-info",
        ]
        
        for pattern in cache_patterns:
            for path in self.root.rglob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                self.stats["files_deleted"] += 1
                print(f"  🗑️  删除: {path.relative_to(self.root)}")
    
    def update_imports(self) -> None:
        """更新Python文件中的导入路径"""
        print("🔄 更新导入路径...")
        
        # 需要更新的导入映射
        import_map = {
            "from src.": "from rulek.",
            "import src.": "import rulek.",
            "from play_cli": "from rulek.cli",
            "from cli_game": "from rulek.cli.game",
        }
        
        # 遍历所有Python文件
        for py_file in self.root.rglob("*.py"):
            if ".backups" in str(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding="utf-8")
                original_content = content
                
                for old_import, new_import in import_map.items():
                    content = content.replace(old_import, new_import)
                
                if content != original_content:
                    self.backup_file(py_file)
                    py_file.write_text(content, encoding="utf-8")
                    print(f"  ✏️  更新: {py_file.relative_to(self.root)}")
            except Exception as e:
                self.stats["errors"].append(f"更新导入失败 {py_file}: {e}")
    
    def generate_report(self) -> None:
        """生成重构报告"""
        report_path = self.root / "RESTRUCTURE_REPORT.md"
        
        report = f"""# 项目重构报告

## 📅 执行时间
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 统计信息
- 创建目录: {self.stats['dirs_created']} 个
- 移动文件: {self.stats['files_moved']} 个
- 删除文件: {self.stats['files_deleted']} 个
- 错误数量: {len(self.stats['errors'])} 个

## 🗂️ 备份位置
{self.backup_dir}

## ⚠️ 错误列表
"""
        
        if self.stats["errors"]:
            for error in self.stats["errors"]:
                report += f"- {error}\n"
        else:
            report += "无错误\n"
        
        report += """
## ✅ 下一步操作

1. 检查项目结构是否正确
2. 运行 `make test` 验证功能
3. 提交更改到版本控制
4. 删除备份文件夹（确认无误后）

---
*此报告由重构脚本自动生成*
"""
        
        report_path.write_text(report)
        print(f"\n📄 重构报告已生成: {report_path}")
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """检查文件名是否匹配模式
        
        Args:
            filename: 文件名
            pattern: 匹配模式（支持*通配符）
            
        Returns:
            是否匹配
        """
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def run(self, dry_run: bool = False) -> None:
        """执行重构
        
        Args:
            dry_run: 是否只预览不执行
        """
        print("=" * 60)
        print("🔧 RuleK 项目结构重构工具")
        print("=" * 60)
        
        if dry_run:
            print("⚠️  预览模式 - 不会实际修改文件")
            print("=" * 60)
        
        try:
            # 1. 创建备份目录
            if not dry_run:
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                print(f"📁 备份目录: {self.backup_dir}\n")
            
            # 2. 创建目录结构
            self.create_directories()
            print()
            
            # 3. 移动源代码
            self.move_source_files()
            print()
            
            # 4. 清理根目录
            self.clean_root_directory()
            print()
            
            # 5. 创建包文件
            if not dry_run:
                self.create_package_files()
                print()
            
            # 6. 清理缓存
            self.clean_cache_files()
            print()
            
            # 7. 更新导入
            if not dry_run:
                self.update_imports()
                print()
            
            # 8. 生成报告
            if not dry_run:
                self.generate_report()
            
            print("=" * 60)
            print("✅ 重构完成！")
            print(f"📊 统计: 移动 {self.stats['files_moved']} 个文件, "
                  f"删除 {self.stats['files_deleted']} 个文件, "
                  f"创建 {self.stats['dirs_created']} 个目录")
            
            if self.stats["errors"]:
                print(f"⚠️  发生 {len(self.stats['errors'])} 个错误，请查看报告")
            
        except Exception as e:
            print(f"❌ 重构失败: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RuleK 项目结构重构工具")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式，不实际修改文件"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="项目根目录路径"
    )
    
    args = parser.parse_args()
    
    restructure = ProjectRestructure(args.path)
    restructure.run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
