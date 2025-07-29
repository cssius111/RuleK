#!/usr/bin/env python3
"""
终极CLI测试修复和运行脚本
一键修复所有问题并运行测试
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path
import time

def print_header(text):
    """打印标题"""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print('=' * 60)

def main():
    """主函数"""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print_header("🚀 RuleK CLI 测试修复和运行工具")
    
    # 步骤1：清理缓存
    print_header("步骤1：清理Python缓存")
    cache_dirs = [
        ".pytest_cache",
        "__pycache__",
        "src/__pycache__",
        "src/models/__pycache__",
        "src/core/__pycache__",
        "src/api/__pycache__",
        "src/ai/__pycache__",
        "tests/__pycache__",
        "tests/cli/__pycache__"
    ]
    
    for cache_dir in cache_dirs:
        cache_path = project_root / cache_dir
        if cache_path.exists():
            try:
                shutil.rmtree(cache_path)
                print(f"  ✓ 清理了 {cache_dir}")
            except Exception as e:
                print(f"  ⚠️  无法清理 {cache_dir}: {e}")
    
    # 步骤2：设置环境
    print_header("步骤2：设置测试环境")
    os.environ['PYTEST_RUNNING'] = '1'
    os.environ['PYTHONPATH'] = str(project_root)
    print("  ✓ 设置了环境变量")
    
    # 创建必要目录
    dirs = ['test_results', 'htmlcov', 'logs', 'data/saves']
    for dir_path in dirs:
        (project_root / dir_path).mkdir(parents=True, exist_ok=True)
    print("  ✓ 创建了必要目录")
    
    # 步骤3：检查依赖
    print_header("步骤3：检查和安装依赖")
    required_packages = {
        'pytest': 'pytest',
        'pytest_asyncio': 'pytest-asyncio',
        'pytest_mock': 'pytest-mock',
        'pytest_cov': 'pytest-cov'
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package_name} 已安装")
        except ImportError:
            missing.append(package_name)
            print(f"  ❌ {package_name} 未安装")
    
    if missing:
        print(f"\n  📦 安装缺失的包: {', '.join(missing)}")
        cmd = [sys.executable, "-m", "pip", "install"] + missing
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print("  ❌ 安装失败，请手动安装")
            return 1
    
    # 步骤4：验证修复
    print_header("步骤4：验证Event类修复")
    try:
        # 动态导入以避免缓存
        if 'src.models.event' in sys.modules:
            del sys.modules['src.models.event']
        
        from src.models.event import Event, EventType
        event = Event(type=EventType.SYSTEM, description="测试", turn=1)
        print("  ✓ Event类已修复并可正常使用")
    except Exception as e:
        print(f"  ❌ Event类仍有问题: {e}")
        print("\n  💡 请确保 src/models/event.py 已更新")
        return 1
    
    # 步骤5：运行快速测试
    print_header("步骤5：运行快速导入测试")
    try:
        from src.cli_game import CLIGame
        game = CLIGame()
        game.clear_screen = lambda: None
        print("  ✓ CLIGame可以正常导入和实例化")
    except Exception as e:
        print(f"  ❌ CLIGame导入失败: {e}")
        return 1
    
    # 步骤6：运行完整测试
    print_header("步骤6：运行CLI测试套件")
    
    # 等待一下确保文件系统同步
    time.sleep(0.5)
    
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/cli/test_cli_game.py',
        '-v',
        '--tb=short',
        '--no-header',
        '-x'  # 在第一个失败时停止
    ]
    
    print(f"\n  执行命令: {' '.join(cmd)}")
    print("\n" + "-" * 60)
    
    result = subprocess.run(cmd, cwd=project_root)
    
    print("-" * 60)
    
    # 总结
    print_header("测试结果")
    if result.returncode == 0:
        print("  ✅ 所有测试通过！")
        print("\n  🎉 恭喜！CLI测试已经完全修复！")
        print("\n  下一步：")
        print("  1. 运行扩展测试: pytest tests/cli/test_cli_game_extended.py -v")
        print("  2. 查看覆盖率: pytest tests/cli/test_cli_game.py --cov=src.cli_game --cov-report=html")
        print("  3. 集成到CI/CD流程")
    else:
        print("  ❌ 仍有测试失败")
        print("\n  💡 建议：")
        print("  1. 查看上面的错误信息")
        print("  2. 运行: python diagnose_cli.py")
        print("  3. 手动修复具体问题")
        print("  4. 重新运行此脚本")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
