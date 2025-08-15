#!/usr/bin/env python3
"""
RuleK 一键启动和测试脚本
自动启动服务器并验证API
"""
import subprocess
import time
import requests
import os
import sys

def check_port(port):
    """检查端口是否被占用"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def start_backend():
    """启动后端服务器"""
    print("🚀 启动后端服务器...")
    backend_dir = os.path.join(os.path.dirname(__file__), 'web', 'backend')
    
    # 检查端口
    if check_port(8000):
        print("   后端已在运行 (端口 8000)")
        return None
    
    # 启动后端
    process = subprocess.Popen(
        [sys.executable, 'app.py'],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 等待启动
    for i in range(10):
        time.sleep(1)
        try:
            response = requests.get("http://localhost:8000/api/health")
            if response.status_code == 200:
                print("✅ 后端启动成功!")
                return process
        except:
            pass
    
    print("❌ 后端启动失败")
    process.terminate()
    return None

def start_frontend():
    """启动前端服务器"""
    print("🚀 启动前端服务器...")
    frontend_dir = os.path.join(os.path.dirname(__file__), 'web', 'frontend')
    
    # 检查端口
    if check_port(5173):
        print("   前端已在运行 (端口 5173)")
        return None
    
    # 启动前端
    process = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 等待启动
    for i in range(15):
        time.sleep(1)
        if check_port(5173):
            print("✅ 前端启动成功!")
            return process
    
    print("❌ 前端启动失败")
    process.terminate()
    return None

def test_api():
    """测试API功能"""
    print("\n🧪 测试API功能...")
    print("-" * 50)
    
    results = []
    
    # 1. 健康检查
    try:
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            print("✅ API健康检查通过")
            results.append(True)
        else:
            print("❌ API健康检查失败")
            results.append(False)
    except:
        print("❌ 无法连接到API")
        results.append(False)
        return results
    
    # 2. 创建游戏
    try:
        game_data = {
            "config": {
                "initial_fear_points": 1000,
                "initial_npc_count": 4,
                "difficulty": "normal",
                "ai_enabled": True
            }
        }
        response = requests.post("http://localhost:8000/api/games", json=game_data)
        if response.status_code == 200:
            game_id = response.json().get("game_id")
            print(f"✅ 游戏创建成功: {game_id}")
            results.append(True)
            
            # 3. 获取游戏状态
            response = requests.get(f"http://localhost:8000/api/games/{game_id}")
            if response.status_code == 200:
                print("✅ 获取游戏状态成功")
                results.append(True)
            else:
                print("❌ 获取游戏状态失败")
                results.append(False)
        else:
            print("❌ 游戏创建失败")
            results.append(False)
            results.append(False)
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        results.append(False)
        results.append(False)
    
    # 4. 规则模板
    try:
        response = requests.get("http://localhost:8000/api/rules/templates")
        if response.status_code == 200:
            templates = response.json().get("templates", [])
            print(f"✅ 获取规则模板成功: {len(templates)} 个")
            results.append(True)
        else:
            print("❌ 获取规则模板失败")
            results.append(False)
    except:
        print("❌ 规则API测试失败")
        results.append(False)
    
    return results

def main():
    """主函数"""
    print("=" * 60)
    print("🎮 RuleK 一键启动和测试")
    print("=" * 60)
    
    processes = []
    
    # 启动服务器
    backend = start_backend()
    if backend:
        processes.append(backend)
    
    frontend = start_frontend()
    if frontend:
        processes.append(frontend)
    
    # 等待服务完全启动
    print("\n⏳ 等待服务完全启动...")
    time.sleep(5)
    
    # 测试API
    test_results = test_api()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    if passed == total:
        print(f"✅ 所有测试通过 ({passed}/{total})")
        print("\n🎉 系统准备就绪！")
        print("🌐 访问游戏: http://localhost:5173")
        print("📚 API文档: http://localhost:8000/docs")
    else:
        print(f"⚠️ 部分测试失败 ({passed}/{total})")
        print("\n请检查:")
        print("1. API路径是否正确 (应包含/api前缀)")
        print("2. 后端服务是否正常启动")
        print("3. 数据库连接是否正常")
    
    if processes:
        print("\n按 Ctrl+C 停止所有服务")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 停止所有服务...")
            for p in processes:
                p.terminate()
            print("✅ 服务已停止")

if __name__ == "__main__":
    main()
