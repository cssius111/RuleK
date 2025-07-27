#!/usr/bin/env python3
"""最终测试运行脚本 - 带有所有修复"""

import subprocess
import sys
import os
from pathlib import Path


def main():
    """运行测试，忽略已知的警告"""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🧪 规则怪谈管理者 - 测试运行器（已修复版）")
    print("=" * 60)
    
    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    # pytest 参数
    args = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",                           # 详细输出
        "--tb=short",                   # 简短回溯
        "-W", "ignore::DeprecationWarning",  # 忽略弃用警告
        "--color=yes",                  # 彩色输出
    ]
    
    # 添加用户传入的参数
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    
    print("运行命令:", " ".join(args[2:]))  # 不显示 python -m 部分
    print("-" * 60)
    
    # 运行测试
    result = subprocess.run(args, env=env)
    
    print("-" * 60)
    
    if result.returncode == 0:
        print("✅ 所有测试通过！")
        print("\n下一步:")
        print("1. 运行游戏: python run_game.py")
        print("2. 查看文档: cat docs/README.md")
        print("3. 开始开发: 查看 docs/SPRINT_3_PLAN.md")
    else:
        print(f"❌ 有测试失败 (退出码: {result.returncode})")
        print("\n提示:")
        print("1. 查看上面的错误信息")
        print("2. 运行 'python scripts/verify_env.py' 检查环境")
        print("3. 确保已安装所有依赖: pip install -r requirements.txt")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
