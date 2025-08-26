"""系统诊断工具"""
from __future__ import annotations

import socket
import subprocess
import sys
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def check_python_version() -> bool:
    """检查Python版本"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    print("  ✗ Python版本过低 (需要3.10+)")
    return False


def check_nodejs() -> bool:
    """检查Node.js"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"  ✓ Node.js {result.stdout.strip()}")
        return True
    except Exception:
        print("  ✗ Node.js未安装")
        return False


def check_python_deps() -> bool:
    """检查Python依赖"""
    try:
        import fastapi  # noqa: F401  # type: ignore
        import uvicorn  # noqa: F401  # type: ignore
        import pydantic  # noqa: F401  # type: ignore
        print("  ✓ 核心依赖已安装")
        return True
    except ImportError as e:
        print(f"  ✗ 缺少依赖: {e}")
        return False


def check_frontend_deps() -> bool:
    """检查前端依赖"""
    node_modules = PROJECT_ROOT / "web" / "frontend" / "node_modules"
    if node_modules.exists():
        print("  ✓ 前端依赖已安装")
        return True
    print("  ⚠ 前端依赖未安装")
    return False


def check_ports() -> bool:
    """检查端口是否可用"""
    ports = [(8000, "后端"), (5173, "前端")]
    all_free = True
    for port, name in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("localhost", port))
        if result == 0:
            print(f"  ⚠ 端口 {port} ({name}) 已被占用")
            all_free = False
        else:
            print(f"  ✓ 端口 {port} ({name}) 可用")
    return all_free


def check_project_structure() -> bool:
    """检查项目结构"""
    required_dirs = ["src", "web", "tests", "scripts", "docs"]
    all_exist = True
    for dir_name in required_dirs:
        if (PROJECT_ROOT / dir_name).exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ 缺失")
            all_exist = False
    return all_exist


def run_diagnostics() -> None:
    """运行完整诊断"""
    checks: list[tuple[str, Callable[[], bool]]] = [
        ("Python版本", check_python_version),
        ("Node.js", check_nodejs),
        ("Python依赖", check_python_deps),
        ("前端依赖", check_frontend_deps),
        ("端口状态", check_ports),
        ("项目结构", check_project_structure),
    ]

    all_pass = True
    for name, func in checks:
        print(f"\n检查 {name}...")
        if not func():
            all_pass = False
    if all_pass:
        print("\n✅ 所有检查通过！")
    else:
        print("\n⚠️ 发现一些问题，运行 'python rulek.py fix' 尝试修复")


if __name__ == "__main__":
    run_diagnostics()
