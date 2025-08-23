#!/usr/bin/env python3
"""
RuleK Web UI 快速启动器
"""
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent

def print_banner():
    """打印欢迎信息"""
    print("""
╔══════════════════════════════════════════════════╗
║        🎮 RuleK - 规则怪谈管理者 🎮            ║
╚══════════════════════════════════════════════════╝
    """)

def check_requirements():
    """检查必要的依赖"""
    print("📋 检查环境...")
    
    # 检查Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        node_version = result.stdout.strip()
        print(f"✅ Node.js: {node_version}")
    except:
        print("❌ 未找到Node.js，请先安装Node.js 16+")
        return False
    
    # 检查npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        npm_version = result.stdout.strip()
        print(f"✅ npm: {npm_version}")
    except:
        print("❌ 未找到npm")
        return False
    
    return True

def start_backend():
    """启动后端服务器"""
    print("\n🚀 启动后端服务器...")
    
    # 尝试不同的启动方式
    start_script = PROJECT_ROOT / "start_web_server.py"
    rulek_script = PROJECT_ROOT / "rulek.py"
    
    if start_script.exists():
        cmd = [sys.executable, str(start_script)]
    elif rulek_script.exists():
        cmd = [sys.executable, str(rulek_script), "web"]
    else:
        print("❌ 找不到启动脚本")
        return None
    
    process = subprocess.Popen(cmd, cwd=PROJECT_ROOT)
    print(f"✅ 后端已启动 (PID: {process.pid})")
    print(f"   地址: http://localhost:8000")
    print(f"   文档: http://localhost:8000/docs")
    return process

def start_frontend():
    """启动前端开发服务器"""
    print("\n🚀 启动前端界面...")
    frontend_dir = PROJECT_ROOT / "web" / "frontend"
    
    if not frontend_dir.exists():
        print(f"❌ 前端目录不存在: {frontend_dir}")
        return None
    
    # 检查是否需要安装依赖
    node_modules = frontend_dir / "node_modules"
    package_json = frontend_dir / "package.json"
    
    if package_json.exists() and not node_modules.exists():
        print("📦 首次运行，安装前端依赖...")
        print("   这可能需要几分钟，请耐心等待...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("✅ 依赖安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return None
    
    # 启动前端
    try:
        cmd = ["npm", "run", "dev"]
        process = subprocess.Popen(cmd, cwd=frontend_dir)
        print(f"✅ 前端已启动 (PID: {process.pid})")
        print(f"   地址: http://localhost:5173")
        return process
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        return None

def open_browser():
    """打开浏览器"""
    time.sleep(3)  # 等待服务完全启动
    print("\n🌐 正在打开浏览器...")
    webbrowser.open("http://localhost:5173")

def main():
    """主函数"""
    print_banner()
    
    # 检查环境
    if not check_requirements():
        print("\n请先安装必要的依赖：")
        print("1. Node.js 16+: https://nodejs.org/")
        print("2. Python 3.10+")
        sys.exit(1)
    
    processes = []
    
    try:
        # 启动后端
        backend = start_backend()
        if backend:
            processes.append(backend)
            time.sleep(3)  # 等待后端启动
        else:
            print("❌ 后端启动失败")
            sys.exit(1)
        
        # 启动前端
        frontend = start_frontend()
        if frontend:
            processes.append(frontend)
        else:
            print("❌ 前端启动失败")
            # 清理后端进程
            backend.terminate()
            sys.exit(1)
        
        # 打开浏览器
        open_browser()
        
        print("""
╔══════════════════════════════════════════════════╗
║              ✨ 启动成功！✨                    ║
╠══════════════════════════════════════════════════╣
║  🎮 游戏界面: http://localhost:5173            ║
║  🔧 API文档:  http://localhost:8000/docs       ║
║  📊 API端点:  http://localhost:8000            ║
╠══════════════════════════════════════════════════╣
║          按 Ctrl+C 停止所有服务                  ║
╚══════════════════════════════════════════════════╝
        """)
        
        # 保持运行
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止所有服务...")
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        print("✅ 所有服务已停止")
        print("👋 感谢使用RuleK！")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("\n可能的解决方案：")
        print("1. 确保端口8000和5173未被占用")
        print("2. 运行: pip install -r requirements.txt")
        print("3. 运行: cd web/frontend && npm install")
        
        # 清理进程
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        sys.exit(1)

if __name__ == "__main__":
    main()
