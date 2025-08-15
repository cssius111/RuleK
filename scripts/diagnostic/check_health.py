#!/usr/bin/env python3
"""
项目健康检查
"""

import os
import sys
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def check_file(path, description):
    """检查文件是否存在"""
    full_path = PROJECT_ROOT / path
    if full_path.exists():
        print(f"  ✓ {description}")
        return True
    else:
        print(f"  ✗ {description} (缺失: {path})")
        return False

def check_python_deps():
    """检查Python依赖"""
    print("\n检查Python依赖...")
    try:
        import fastapi
        print("  ✓ FastAPI")
    except ImportError:
        print("  ✗ FastAPI (运行: pip install fastapi)")
        return False
    
    try:
        import uvicorn
        print("  ✓ Uvicorn")
    except ImportError:
        print("  ✗ Uvicorn (运行: pip install uvicorn[standard])")
        return False
    
    return True

def check_node():
    """检查Node.js"""
    print("\n检查Node.js...")
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Node.js {result.stdout.strip()}")
            return True
    except:
        pass
    print("  ✗ Node.js未安装")
    return False

def check_frontend_deps():
    """检查前端依赖"""
    print("\n检查前端依赖...")
    node_modules = PROJECT_ROOT / "web" / "frontend" / "node_modules"
    if node_modules.exists():
        print("  ✓ 前端依赖已安装")
        return True
    else:
        print("  ✗ 前端依赖未安装 (运行: cd web/frontend && npm install)")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("RuleK 项目健康检查")
    print("=" * 50)
    
    all_ok = True
    
    # 检查核心文件
    print("\n检查核心文件...")
    all_ok &= check_file("start_web_server.py", "后端启动脚本")
    all_ok &= check_file("web/backend/app.py", "后端应用")
    all_ok &= check_file("web/frontend/index.html", "前端入口")
    all_ok &= check_file("web/frontend/src/main.ts", "前端主文件")
    all_ok &= check_file("web/frontend/src/stores/game.js", "游戏状态管理")
    all_ok &= check_file("config/config.json", "配置文件")
    
    # 检查Python依赖
    all_ok &= check_python_deps()
    
    # 检查Node.js
    all_ok &= check_node()
    
    # 检查前端依赖
    if check_node():
        all_ok &= check_frontend_deps()
    
    # 总结
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ 项目状态良好！")
        print("\n启动方法:")
        print("  python start_all.py")
        print("\n或分别启动:")
        print("  1. python start_web_server.py")
        print("  2. cd web/frontend && npm run dev")
    else:
        print("⚠️ 发现一些问题，请按照提示修复")
        print("\n快速修复:")
        print("  1. pip install -r requirements.txt")
        print("  2. cd web/frontend && npm install")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
