#!/usr/bin/env python3
"""
RuleK 项目启动器
同时启动前后端服务
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def print_banner():
    """打印横幅"""
    print("""
╔══════════════════════════════════════════════════╗
║           RuleK - 规则怪谈管理者                ║
╚══════════════════════════════════════════════════╝
    """)

def start_backend():
    """启动后端服务器"""
    print("\n1. 启动后端服务器...")
    cmd = [sys.executable, "start_web_server.py"]
    process = subprocess.Popen(cmd, cwd=PROJECT_ROOT)
    print(f"   ✓ 后端已启动 (PID: {process.pid})")
    print(f"   地址: http://localhost:8000")
    return process

def start_frontend():
    """启动前端开发服务器"""
    print("\n2. 启动前端开发服务器...")
    frontend_dir = PROJECT_ROOT / "web" / "frontend"
    
    # 检查是否已安装依赖
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("   首次运行，安装前端依赖...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    
    # 启动前端
    cmd = ["npm", "run", "dev"]
    process = subprocess.Popen(cmd, cwd=frontend_dir)
    print(f"   ✓ 前端已启动 (PID: {process.pid})")
    print(f"   地址: http://localhost:5173")
    return process

def main():
    """主函数"""
    print_banner()
    
    processes = []
    
    try:
        # 启动后端
        backend_process = start_backend()
        processes.append(backend_process)
        
        # 等待后端启动
        time.sleep(3)
        
        # 启动前端
        frontend_process = start_frontend()
        processes.append(frontend_process)
        
        print("""
==========================================
✅ 所有服务已启动！

   后端API: http://localhost:8000
   前端界面: http://localhost:5173
   API文档: http://localhost:8000/docs

   按 Ctrl+C 停止所有服务
==========================================
        """)
        
        # 等待进程
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n\n正在停止所有服务...")
        for process in processes:
            process.terminate()
        print("✅ 服务已停止")
        
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n可能的原因：")
        print("1. 缺少Node.js或npm")
        print("2. 缺少Python依赖")
        print("3. 端口被占用")
        
        # 清理进程
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
