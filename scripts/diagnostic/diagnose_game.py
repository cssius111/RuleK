#!/usr/bin/env python3
"""
RuleK 游戏诊断和修复工具
"""

import os
import sys
import subprocess
import time
import json
import requests
from pathlib import Path

# 颜色输出
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def print_colored(text, color=Colors.WHITE):
    print(f"{color}{text}{Colors.RESET}")

def print_header(title):
    print("\n" + "="*60)
    print_colored(f"  {title}", Colors.CYAN)
    print("="*60)

def check_service(url, name):
    """检查服务是否运行"""
    try:
        response = requests.get(url, timeout=2)
        if response.status_code < 400:
            print_colored(f"✅ {name} 运行正常 ({url})", Colors.GREEN)
            return True
    except:
        pass
    print_colored(f"❌ {name} 未运行 ({url})", Colors.RED)
    return False

def check_port(port):
    """检查端口是否被占用"""
    result = subprocess.run(
        f"lsof -i :{port}", 
        shell=True, 
        capture_output=True, 
        text=True
    )
    return result.returncode == 0

def kill_port(port):
    """杀死占用端口的进程"""
    subprocess.run(f"lsof -ti :{port} | xargs kill -9", shell=True, stderr=subprocess.DEVNULL)
    time.sleep(1)

def start_backend():
    """启动后端服务"""
    print_colored("🚀 启动后端服务...", Colors.YELLOW)
    
    # 检查端口
    if check_port(8000):
        print_colored("   端口8000被占用，尝试清理...", Colors.YELLOW)
        kill_port(8000)
    
    # 启动后端
    backend_process = subprocess.Popen(
        ["python3", "start_web_server.py"],
        cwd="/Users/chenpinle/Desktop/杂/pythonProject/RuleK",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待启动
    for i in range(10):
        time.sleep(1)
        if check_service("http://localhost:8000/health", "后端API"):
            return backend_process
    
    print_colored("   后端启动失败", Colors.RED)
    return None

def start_frontend():
    """启动前端服务"""
    print_colored("🚀 启动前端服务...", Colors.YELLOW)
    
    # 检查端口
    if check_port(5173):
        print_colored("   端口5173被占用，尝试清理...", Colors.YELLOW)
        kill_port(5173)
    
    # 检查是否安装了依赖
    frontend_dir = Path("/Users/chenpinle/Desktop/杂/pythonProject/RuleK/web/frontend")
    node_modules = frontend_dir / "node_modules"
    
    if not node_modules.exists():
        print_colored("📦 安装前端依赖...", Colors.YELLOW)
        subprocess.run(
            ["npm", "install"],
            cwd=str(frontend_dir),
            check=True
        )
    
    # 启动前端
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "NODE_ENV": "development"}
    )
    
    # 等待启动
    for i in range(15):
        time.sleep(1)
        if check_service("http://localhost:5173", "前端开发服务器"):
            return frontend_process
    
    print_colored("   前端启动失败", Colors.RED)
    return None

def test_game_creation():
    """测试游戏创建API"""
    print_header("测试游戏创建")
    
    # 测试API端点
    api_url = "http://localhost:8000/api/games"
    
    # 创建游戏的请求数据
    game_config = {
        "difficulty": "normal",
        "initialFearPoints": 1000,
        "initialNPCCount": 4,
        "aiEnabled": False,
        "playerName": "TestPlayer"
    }
    
    try:
        print_colored("📡 发送创建游戏请求...", Colors.YELLOW)
        response = requests.post(
            api_url,
            json=game_config,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            print_colored("✅ 游戏创建成功！", Colors.GREEN)
            data = response.json()
            print(f"   游戏ID: {data.get('gameId', 'N/A')}")
            return True
        else:
            print_colored(f"❌ 游戏创建失败: {response.status_code}", Colors.RED)
            print(f"   响应: {response.text[:200]}")
            return False
    except Exception as e:
        print_colored(f"❌ API请求失败: {e}", Colors.RED)
        return False

def check_frontend_config():
    """检查前端配置"""
    print_header("检查前端配置")
    
    env_file = Path("/Users/chenpinle/Desktop/杂/pythonProject/RuleK/web/frontend/.env")
    
    if not env_file.exists():
        print_colored("⚠️ .env文件不存在，创建默认配置...", Colors.YELLOW)
        env_content = """# API配置
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000

# WebSocket配置
VITE_WS_URL=ws://localhost:8000

# 开发模式配置
VITE_USE_MOCK_DATA=false
VITE_USE_REAL_API=true

# 调试配置
VITE_DEBUG_MODE=true
"""
        env_file.write_text(env_content)
        print_colored("✅ 已创建.env文件", Colors.GREEN)
    else:
        print_colored("✅ .env文件存在", Colors.GREEN)
        # 读取并显示关键配置
        content = env_file.read_text()
        if "VITE_API_BASE_URL" in content:
            for line in content.split('\n'):
                if 'VITE_API_BASE_URL' in line:
                    print(f"   {line.strip()}")

def check_store_files():
    """检查store文件冲突"""
    print_header("检查Store文件")
    
    store_dir = Path("/Users/chenpinle/Desktop/杂/pythonProject/RuleK/web/frontend/src/stores")
    
    js_file = store_dir / "game.js"
    ts_file = store_dir / "game.ts"
    
    if js_file.exists() and ts_file.exists():
        print_colored("⚠️ 发现重复的store文件！", Colors.YELLOW)
        print("   - game.js (旧版本)")
        print("   - game.ts (新版本)")
        
        # 备份并删除旧文件
        backup_name = store_dir / "game.js.backup"
        js_file.rename(backup_name)
        print_colored(f"✅ 已将game.js重命名为game.js.backup", Colors.GREEN)
    elif ts_file.exists():
        print_colored("✅ 只有game.ts文件存在（正确）", Colors.GREEN)
    else:
        print_colored("❌ 未找到game store文件！", Colors.RED)

def run_diagnostics():
    """运行完整诊断"""
    print_colored("\n🔍 RuleK 游戏诊断工具", Colors.MAGENTA)
    print_colored("="*60, Colors.MAGENTA)
    
    # 1. 检查服务状态
    print_header("检查服务状态")
    backend_running = check_service("http://localhost:8000/health", "后端API")
    frontend_running = check_service("http://localhost:5173", "前端开发服务器")
    
    # 2. 检查文件配置
    check_store_files()
    check_frontend_config()
    
    # 3. 启动缺失的服务
    backend_process = None
    frontend_process = None
    
    if not backend_running:
        backend_process = start_backend()
        if not backend_process:
            print_colored("❌ 无法启动后端服务", Colors.RED)
            return False
    
    if not frontend_running:
        frontend_process = start_frontend()
        if not frontend_process:
            print_colored("❌ 无法启动前端服务", Colors.RED)
            return False
    
    # 4. 测试API
    time.sleep(2)  # 等待服务完全启动
    test_game_creation()
    
    # 5. 输出访问信息
    print_header("🎮 服务已就绪！")
    print_colored("访问地址:", Colors.GREEN)
    print("  前端: http://localhost:5173")
    print("  后端API: http://localhost:8000")
    print("  API文档: http://localhost:8000/docs")
    print()
    print_colored("测试步骤:", Colors.YELLOW)
    print("  1. 打开浏览器访问 http://localhost:5173")
    print("  2. 点击'新游戏'或访问 http://localhost:5173/new-game")
    print("  3. 填写游戏配置并点击'开启地狱之门'")
    print()
    print_colored("如果仍有问题:", Colors.CYAN)
    print("  1. 清除浏览器缓存 (Cmd+Shift+R)")
    print("  2. 打开浏览器控制台 (F12) 查看错误")
    print("  3. 检查 web/frontend/test-results/ 目录的截图")
    
    return True

if __name__ == "__main__":
    try:
        success = run_diagnostics()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_colored("\n\n⛔ 用户中断", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_colored(f"\n❌ 发生错误: {e}", Colors.RED)
        sys.exit(1)
