#!/usr/bin/env python3
"""
RuleK 统一入口程序
根据MAIN_AGENT规则设计的项目统一管理入口

Usage:
    python rulek.py              # 显示交互式菜单
    python rulek.py <command>    # 执行指定命令
    python rulek.py help         # 显示帮助信息
"""
import sys
import os
import subprocess
import time
import signal
from pathlib import Path
from typing import List, Optional, Dict, Callable

from src.utils.logger import setup_logging

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 全局进程列表，用于清理
active_processes = []


class Colors:
    """终端颜色"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    WHITE = '\033[0;37m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """打印项目横幅"""
    print(f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════╗
║              🎮 RuleK - 规则怪谈管理者 🎮              ║
║                    统一管理入口 v2.0                     ║
╚══════════════════════════════════════════════════════════╝
{Colors.RESET}""")


def print_menu():
    """显示交互式菜单"""
    menu_items = [
        ("1", "🎮 启动完整游戏", "前端+后端"),
        ("2", "🔧 启动Web API", "仅后端服务"),
        ("3", "🎨 启动前端界面", "仅前端服务"),
        ("4", "💻 启动CLI游戏", "命令行版本"),
        ("-", "-" * 40, ""),
        ("5", "🧪 运行测试", "完整测试套件"),
        ("6", "🔍 诊断系统", "检查环境和依赖"),
        ("7", "🔧 修复问题", "自动修复常见问题"),
        ("8", "🧹 清理项目", "清理缓存和临时文件"),
        ("-", "-" * 40, ""),
        ("9", "📚 查看文档", "项目文档"),
        ("0", "📊 项目状态", "查看项目信息"),
        ("-", "-" * 40, ""),
        ("h", "❓ 帮助", "命令行帮助"),
        ("q", "👋 退出", "退出程序"),
    ]
    
    print(f"\n{Colors.BOLD}请选择操作:{Colors.RESET}\n")
    for key, name, desc in menu_items:
        if key == "-":
            print(f"  {name}")
        else:
            print(f"  {Colors.CYAN}[{key}]{Colors.RESET} {name:<20} {Colors.YELLOW}{desc}{Colors.RESET}")
    print()


def show_help():
    """显示命令行帮助"""
    print(f"""
{Colors.BOLD}命令行使用方法:{Colors.RESET}
    python rulek.py [command] [options]

{Colors.BOLD}可用命令:{Colors.RESET}
    {Colors.CYAN}start{Colors.RESET}       - 启动完整游戏（前端+后端）
    {Colors.CYAN}web{Colors.RESET}         - 启动Web API服务器
    {Colors.CYAN}frontend{Colors.RESET}    - 启动前端开发服务器
    {Colors.CYAN}cli{Colors.RESET}         - 启动命令行游戏
    {Colors.CYAN}test{Colors.RESET}        - 运行测试套件
    {Colors.CYAN}diagnose{Colors.RESET}    - 诊断系统问题
    {Colors.CYAN}fix{Colors.RESET}         - 修复常见问题
    {Colors.CYAN}clean{Colors.RESET}       - 清理项目
    {Colors.CYAN}docs{Colors.RESET}        - 查看文档
    {Colors.CYAN}status{Colors.RESET}      - 查看项目状态
    {Colors.CYAN}help{Colors.RESET}        - 显示此帮助

{Colors.BOLD}快速启动示例:{Colors.RESET}
    python rulek.py start       # 启动完整游戏
    python rulek.py web         # 仅启动后端
    python rulek.py test        # 运行测试

{Colors.BOLD}环境变量:{Colors.RESET}
    RULEK_ENV    - 运行环境 (development/production)
    RULEK_PORT   - API端口 (默认: 8000)
    RULEK_DEBUG  - 调试模式 (true/false)
""")


def start_full_game():
    """启动完整游戏（前端+后端）"""
    print(f"\n{Colors.GREEN}🎮 启动完整游戏...{Colors.RESET}")
    
    # 启动后端
    print(f"\n{Colors.CYAN}1. 启动后端服务...{Colors.RESET}")
    backend_process = start_backend(standalone=False)
    if backend_process:
        active_processes.append(backend_process)
        time.sleep(3)  # 等待后端启动
    
    # 启动前端
    print(f"\n{Colors.CYAN}2. 启动前端界面...{Colors.RESET}")
    frontend_process = start_frontend(standalone=False)
    if frontend_process:
        active_processes.append(frontend_process)
    
    # 显示访问信息
    print(f"""
{Colors.GREEN}{'='*50}
✨ 游戏启动成功！

  🎮 游戏界面: {Colors.CYAN}http://localhost:5173{Colors.RESET}
  📊 API文档:  {Colors.CYAN}http://localhost:8000/docs{Colors.RESET}
  🔧 API端点:  {Colors.CYAN}http://localhost:8000{Colors.RESET}

  按 {Colors.YELLOW}Ctrl+C{Colors.RESET} 停止所有服务
{'='*50}{Colors.RESET}
""")
    
    # 等待进程
    try:
        for process in active_processes:
            process.wait()
    except KeyboardInterrupt:
        cleanup_processes()


def start_backend(standalone=True):
    """启动后端服务"""
    if standalone:
        print(f"\n{Colors.GREEN}🔧 启动Web API服务器...{Colors.RESET}")
    
    os.chdir(PROJECT_ROOT)
    
    try:
        # 检查依赖
        import uvicorn
        import fastapi
        
        # 启动服务
        if standalone:
            print(f"   地址: {Colors.CYAN}http://localhost:8000{Colors.RESET}")
            print(f"   文档: {Colors.CYAN}http://localhost:8000/docs{Colors.RESET}")
            print(f"   按 {Colors.YELLOW}Ctrl+C{Colors.RESET} 停止")
            print("-" * 50)
            
            uvicorn.run(
                "web.backend.app:app",
                host="0.0.0.0",
                port=8000,
                reload=True,
                log_level="info"
            )
        else:
            # 作为子进程启动
            cmd = [sys.executable, "-m", "uvicorn", "web.backend.app:app", 
                   "--host", "0.0.0.0", "--port", "8000", "--reload"]
            process = subprocess.Popen(cmd, cwd=PROJECT_ROOT)
            print(f"   ✅ 后端已启动 (PID: {process.pid})")
            return process
            
    except ImportError as e:
        print(f"{Colors.RED}❌ 缺少依赖: {e}{Colors.RESET}")
        print(f"   请运行: pip install -r requirements.txt")
        if not standalone:
            return None
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}✅ 服务器已停止{Colors.RESET}")


def start_frontend(standalone: bool = True) -> Optional[subprocess.Popen]:
    """启动前端服务"""
    if standalone:
        print(f"\n{Colors.GREEN}🎨 启动前端界面...{Colors.RESET}")

    frontend_dir = PROJECT_ROOT / "web" / "frontend"
    
    if not frontend_dir.exists():
        print(f"{Colors.RED}❌ 前端目录不存在{Colors.RESET}")
        return None
    
    # 检查Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError()
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Node.js未安装{Colors.RESET}")
        print("   请访问: https://nodejs.org/")
        return None
    
    # 检查依赖
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print(f"{Colors.YELLOW}📦 安装前端依赖...{Colors.RESET}")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError:
            print(f"{Colors.RED}❌ 前端依赖安装失败{Colors.RESET}")
            print("   请检查 npm 配置或网络连接")
            return None
    
    # 启动前端
    if standalone:
        print(f"   地址: {Colors.CYAN}http://localhost:5173{Colors.RESET}")
        print(f"   按 {Colors.YELLOW}Ctrl+C{Colors.RESET} 停止")
        print("-" * 50)
        try:
            subprocess.run(["npm", "run", "dev"], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError:
            print(f"{Colors.RED}❌ 前端启动失败{Colors.RESET}")
            print("   请检查 npm 配置或源码是否存在错误")
            return None
    else:
        cmd = ["npm", "run", "dev"]
        try:
            process = subprocess.Popen(cmd, cwd=frontend_dir)
        except Exception as e:  # pragma: no cover - 捕获所有子进程异常
            print(f"{Colors.RED}❌ 前端启动失败: {e}{Colors.RESET}")
            return None
        print(f"   ✅ 前端已启动 (PID: {process.pid})")
        return process


def start_cli() -> None:
    """启动CLI游戏"""
    print(f"\n{Colors.GREEN}💻 启动命令行游戏...{Colors.RESET}")
    print("-" * 50)

    try:
        import asyncio
        from src.cli_game import main as cli_main
        asyncio.run(cli_main())
    except ImportError as e:
        # 尝试其他路径
        try:
            cli_script = PROJECT_ROOT / "scripts" / "dev" / "play_cli.py"
            if cli_script.exists():
                subprocess.run([sys.executable, str(cli_script)])
            else:
                print(f"{Colors.RED}❌ 无法找到CLI游戏: {e}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ 启动失败: {e}{Colors.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}👋 游戏已退出{Colors.RESET}")


def run_tests():
    """运行测试套件"""
    print(f"\n{Colors.GREEN}🧪 运行测试套件...{Colors.RESET}")
    print("-" * 50)
    
    try:
        import pytest
        pytest.main(["-v", "tests/", "--tb=short"])
    except ImportError:
        print(f"{Colors.RED}❌ pytest未安装{Colors.RESET}")
        print("   请运行: pip install pytest")
        sys.exit(1)


def diagnose_system():
    """诊断系统"""
    print(f"\n{Colors.GREEN}🔍 系统诊断...{Colors.RESET}")
    print("-" * 50)
    
    checks = [
        ("Python版本", check_python_version),
        ("Node.js", check_nodejs),
        ("Python依赖", check_python_deps),
        ("前端依赖", check_frontend_deps),
        ("端口状态", check_ports),
        ("项目结构", check_project_structure),
    ]
    
    all_pass = True
    for name, check_func in checks:
        print(f"\n检查 {name}...")
        result = check_func()
        if not result:
            all_pass = False
    
    if all_pass:
        print(f"\n{Colors.GREEN}✅ 所有检查通过！{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}⚠️ 发现一些问题，运行 'python rulek.py fix' 尝试修复{Colors.RESET}")


def fix_issues():
    """修复常见问题"""
    print(f"\n{Colors.GREEN}🔧 修复常见问题...{Colors.RESET}")
    print("-" * 50)
    
    # 运行修复脚本
    fix_script = PROJECT_ROOT / "scripts" / "fix" / "final_fix_and_test.sh"
    if fix_script.exists():
        subprocess.run(["bash", str(fix_script)])
    else:
        print(f"{Colors.YELLOW}修复脚本不存在，尝试基本修复...{Colors.RESET}")
        
        # 基本修复
        print("\n1. 安装Python依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("\n2. 安装前端依赖...")
        frontend_dir = PROJECT_ROOT / "web" / "frontend"
        if frontend_dir.exists():
            subprocess.run(["npm", "install"], cwd=frontend_dir)
        
        print(f"\n{Colors.GREEN}✅ 基本修复完成{Colors.RESET}")


def clean_project():
    """清理项目"""
    print(f"\n{Colors.GREEN}🧹 清理项目...{Colors.RESET}")
    print("-" * 50)
    
    # 清理Python缓存
    print("\n清理Python缓存...")
    for pattern in ["**/__pycache__", "**/*.pyc", "**/.pytest_cache"]:
        for path in PROJECT_ROOT.glob(pattern):
            if path.is_dir():
                import shutil
                shutil.rmtree(path)
            else:
                path.unlink()
    
    # 清理日志
    print("清理日志文件...")
    logs_dir = PROJECT_ROOT / "logs"
    if logs_dir.exists():
        for log_file in logs_dir.glob("*.log"):
            log_file.unlink()
    
    print(f"{Colors.GREEN}✅ 清理完成{Colors.RESET}")


def show_docs():
    """显示文档"""
    print(f"\n{Colors.GREEN}📚 项目文档{Colors.RESET}")
    print("-" * 50)
    
    docs = [
        ("README.md", "项目说明"),
        ("PROJECT_PLAN.md", "项目计划"),
        ("MAIN_AGENT.md", "开发规范"),
        ("PROJECT_STRUCTURE.md", "项目结构"),
    ]
    
    for filename, desc in docs:
        doc_path = PROJECT_ROOT / filename
        if doc_path.exists():
            print(f"\n{Colors.CYAN}{desc} ({filename}):{Colors.RESET}")
            with open(doc_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]  # 显示前10行
                for line in lines:
                    print(f"  {line.rstrip()}")
            print(f"  {Colors.YELLOW}...（查看完整文档: cat {filename}）{Colors.RESET}")


def show_status():
    """显示项目状态"""
    print(f"\n{Colors.GREEN}📊 项目状态{Colors.RESET}")
    print("-" * 50)
    
    # 基本信息
    print(f"\n项目路径: {PROJECT_ROOT}")
    
    # 检查服务状态
    print(f"\n服务状态:")
    
    # 检查后端
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=1)
        if response.status_code == 200:
            print(f"  后端: {Colors.GREEN}运行中{Colors.RESET} (http://localhost:8000)")
        else:
            print(f"  后端: {Colors.YELLOW}异常{Colors.RESET}")
    except:
        print(f"  后端: {Colors.RED}未运行{Colors.RESET}")
    
    # 检查前端
    try:
        import requests
        response = requests.get("http://localhost:5173", timeout=1)
        print(f"  前端: {Colors.GREEN}运行中{Colors.RESET} (http://localhost:5173)")
    except:
        print(f"  前端: {Colors.RED}未运行{Colors.RESET}")
    
    # 统计信息
    print(f"\n项目统计:")
    py_files = len(list(PROJECT_ROOT.glob("**/*.py")))
    js_files = len(list(PROJECT_ROOT.glob("**/*.js"))) + len(list(PROJECT_ROOT.glob("**/*.ts")))
    print(f"  Python文件: {py_files}")
    print(f"  JS/TS文件: {js_files}")


# 辅助函数
def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"  {Colors.GREEN}✓{Colors.RESET} Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  {Colors.RED}✗{Colors.RESET} Python版本过低 (需要3.10+)")
        return False

def check_nodejs():
    """检查Node.js"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"  {Colors.GREEN}✓{Colors.RESET} Node.js {version}")
        return True
    except:
        print(f"  {Colors.RED}✗{Colors.RESET} Node.js未安装")
        return False

def check_python_deps():
    """检查Python依赖"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print(f"  {Colors.GREEN}✓{Colors.RESET} 核心依赖已安装")
        return True
    except ImportError as e:
        print(f"  {Colors.RED}✗{Colors.RESET} 缺少依赖: {e}")
        return False

def check_frontend_deps():
    """检查前端依赖"""
    node_modules = PROJECT_ROOT / "web" / "frontend" / "node_modules"
    if node_modules.exists():
        print(f"  {Colors.GREEN}✓{Colors.RESET} 前端依赖已安装")
        return True
    else:
        print(f"  {Colors.YELLOW}⚠{Colors.RESET} 前端依赖未安装")
        return False

def check_ports():
    """检查端口状态"""
    import socket
    
    ports = [(8000, "后端"), (5173, "前端")]
    all_free = True
    
    for port, name in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"  {Colors.YELLOW}⚠{Colors.RESET} 端口 {port} ({name}) 已被占用")
            all_free = False
        else:
            print(f"  {Colors.GREEN}✓{Colors.RESET} 端口 {port} ({name}) 可用")
    
    return all_free

def check_project_structure():
    """检查项目结构"""
    required_dirs = ["src", "web", "tests", "scripts", "docs"]
    all_exist = True
    
    for dir_name in required_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists():
            print(f"  {Colors.GREEN}✓{Colors.RESET} {dir_name}/")
        else:
            print(f"  {Colors.RED}✗{Colors.RESET} {dir_name}/ 缺失")
            all_exist = False
    
    return all_exist

def cleanup_processes():
    """清理所有启动的进程"""
    print(f"\n{Colors.YELLOW}🛑 正在停止所有服务...{Colors.RESET}")
    for process in active_processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            try:
                process.kill()
            except:
                pass
    print(f"{Colors.GREEN}✅ 所有服务已停止{Colors.RESET}")

def handle_signal(signum, frame):
    """处理信号"""
    cleanup_processes()
    sys.exit(0)

# 注册信号处理
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def main():
    """主函数"""
    logger = setup_logging()
    logger.info("RuleK unified entry started")

    # 命令映射
    commands = {
        "start": start_full_game,
        "web": start_backend,
        "backend": start_backend,
        "frontend": start_frontend,
        "cli": start_cli,
        "test": run_tests,
        "diagnose": diagnose_system,
        "fix": fix_issues,
        "clean": clean_project,
        "docs": show_docs,
        "status": show_status,
        "help": show_help,
    }
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command in commands:
            try:
                commands[command]()
            except KeyboardInterrupt:
                cleanup_processes()
                print(f"\n{Colors.GREEN}👋 再见！{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ 未知命令: {command}{Colors.RESET}")
            show_help()
            sys.exit(1)
    else:
        # 交互式菜单
        print_banner()
        
        while True:
            print_menu()
            try:
                choice = input(f"{Colors.CYAN}请选择 > {Colors.RESET}").strip().lower()
                
                menu_actions = {
                    "1": start_full_game,
                    "2": start_backend,
                    "3": start_frontend,
                    "4": start_cli,
                    "5": run_tests,
                    "6": diagnose_system,
                    "7": fix_issues,
                    "8": clean_project,
                    "9": show_docs,
                    "0": show_status,
                    "h": show_help,
                    "q": lambda: sys.exit(0),
                }
                
                if choice in menu_actions:
                    if choice == "q":
                        cleanup_processes()
                        print(f"{Colors.GREEN}👋 再见！{Colors.RESET}")
                        break
                    menu_actions[choice]()
                    if choice in ["1", "2", "3", "4"]:
                        break  # 启动服务后退出菜单
                else:
                    print(f"{Colors.RED}无效选择，请重试{Colors.RESET}")
                    
            except KeyboardInterrupt:
                cleanup_processes()
                print(f"\n{Colors.GREEN}👋 再见！{Colors.RESET}")
                break
            except Exception as e:
                print(f"{Colors.RED}错误: {e}{Colors.RESET}")


if __name__ == "__main__":
    main()
