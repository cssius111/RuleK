#!/usr/bin/env python3
"""
RuleK 项目管理工具
统一的项目管理入口
"""
import sys
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ProjectManager:
    """项目管理器"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = self.project_root / "scripts"
        
    def print_banner(self):
        """打印横幅"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║               RuleK - 规则怪谈管理者                        ║
║                   项目管理中心                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
    
    def print_menu(self):
        """打印菜单"""
        print("\n" + "=" * 60)
        print("📋 主菜单")
        print("=" * 60)
        print("1. 🚀 启动Web服务器")
        print("2. 🎮 启动CLI游戏")
        print("3. 🧪 运行测试")
        print("4. 🔧 诊断和修复")
        print("5. 📊 项目状态")
        print("6. 📚 查看文档")
        print("7. 🧹 清理项目")
        print("8. 💾 备份项目")
        print("0. 退出")
        print("=" * 60)
    
    def run_command(self, command: list, name: str = "命令") -> bool:
        """运行命令"""
        try:
            print(f"\n▶️ 运行 {name}...")
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"❌ {name}失败: {e}")
            return False
    
    def start_web_server(self):
        """启动Web服务器"""
        print("\n🚀 启动Web服务器")
        print("-" * 40)
        print("选择启动方式:")
        print("1. 仅后端 (API)")
        print("2. 仅前端 (Vue)")
        print("3. 前后端同时启动")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            self.run_command([sys.executable, "rulek.py", "web"], "后端服务器")
        elif choice == "2":
            self.run_command(["npm", "run", "dev"], "前端服务器")
        elif choice == "3":
            # 使用start_all.py脚本
            start_all = self.scripts_dir / "startup" / "start_all.py"
            if start_all.exists():
                self.run_command([sys.executable, str(start_all)], "全栈服务")
            else:
                print("❌ start_all.py 脚本不存在")
        elif choice == "0":
            return
    
    def start_cli_game(self):
        """启动CLI游戏"""
        print("\n🎮 启动CLI游戏")
        self.run_command([sys.executable, "rulek.py", "cli"], "CLI游戏")
    
    def run_tests(self):
        """运行测试"""
        print("\n🧪 测试菜单")
        print("-" * 40)
        print("1. 快速API测试")
        print("2. 综合API测试")
        print("3. 所有单元测试")
        print("4. AI功能测试")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        test_scripts = {
            "1": self.scripts_dir / "test" / "quick_api_test.py",
            "2": self.scripts_dir / "test" / "test_api_comprehensive.py",
            "3": "pytest",  # 特殊标记
            "4": self.scripts_dir / "test" / "test_ai_integration.py"
        }
        
        if choice in test_scripts:
            if choice == "3":
                self.run_command(["pytest", "tests/", "-v"], "单元测试")
            elif choice != "0":
                script = test_scripts[choice]
                if script.exists():
                    self.run_command([sys.executable, str(script)], f"测试脚本")
                else:
                    print(f"❌ 测试脚本不存在: {script}")
    
    def run_diagnostics(self):
        """运行诊断和修复"""
        print("\n🔧 诊断和修复")
        print("-" * 40)
        print("1. API诊断和修复")
        print("2. 前端诊断")
        print("3. 游戏核心诊断")
        print("4. 依赖检查")
        print("5. 全面诊断")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        scripts = {
            "1": self.scripts_dir / "fix" / "fix_api.py",
            "2": self.scripts_dir / "diagnostic" / "diagnose_frontend.py",
            "3": self.scripts_dir / "diagnostic" / "diagnose_game.py",
            "4": self.scripts_dir / "diagnostic" / "check_dependencies.py",
            "5": self.scripts_dir / "diagnostic" / "full_diagnostic.py"
        }
        
        if choice in scripts and choice != "0":
            script = scripts[choice]
            if script.exists():
                self.run_command([sys.executable, str(script)], "诊断脚本")
            else:
                print(f"⚠️ 脚本不存在: {script}")
                # 尝试运行基本诊断
                if choice == "4":
                    self.check_dependencies()
                elif choice == "5":
                    self.full_diagnostic()
    
    def check_dependencies(self):
        """检查依赖"""
        print("\n📦 检查依赖")
        print("-" * 40)
        
        # Python依赖
        print("Python依赖:")
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                deps = [line.strip().split('==')[0] for line in f if line.strip() and not line.startswith('#')]
            
            missing = []
            for dep in deps:
                try:
                    __import__(dep.replace('-', '_'))
                    print(f"  ✅ {dep}")
                except ImportError:
                    print(f"  ❌ {dep} (未安装)")
                    missing.append(dep)
            
            if missing:
                print(f"\n缺少 {len(missing)} 个依赖包")
                install = input("是否安装? (y/n): ").strip().lower()
                if install == 'y':
                    self.run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], "安装依赖")
        
        # Node依赖
        print("\nNode依赖:")
        package_json = self.project_root / "web" / "frontend" / "package.json"
        if package_json.exists():
            node_modules = self.project_root / "web" / "frontend" / "node_modules"
            if node_modules.exists():
                print("  ✅ node_modules 存在")
            else:
                print("  ❌ node_modules 不存在")
                install = input("是否安装? (y/n): ").strip().lower()
                if install == 'y':
                    os.chdir(self.project_root / "web" / "frontend")
                    self.run_command(["npm", "install"], "安装Node依赖")
                    os.chdir(self.project_root)
    
    def show_project_status(self):
        """显示项目状态"""
        print("\n📊 项目状态")
        print("=" * 60)
        
        # 基本信息
        print("📁 项目路径:", self.project_root)
        print("📅 当前时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # 文件统计
        print("\n📈 文件统计:")
        py_files = list(self.project_root.rglob("*.py"))
        js_files = list(self.project_root.rglob("*.js"))
        vue_files = list(self.project_root.rglob("*.vue"))
        
        print(f"  Python文件: {len(py_files)}")
        print(f"  JavaScript文件: {len(js_files)}")
        print(f"  Vue文件: {len(vue_files)}")
        
        # 目录大小
        def get_dir_size(path):
            total = 0
            for entry in Path(path).rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
            return total / (1024 * 1024)  # MB
        
        print("\n💾 目录大小:")
        dirs = ["src", "web", "tests", "docs", "data"]
        for dir_name in dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                size = get_dir_size(dir_path)
                print(f"  {dir_name:10s}: {size:6.2f} MB")
        
        # 服务状态
        print("\n🔌 服务状态:")
        import socket
        
        # 检查后端
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            backend_running = s.connect_ex(('localhost', 8000)) == 0
        print(f"  后端 (8000): {'✅ 运行中' if backend_running else '⭕ 未运行'}")
        
        # 检查前端
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            frontend_running = s.connect_ex(('localhost', 5173)) == 0
        print(f"  前端 (5173): {'✅ 运行中' if frontend_running else '⭕ 未运行'}")
        
        print("=" * 60)
    
    def view_docs(self):
        """查看文档"""
        print("\n📚 文档菜单")
        print("-" * 40)
        
        docs_dir = self.project_root / "docs"
        doc_files = [
            ("README.md", "项目说明"),
            ("PROJECT_STRUCTURE.md", "项目结构"),
            ("PROJECT_PLAN.md", "项目计划"),
            ("AGENT.md", "AI协作指南"),
            ("MAIN_AGENT.md", "主Agent规则")
        ]
        
        for i, (filename, desc) in enumerate(doc_files, 1):
            file_path = self.project_root / filename
            if not file_path.exists():
                file_path = docs_dir / filename
            exists = "✅" if file_path.exists() else "❌"
            print(f"{i}. {exists} {desc} ({filename})")
        
        print("0. 返回")
        
        choice = input("\n请选择查看的文档: ").strip()
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(doc_files):
                filename, _ = doc_files[index]
                file_path = self.project_root / filename
                if not file_path.exists():
                    file_path = docs_dir / filename
                
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 分页显示
                    lines = content.split('\n')
                    page_size = 30
                    for i in range(0, len(lines), page_size):
                        print('\n'.join(lines[i:i+page_size]))
                        if i + page_size < len(lines):
                            input("\n--- 按Enter继续 ---")
                else:
                    print(f"❌ 文档不存在: {filename}")
        except (ValueError, IndexError):
            pass
    
    def clean_project(self):
        """清理项目"""
        print("\n🧹 清理项目")
        print("-" * 40)
        print("将清理以下内容:")
        print("- __pycache__ 目录")
        print("- .pyc 文件")
        print("- .pytest_cache")
        print("- 临时文件")
        
        confirm = input("\n确认清理? (y/n): ").strip().lower()
        if confirm != 'y':
            return
        
        # 清理Python缓存
        cleaned = 0
        for cache_dir in self.project_root.rglob("__pycache__"):
            import shutil
            shutil.rmtree(cache_dir)
            cleaned += 1
        
        for pyc_file in self.project_root.rglob("*.pyc"):
            pyc_file.unlink()
            cleaned += 1
        
        # 清理pytest缓存
        pytest_cache = self.project_root / ".pytest_cache"
        if pytest_cache.exists():
            import shutil
            shutil.rmtree(pytest_cache)
            cleaned += 1
        
        print(f"✅ 清理完成，删除了 {cleaned} 个文件/目录")
    
    def backup_project(self):
        """备份项目"""
        print("\n💾 备份项目")
        print("-" * 40)
        
        backup_dir = self.project_root / ".backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"rulek_backup_{timestamp}.tar.gz"
        backup_path = backup_dir / backup_name
        
        print(f"创建备份: {backup_name}")
        
        # 创建tar.gz备份
        import tarfile
        
        exclude_patterns = [
            "__pycache__",
            "*.pyc",
            "node_modules",
            ".git",
            ".pytest_cache",
            ".backups"
        ]
        
        def filter_func(tarinfo):
            for pattern in exclude_patterns:
                if pattern in tarinfo.name:
                    return None
            return tarinfo
        
        try:
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(self.project_root, arcname="RuleK", filter=filter_func)
            
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            print(f"✅ 备份成功: {backup_name} ({size_mb:.2f} MB)")
            
            # 清理旧备份（保留最近5个）
            backups = sorted(backup_dir.glob("rulek_backup_*.tar.gz"))
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    old_backup.unlink()
                    print(f"删除旧备份: {old_backup.name}")
                    
        except Exception as e:
            print(f"❌ 备份失败: {e}")
    
    def full_diagnostic(self):
        """全面诊断"""
        print("\n🔍 全面诊断")
        print("=" * 60)
        
        issues = []
        
        # 1. 检查核心文件
        print("检查核心文件...")
        core_files = [
            "rulek.py",
            "requirements.txt",
            "README.md",
            "web/backend/app.py",
            "src/core/game_state.py"
        ]
        
        for file in core_files:
            file_path = self.project_root / file
            if file_path.exists():
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file}")
                issues.append(f"缺少文件: {file}")
        
        # 2. 检查Python版本
        print("\nPython版本:")
        import sys
        py_version = sys.version_info
        if py_version >= (3, 10):
            print(f"  ✅ Python {py_version.major}.{py_version.minor}.{py_version.micro}")
        else:
            print(f"  ❌ Python {py_version.major}.{py_version.minor}.{py_version.micro} (需要3.10+)")
            issues.append("Python版本过低")
        
        # 3. 检查Node版本
        print("\nNode版本:")
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            node_version = result.stdout.strip()
            print(f"  ✅ Node {node_version}")
        except:
            print(f"  ❌ Node未安装")
            issues.append("Node.js未安装")
        
        # 总结
        print("\n" + "=" * 60)
        if issues:
            print(f"⚠️ 发现 {len(issues)} 个问题:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ 诊断完成，未发现问题！")
        print("=" * 60)
    
    def run(self):
        """运行管理器"""
        self.print_banner()
        
        while True:
            self.print_menu()
            choice = input("\n请选择操作 (0-8): ").strip()
            
            if choice == "1":
                self.start_web_server()
            elif choice == "2":
                self.start_cli_game()
            elif choice == "3":
                self.run_tests()
            elif choice == "4":
                self.run_diagnostics()
            elif choice == "5":
                self.show_project_status()
            elif choice == "6":
                self.view_docs()
            elif choice == "7":
                self.clean_project()
            elif choice == "8":
                self.backup_project()
            elif choice == "0":
                print("\n👋 再见！")
                break
            else:
                print("❌ 无效选择，请重试")
            
            input("\n按Enter继续...")


def main():
    """主函数"""
    manager = ProjectManager()
    try:
        manager.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ 程序被中断")
        sys.exit(0)


if __name__ == "__main__":
    main()
