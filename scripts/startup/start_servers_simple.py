#!/usr/bin/env python3
"""简单的服务器启动脚本"""
import subprocess
import os
import sys
import time

def main():
    print("🚀 启动RuleK服务器...\n")
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 启动后端
    print("📦 启动后端服务器...")
    backend_dir = os.path.join(project_root, "web", "backend")
    backend_cmd = [sys.executable, "app.py"]
    
    try:
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=backend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"✅ 后端进程已启动 (PID: {backend_process.pid})")
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return
    
    # 等待后端启动
    time.sleep(3)
    
    # 启动前端
    print("📦 启动前端服务器...")
    frontend_dir = os.path.join(project_root, "web", "frontend")
    frontend_cmd = ["npm", "run", "dev"]
    
    try:
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=frontend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"✅ 前端进程已启动 (PID: {frontend_process.pid})")
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        backend_process.terminate()
        return
    
    print("\n✨ 服务器正在启动，请稍等...")
    print("   后端: http://localhost:8000")
    print("   前端: http://localhost:5173")
    print("\n按 Ctrl+C 停止服务器")
    
    try:
        # 保持脚本运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 停止服务器...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ 服务器已停止")

if __name__ == "__main__":
    main()
