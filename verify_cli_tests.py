#!/usr/bin/env python3
"""快速验证CLI测试准备情况"""
import os
import sys
from pathlib import Path

def check_cli_tests():
    """检查CLI测试准备情况"""
    project_root = Path(__file__).parent
    checks = []
    
    print("🔍 检查CLI测试准备情况...")
    print("=" * 50)
    
    # 检查测试文件
    test_files = [
        "tests/cli/test_cli_game.py",
        "tests/cli/test_cli_game_extended.py",
        "tests/cli/conftest.py"
    ]
    
    for file in test_files:
        path = project_root / file
        if path.exists():
            checks.append(f"✅ {file} 存在")
        else:
            checks.append(f"❌ {file} 缺失")
    
    # 检查源文件
    source_files = [
        "src/cli_game.py",
        "src/custom_rule_creator.py",
        "src/core/game_state.py",
        "src/core/rule_executor.py"
    ]
    
    for file in source_files:
        path = project_root / file
        if path.exists():
            checks.append(f"✅ {file} 存在")
        else:
            checks.append(f"❌ {file} 缺失")
    
    # 检查测试工具
    tools = [
        "run_cli_tests.sh",
        "fix_cli_test_env.py",
        "quick_test_cli.py",
        "cli_test_runner.py"
    ]
    
    print("\n📦 测试工具：")
    for tool in tools:
        path = project_root / tool
        if path.exists():
            print(f"  ✅ {tool}")
        else:
            print(f"  ❌ {tool}")
    
    # 检查Python包
    print("\n📚 Python包：")
    packages = ['pytest', 'pytest-asyncio', 'pytest-mock']
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_'))
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg} (需要安装)")
    
    # 检查环境变量
    print("\n🌍 环境变量：")
    if os.environ.get('PYTEST_RUNNING'):
        print("  ✅ PYTEST_RUNNING 已设置")
    else:
        print("  ⚠️  PYTEST_RUNNING 未设置（测试时会自动设置）")
    
    # 总结
    print("\n" + "=" * 50)
    if all("✅" in check for check in checks):
        print("✅ 所有文件都已准备就绪！")
        print("\n下一步：")
        print("1. 运行: python cli_test_runner.py")
        print("2. 或者快速测试: python quick_test_cli.py")
    else:
        print("❌ 有文件缺失，请检查项目结构")
        print("\n缺失的文件：")
        for check in checks:
            if "❌" in check:
                print(f"  {check}")

if __name__ == "__main__":
    check_cli_tests()
