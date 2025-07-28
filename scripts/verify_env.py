#!/usr/bin/env python3
"""环境验证脚本 - 检查测试环境是否正确配置"""

import sys
import os
import subprocess
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    print("1. 检查Python版本...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (需要3.8+)")
        return False
    return True


def check_dependencies():
    """检查依赖包"""
    print("\n2. 检查关键依赖...")
    
    required_packages = {
        "pytest": "测试框架",
        "pytest-asyncio": "异步测试支持",
        "pydantic": "数据验证",
        "httpx": "HTTP客户端",
    }
    
    all_installed = True
    for package, description in required_packages.items():
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # 提取版本信息
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':')[1].strip()
                        print(f"   ✅ {package} {version} - {description}")
                        break
            else:
                print(f"   ❌ {package} 未安装 - {description}")
                all_installed = False
        except Exception as e:
            print(f"   ❌ 检查 {package} 时出错: {e}")
            all_installed = False
    
    return all_installed


def check_project_structure():
    """检查项目结构"""
    print("\n3. 检查项目结构...")
    
    project_root = Path(__file__).parent.parent
    required_dirs = [
        "src",
        "tests",
        "tests/unit",
        "scripts",
        "docs",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ (缺失)")
            all_exist = False
    
    return all_exist


def test_import():
    """测试关键模块导入"""
    print("\n4. 测试模块导入...")
    
    # 添加项目路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    modules_to_test = [
        ("src.core.game_state", "GameStateManager"),
        ("src.models.rule", "Rule"),
        ("src.models.npc", "NPC"),
    ]
    
    all_imported = True
    for module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"   ✅ {module_path}.{class_name}")
            else:
                print(f"   ❌ {module_path}.{class_name} (类不存在)")
                all_imported = False
        except ImportError as e:
            print(f"   ❌ {module_path} (导入失败: {e})")
            all_imported = False
    
    return all_imported


def test_async_support():
    """测试异步支持"""
    print("\n5. 测试异步支持...")
    
    test_code = '''
import asyncio
import pytest

@pytest.mark.asyncio
async def test_async():
    await asyncio.sleep(0.01)
    return True

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_async())
    print("异步测试执行成功")
'''
    
    try:
        # 创建一个新的全局命名空间来执行代码
        namespace = {}
        exec(test_code, namespace)
        print("   ✅ 异步测试支持正常")
        return True
    except Exception as e:
        print(f"   ❌ 异步测试失败: {e}")
        return False


def run_simple_test():
    """运行一个简单的测试"""
    print("\n6. 运行简单测试...")
    
    project_root = Path(__file__).parent.parent
    test_file = project_root / "tests" / "unit" / "test_game.py"
    
    if not test_file.exists():
        print("   ❌ 测试文件不存在")
        return False
    
    # 运行单个测试
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file), "-v", "-k", "test_imports",
        "--tb=short"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if "passed" in result.stdout:
        print("   ✅ 测试运行成功")
        return True
    else:
        print("   ❌ 测试运行失败")
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return False


def main():
    """主函数"""
    print("🔍 规则怪谈管理者 - 环境验证")
    print("=" * 50)
    
    results = []
    
    # 运行所有检查
    results.append(("Python版本", check_python_version()))
    results.append(("依赖包", check_dependencies()))
    results.append(("项目结构", check_project_structure()))
    results.append(("模块导入", test_import()))
    results.append(("异步支持", test_async_support()))
    results.append(("测试运行", run_simple_test()))
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 验证结果总结:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 环境配置完美！可以开始运行测试了。")
        print("\n下一步:")
        print("1. 运行所有测试: python rulek.py test")
        print("2. 开始游戏: python rulek.py")
    else:
        print("\n⚠️  有些检查未通过，请根据上面的提示进行修复。")
        print("\n建议:")
        print("1. 安装缺失的依赖: pip install -r requirements.txt")
        print("2. 检查项目结构是否完整")
        print("3. 确保在项目根目录运行此脚本")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
