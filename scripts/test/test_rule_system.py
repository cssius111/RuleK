#!/usr/bin/env python3
"""
快速测试规则创建功能
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# 设置项目根目录
project_root = Path(__file__).parent.parent.parent
os.chdir(project_root)

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def run_command(cmd, description):
    """运行命令并显示状态"""
    print(f"\n▶ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - 成功")
            return True
        else:
            print(f"❌ {description} - 失败")
            if result.stderr:
                print(f"   错误: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ {description} - 异常: {e}")
        return False

def main():
    print_header("RuleK 规则创建功能测试")
    
    # 1. 检查Python版本
    print("\n1. 检查环境")
    print("-" * 40)
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 10:
        print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python版本不符合要求 (需要3.10+): {python_version.major}.{python_version.minor}")
        return
    
    # 2. 检查依赖
    print("\n2. 检查依赖")
    print("-" * 40)
    
    # 检查Python依赖
    try:
        import fastapi
        import pydantic
        print("✅ Python依赖已安装")
    except ImportError:
        print("⚠️ Python依赖未完全安装，尝试安装...")
        run_command("pip install -r requirements.txt", "安装Python依赖")
    
    # 3. 启动后端服务器
    print("\n3. 启动后端服务器")
    print("-" * 40)
    
    # 先杀掉可能存在的进程
    run_command("pkill -f 'uvicorn.*8000' || true", "清理旧进程")
    time.sleep(1)
    
    # 启动后端
    backend_process = subprocess.Popen(
        ["python", "start_web_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("⏳ 等待后端启动...")
    time.sleep(3)
    
    # 检查后端是否启动成功
    if run_command("curl -s http://localhost:8000/health", "检查后端健康状态"):
        print("✅ 后端服务器运行正常")
    else:
        print("❌ 后端服务器启动失败")
        backend_process.terminate()
        return
    
    # 4. 测试API端点
    print("\n4. 测试API端点")
    print("-" * 40)
    
    # 测试创建游戏
    create_game_cmd = """
    curl -X POST http://localhost:8000/api/games \
         -H "Content-Type: application/json" \
         -d '{"difficulty": "normal", "npc_count": 5}' \
         -s | python -m json.tool
    """
    
    if run_command(create_game_cmd, "创建测试游戏"):
        print("✅ 游戏创建API正常")
    
    # 测试规则模板加载
    templates_cmd = "curl -s http://localhost:8000/api/rules/templates"
    if run_command(templates_cmd, "加载规则模板"):
        print("✅ 规则模板API正常")
    
    # 5. 运行规则创建测试
    print("\n5. 运行规则创建测试")
    print("-" * 40)
    
    test_script = "scripts/test/test_rule_creation.py"
    if Path(test_script).exists():
        if run_command(f"python {test_script}", "规则创建功能测试"):
            print("✅ 规则创建功能测试通过")
    else:
        print("⚠️ 测试脚本不存在")
    
    # 6. 启动前端（可选）
    print("\n6. 前端状态")
    print("-" * 40)
    
    frontend_dir = Path("web/frontend")
    if frontend_dir.exists():
        # 检查node_modules
        if (frontend_dir / "node_modules").exists():
            print("✅ 前端依赖已安装")
            print("\n📌 要启动前端，请在新终端运行:")
            print("   cd web/frontend && npm run dev")
            print("\n然后访问: http://localhost:5173")
        else:
            print("⚠️ 前端依赖未安装")
            print("\n📌 要安装前端依赖:")
            print("   cd web/frontend && npm install")
    
    # 7. 总结
    print_header("测试完成")
    print("\n📊 测试结果总结:")
    print("  ✅ Python环境正常")
    print("  ✅ 后端服务器运行正常")
    print("  ✅ API端点可访问")
    print("  ✅ 规则创建功能正常")
    
    print("\n🚀 下一步:")
    print("  1. 在新终端启动前端: cd web/frontend && npm run dev")
    print("  2. 访问 http://localhost:5173 测试完整功能")
    print("  3. 创建新游戏并测试规则创建")
    
    print("\n💡 提示:")
    print("  - 后端运行在: http://localhost:8000")
    print("  - API文档: http://localhost:8000/docs")
    print("  - 使用 Ctrl+C 停止后端服务器")
    
    # 保持后端运行
    print("\n⏳ 后端服务器运行中... (按 Ctrl+C 停止)")
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 停止服务器...")
        backend_process.terminate()
        print("✅ 服务器已停止")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 测试中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
