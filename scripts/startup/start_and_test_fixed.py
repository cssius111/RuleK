#!/usr/bin/env python3
"""
RuleK 一键启动和测试脚本（修复版）
自动启动服务器并验证API
"""
import subprocess
import time
import requests
import os
import sys
import json

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
            # 修复：使用正确的根路径
            response = requests.get("http://localhost:8000/")
            if response.status_code == 200:
                print("✅ 后端启动成功!")
                return process
        except:
            pass
    
    print("❌ 后端启动失败")
    process.terminate()
    return None

def check_frontend_dependencies():
    """检查前端依赖是否已安装"""
    frontend_dir = os.path.join(os.path.dirname(__file__), 'web', 'frontend')
    node_modules = os.path.join(frontend_dir, 'node_modules')
    
    if not os.path.exists(node_modules):
        print("📦 安装前端依赖...")
        try:
            result = subprocess.run(
                ['npm', 'install'],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            if result.returncode == 0:
                print("✅ 前端依赖安装成功!")
                return True
            else:
                print(f"❌ 前端依赖安装失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ 前端依赖安装超时")
            return False
        except Exception as e:
            print(f"❌ 无法安装前端依赖: {e}")
            return False
    return True

def start_frontend():
    """启动前端服务器"""
    print("🚀 启动前端服务器...")
    frontend_dir = os.path.join(os.path.dirname(__file__), 'web', 'frontend')
    
    # 检查端口
    if check_port(5173):
        print("   前端已在运行 (端口 5173)")
        return None
    
    # 检查依赖
    if not check_frontend_dependencies():
        print("❌ 前端依赖检查失败")
        return None
    
    # 启动前端
    try:
        process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, 'VITE_PORT': '5173'}
        )
        
        # 等待启动（Vite 启动较慢）
        print("   等待前端启动（可能需要10-20秒）...")
        for i in range(30):  # 增加等待时间
            time.sleep(1)
            if check_port(5173):
                print("✅ 前端启动成功!")
                return process
            # 检查进程是否还活着
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print(f"❌ 前端进程已退出")
                if stderr:
                    print(f"   错误信息: {stderr[:500]}")
                break
        
        print("❌ 前端启动超时")
        process.terminate()
        
    except FileNotFoundError:
        print("❌ 未找到 npm 命令，请确保已安装 Node.js")
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
    
    return None

def test_api():
    """测试API功能"""
    print("\n🧪 测试API功能...")
    print("-" * 50)
    
    results = []
    
    # 1. 健康检查（使用根路径）
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API健康检查通过 - {data.get('name', 'RuleK API')} v{data.get('version', 'unknown')}")
            results.append(True)
        else:
            print(f"❌ API健康检查失败 (状态码: {response.status_code})")
            results.append(False)
    except Exception as e:
        print(f"❌ 无法连接到API: {e}")
        results.append(False)
        return results
    
    # 2. 创建游戏
    try:
        game_data = {
            "difficulty": "normal",
            "npc_count": 4
        }
        response = requests.post("http://localhost:8000/api/games", json=game_data)
        if response.status_code == 200:
            game_info = response.json()
            game_id = game_info.get("game_id")
            print(f"✅ 游戏创建成功: {game_id}")
            results.append(True)
            
            # 3. 获取游戏状态
            response = requests.get(f"http://localhost:8000/api/games/{game_id}")
            if response.status_code == 200:
                state = response.json()
                npc_count = len(state.get("npcs", []))
                print(f"✅ 获取游戏状态成功 (NPCs: {npc_count})")
                results.append(True)
            else:
                print(f"❌ 获取游戏状态失败 (状态码: {response.status_code})")
                results.append(False)
        else:
            print(f"❌ 游戏创建失败 (状态码: {response.status_code})")
            print(f"   响应: {response.text[:200]}")
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
            data = response.json()
            templates = data.get("templates", [])
            print(f"✅ 获取规则模板成功: {len(templates)} 个")
            # 显示几个模板名称
            if templates:
                template_names = [t.get('name', 'Unknown') for t in templates[:3]]
                print(f"   示例: {', '.join(template_names)}")
            results.append(True)
        else:
            print(f"❌ 获取规则模板失败 (状态码: {response.status_code})")
            results.append(False)
    except Exception as e:
        print(f"❌ 规则API测试失败: {e}")
        results.append(False)
    
    return results

def check_environment():
    """检查环境配置"""
    print("\n🔍 检查环境...")
    
    issues = []
    
    # 检查 Python 版本
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 10:
        print(f"✅ Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️ Python 版本过低: {python_version.major}.{python_version.minor}")
        issues.append("请使用 Python 3.10+")
    
    # 检查 Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js 版本: {result.stdout.strip()}")
        else:
            issues.append("Node.js 未正确安装")
    except FileNotFoundError:
        print("❌ 未找到 Node.js")
        issues.append("请安装 Node.js 16+")
    
    # 检查 npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm 版本: {result.stdout.strip()}")
        else:
            issues.append("npm 未正确安装")
    except FileNotFoundError:
        print("❌ 未找到 npm")
        issues.append("请确保 npm 已安装")
    
    return issues

def main():
    """主函数"""
    print("=" * 60)
    print("🎮 RuleK 一键启动和测试（修复版）")
    print("=" * 60)
    
    # 环境检查
    issues = check_environment()
    if issues:
        print("\n⚠️ 环境问题:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n继续启动...")
    
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
        print("🔌 WebSocket: ws://localhost:8000/ws/[game_id]")
    else:
        print(f"⚠️ 部分测试失败 ({passed}/{total})")
        print("\n故障排查建议:")
        if not test_results[0]:  # 健康检查失败
            print("1. 后端服务未正常启动")
            print("   - 检查 web/backend/app.py 是否存在")
            print("   - 查看 logs/api.log 的错误信息")
        if len(test_results) > 1 and not test_results[1]:  # 创建游戏失败
            print("2. 游戏创建失败")
            print("   - 检查数据库连接")
            print("   - 确认 src 目录下的核心模块存在")
        if frontend and not check_port(5173):
            print("3. 前端未正常启动")
            print("   - 检查 web/frontend/node_modules 是否存在")
            print("   - 尝试手动运行: cd web/frontend && npm install && npm run dev")
    
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
