#!/usr/bin/env python3
"""快速修复测试问题"""

import os
import sys
from pathlib import Path


def fix_imports():
    """修复导入问题"""
    print("🔧 修复导入问题...")
    
    # 已经在之前的步骤中修复了
    print("   ✅ 导入路径已修复")


def install_dependencies():
    """安装缺失的依赖"""
    print("\n📦 检查依赖...")
    
    import subprocess
    
    # 检查 pytest-asyncio
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "pytest-asyncio"],
        capture_output=True
    )
    
    if result.returncode != 0:
        print("   ⚠️  安装 pytest-asyncio...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest-asyncio"])
    else:
        print("   ✅ pytest-asyncio 已安装")


def run_tests():
    """运行测试"""
    print("\n🧪 运行测试...")
    
    import subprocess
    
    # 设置环境变量
    env = os.environ.copy()
    project_root = Path(__file__).parent.parent
    env["PYTHONPATH"] = str(project_root)
    
    # 运行测试
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--asyncio-mode=auto",
        "-W", "ignore::DeprecationWarning"  # 忽略弃用警告
    ]
    
    result = subprocess.run(cmd, env=env)
    
    return result.returncode


def main():
    """主函数"""
    print("🚀 规则怪谈管理者 - 快速修复")
    print("=" * 50)
    
    # 切换到项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # 执行修复
    fix_imports()
    install_dependencies()
    
    print("\n✅ 修复完成！")
    print("\n现在运行测试...")
    print("-" * 50)
    
    exit_code = run_tests()
    
    if exit_code == 0:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  仍有测试失败 (退出码: {exit_code})")
        print("\n提示:")
        print("1. Pydantic 警告是正常的，不影响功能")
        print("2. 如果看到 API 相关的测试被跳过，需要配置 .env 文件")
        print("3. 运行 'python scripts/verify_env.py' 检查环境")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
