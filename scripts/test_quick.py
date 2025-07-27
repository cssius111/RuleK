#!/usr/bin/env python3
"""快速测试脚本 - 一键运行所有测试"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, env=None):
    """运行命令并返回结果"""
    print(f"运行: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🧪 规则怪谈管理者 - 快速测试")
    print("=" * 50)
    
    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    # 检查是否安装了 pytest-asyncio
    print("\n1. 检查测试依赖...")
    check_cmd = [sys.executable, "-m", "pip", "show", "pytest-asyncio"]
    if run_command(check_cmd, env) != 0:
        print("⚠️  pytest-asyncio 未安装，正在安装...")
        install_cmd = [sys.executable, "-m", "pip", "install", "pytest-asyncio"]
        if run_command(install_cmd, env) != 0:
            print("❌ 安装失败，请手动运行: pip install pytest-asyncio")
            return 1
    
    # 运行测试
    print("\n2. 运行所有测试...")
    test_cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--asyncio-mode=auto"
    ]
    
    # 添加命令行参数
    if len(sys.argv) > 1:
        test_cmd.extend(sys.argv[1:])
    
    exit_code = run_command(test_cmd, env)
    
    if exit_code == 0:
        print("\n✅ 所有测试通过！")
    else:
        print(f"\n❌ 测试失败，退出码: {exit_code}")
        print("\n常见问题解决:")
        print("1. 如果看到 'async def' 警告，确保安装了 pytest-asyncio")
        print("2. 如果看到导入错误，确保在项目根目录运行")
        print("3. 如果看到 Pydantic 警告，这些是已知的弃用警告，不影响功能")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
