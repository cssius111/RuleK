#!/usr/bin/env python3
"""
快速启动RuleK游戏（前后端）
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

# 设置项目根目录
project_root = Path(__file__).parent.parent
os.chdir(project_root)

def print_banner():
    """打印启动横幅"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                    RuleK - 规则怪谈管理者                   ║
║                    快速启动器 v1.0.1                       ║
╚═══════════════════════════════════════════════════════════╝
    """)

def kill_existing_processes():
    """清理可能存在的进程"""
    print("🧹 清理旧进程...")
    subprocess.run("pkill -f 'uvicorn.*8000' || true", shell=True, capture_output=True)
    subprocess.run("pkill -f 'vite.*5173' || true", shell=True, capture_output=True)
    time.sleep(1)

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    backend_process = subprocess.Popen(
        ["python", "start_web_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return backend_process

def start_frontend():
    """启动前端服务"""
    print("🎨 启动前端服务...")
    frontend_dir = Path("web/frontend")
    
    # 检查依赖
    if not (frontend_dir / "node_modules").exists():
        print("📦 安装前端依赖...")
        subprocess.run("npm install", shell=True, cwd=frontend_dir)
    
    # 启动前端
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=frontend_dir
    )
    return frontend_process

def wait_for_services():
    """等待服务启动"""
    print("⏳ 等待服务启动...")
    
    # 等待后端
    for i in range(10):
        result = subprocess.run(
            "curl -s http://localhost:8000/health",
            shell=True,
            capture_output=True
        )
        if result.returncode == 0:
            print("✅ 后端服务已就绪")
            break
        time.sleep(1)
    
    # 等待前端
    time.sleep(3)
    print("✅ 前端服务已就绪")

def open_browser():
    """打开浏览器"""
    print("🌐 打开浏览器...")
    time.sleep(1)
    webbrowser.open("http://localhost:5173")

def show_instructions():
    """显示使用说明"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                      ✅ 服务启动成功！                       ║
╠═══════════════════════════════════════════════════════════╣
║  🎮 游戏地址: http://localhost:5173                        ║
║  📖 API文档: http://localhost:8000/docs                    ║
║  🔧 后端API: http://localhost:8000                         ║
╠═══════════════════════════════════════════════════════════╣
║                      📝 使用说明                           ║
║  1. 浏览器会自动打开游戏页面                                ║
║  2. 点击"新游戏"开始游戏                                   ║
║  3. 在游戏中点击"创建规则"按钮                              ║
║  4. 选择创建方式：模板/自定义/AI解析                         ║
╠═══════════════════════════════════════════════════════════╣
║  ⚠️  注意：不要访问 /game/create-rule                       ║
║  ✅  正确：在游戏内点击"创建规则"按钮                        ║
╠═══════════════════════════════════════════════════════════╣
║  按 Ctrl+C 停止所有服务                                    ║
╚═══════════════════════════════════════════════════════════╝
    """)

def main():
    """主函数"""
    try:
        print_banner()
        
        # 清理旧进程
        kill_existing_processes()
        
        # 启动服务
        backend_process = start_backend()
        frontend_process = start_frontend()
        
        # 等待服务就绪
        wait_for_services()
        
        # 打开浏览器
        open_browser()
        
        # 显示说明
        show_instructions()
        
        # 保持运行
        print("\n⏸️  服务运行中...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        time.sleep(1)
        print("✅ 所有服务已停止")
        print("👋 感谢使用RuleK！")
        
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
