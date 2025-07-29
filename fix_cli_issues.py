#!/usr/bin/env python3
"""修复CLI测试的所有问题"""
import subprocess
import sys
import os
from pathlib import Path

def fix_all_issues():
    """修复所有已知问题"""
    print("🔧 修复CLI测试问题...")
    print("=" * 60)
    
    fixes = []
    project_root = Path(__file__).parent
    
    # 1. 修复Event类已经完成
    fixes.append("✅ 修复了 Event dataclass 字段顺序问题")
    fixes.append("✅ 修复了 datetime.utcnow() 弃用警告")
    
    # 2. 安装缺失的测试依赖
    print("\n📦 安装缺失的测试依赖...")
    missing_packages = []
    
    # 检查pytest-html
    try:
        import pytest_html
    except ImportError:
        missing_packages.append("pytest-html")
    
    # 检查pytest-json-report
    try:
        import pytest_json_report
    except ImportError:
        missing_packages.append("pytest-json-report")
    
    if missing_packages:
        print(f"  需要安装: {', '.join(missing_packages)}")
        cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
        result = subprocess.run(cmd)
        if result.returncode == 0:
            fixes.append(f"✅ 安装了缺失的包: {', '.join(missing_packages)}")
        else:
            fixes.append(f"❌ 安装包失败，请手动运行: pip install {' '.join(missing_packages)}")
    else:
        fixes.append("✅ 所有测试依赖已安装")
    
    # 3. 清理Python缓存
    print("\n🧹 清理Python缓存...")
    cache_dirs = [
        ".pytest_cache",
        "__pycache__",
        "src/__pycache__",
        "src/models/__pycache__",
        "src/core/__pycache__",
        "tests/__pycache__",
        "tests/cli/__pycache__"
    ]
    
    for cache_dir in cache_dirs:
        cache_path = project_root / cache_dir
        if cache_path.exists():
            import shutil
            try:
                shutil.rmtree(cache_path)
                print(f"  ✓ 清理了 {cache_dir}")
            except:
                pass
    
    fixes.append("✅ 清理了Python缓存")
    
    # 4. 创建简化的测试脚本（不使用HTML报告）
    simple_test = '''#!/usr/bin/env python3
"""简化的CLI测试运行器（不需要额外插件）"""
import subprocess
import sys
import os

os.environ['PYTEST_RUNNING'] = '1'
cmd = [sys.executable, '-m', 'pytest', 'tests/cli/test_cli_game.py', '-v', '--tb=short']
sys.exit(subprocess.call(cmd))
'''
    
    simple_test_path = project_root / "simple_cli_test.py"
    simple_test_path.write_text(simple_test)
    simple_test_path.chmod(0o755)
    fixes.append("✅ 创建了简化的测试脚本: simple_cli_test.py")
    
    # 5. 设置环境变量
    os.environ['PYTEST_RUNNING'] = '1'
    os.environ['PYTHONPATH'] = str(project_root)
    fixes.append("✅ 设置了测试环境变量")
    
    # 总结
    print("\n📋 修复总结：")
    print("=" * 60)
    for fix in fixes:
        print(f"  {fix}")
    
    print("\n✨ 修复完成！")
    print("\n下一步：")
    print("1. 运行简化测试: python simple_cli_test.py")
    print("2. 或完整测试: python cli_test_runner.py")
    print("3. 如果还有问题，查看具体错误信息")

if __name__ == "__main__":
    fix_all_issues()
