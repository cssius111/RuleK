#!/usr/bin/env python3
"""
RuleK 服务器启动脚本（修复版）
包含完整的错误处理和诊断
"""

import sys
import os
import subprocess
import time
import httpx
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = ['fastapi', 'uvicorn', 'httpx', 'pydantic']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ 缺少依赖包: {', '.join(missing)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖已安装")
    return True

def check_port(port=8000):
    """检查端口是否可用"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('localhost', port))
        if result == 0:
            print(f"⚠️ 端口 {port} 已被占用")
            print("尝试停止现有服务或使用其他端口")
            return False
    print(f"✅ 端口 {port} 可用")
    return True

def test_server_connection(max_retries=5):
    """测试服务器连接"""
    url = "http://localhost:8000/"
    
    for i in range(max_retries):
        try:
            response = httpx.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ 服务器启动成功!")
                print(f"   名称: {data['name']}")
                print(f"   版本: {data['version']}")
                print(f"   状态: {data['status']}")
                return True
        except:
            if i < max_retries - 1:
                print(f"⏳ 等待服务器启动... ({i+1}/{max_retries})")
                time.sleep(2)
    
    print("❌ 服务器启动失败或响应超时")
    return False

def start_server():
    """启动FastAPI服务器"""
    print("=" * 60)
    print("🚀 RuleK 服务器启动器（修复版）")
    print("=" * 60)
    
    # 1. 检查依赖
    if not check_dependencies():
        return
    
    # 2. 检查端口
    if not check_port():
        response = input("\n是否要尝试停止现有服务？(y/n): ")
        if response.lower() == 'y':
            try:
                # 尝试停止现有服务
                subprocess.run(['pkill', '-f', 'uvicorn.*app:app'], check=False)
                time.sleep(2)
                if not check_port():
                    print("❌ 无法释放端口")
                    return
            except:
                print("❌ 无法停止现有服务")
                return
        else:
            return
    
    # 3. 启动服务器
    print("\n🚀 启动服务器...")
    
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    
    # 启动命令
    cmd = [
        sys.executable, "-m", "uvicorn",
        "web.backend.app:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--log-level", "info"
    ]
    
    try:
        # 启动服务器进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        time.sleep(3)
        
        # 测试连接
        if test_server_connection():
            print("\n" + "=" * 60)
            print("🎮 RuleK 服务器已就绪!")
            print("=" * 60)
            print("\n📍 访问地址:")
            print("   主页: http://localhost:8000")
            print("   API文档: http://localhost:8000/docs")
            print("   交互式文档: http://localhost:8000/redoc")
            print("\n💡 快速测试:")
            print("   运行: python fix_api.py")
            print("\n⌨️ 按 Ctrl+C 停止服务器")
            print("=" * 60)
            
            # 持续输出日志
            try:
                for line in process.stdout:
                    print(line, end='')
            except KeyboardInterrupt:
                print("\n\n🛑 正在停止服务器...")
                process.terminate()
                process.wait()
                print("✅ 服务器已停止")
        else:
            print("\n❌ 服务器启动失败")
            process.terminate()
            process.wait()
            
            # 显示错误信息
            print("\n📋 可能的原因:")
            print("1. 端口被占用")
            print("2. 依赖包版本不兼容")
            print("3. 代码语法错误")
            print("\n💡 调试建议:")
            print("1. 检查 logs/ 目录下的日志文件")
            print("2. 直接运行: uvicorn web.backend.app:app --reload")
            print("3. 检查 web/backend/app.py 是否有语法错误")
            
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n💡 请尝试手动运行:")
        print(f"   {' '.join(cmd)}")

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n\n👋 再见!")
    except Exception as e:
        print(f"\n❌ 意外错误: {e}")
        import traceback
        traceback.print_exc()
