#!/usr/bin/env python
"""
开发工具脚本集合
提供各种开发辅助功能
"""
import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def format_code():
    """格式化代码"""
    print("🎨 格式化代码...")
    
    # 使用 ruff 格式化
    try:
        subprocess.run(["ruff", "check", "src/", "--fix"], check=True)
        print("✅ 代码格式化完成")
    except subprocess.CalledProcessError:
        print("❌ 代码格式化失败")
        return False
    except FileNotFoundError:
        print("⚠️  未安装 ruff，尝试使用 black...")
        try:
            subprocess.run(["black", "src/"], check=True)
            print("✅ 代码格式化完成")
        except:
            print("❌ 请安装 ruff 或 black")
            return False
    
    return True


def check_types():
    """类型检查"""
    print("🔍 类型检查...")
    
    try:
        result = subprocess.run(
            ["mypy", "src/", "--ignore-missing-imports"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 类型检查通过")
            return True
        else:
            print("❌ 类型检查失败:")
            print(result.stdout)
            return False
    except FileNotFoundError:
        print("⚠️  未安装 mypy")
        return True


def run_tests(test_type="all"):
    """运行测试"""
    print(f"🧪 运行测试: {test_type}")
    
    cmd = ["pytest", "-v"]
    
    if test_type == "unit":
        cmd.append("tests/unit/")
    elif test_type == "integration":
        cmd.append("tests/integration/")
    elif test_type == "coverage":
        cmd.extend(["--cov=src", "--cov-report=html"])
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 测试通过")
        return True
    except subprocess.CalledProcessError:
        print("❌ 测试失败")
        return False
    except FileNotFoundError:
        print("❌ 未安装 pytest")
        return False


def generate_api_docs():
    """生成API文档"""
    print("📚 生成API文档...")
    
    # 启动FastAPI并导出OpenAPI schema
    try:
        import requests
        import time
        
        # 启动服务器
        server_process = subprocess.Popen(
            ["python", "web/backend/app.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # 等待服务器启动
        time.sleep(3)
        
        # 获取OpenAPI schema
        response = requests.get("http://localhost:8000/openapi.json")
        
        if response.status_code == 200:
            # 保存schema
            with open("docs/api/openapi.json", "w") as f:
                json.dump(response.json(), f, indent=2)
            print("✅ API文档已生成: docs/api/openapi.json")
        else:
            print("❌ 无法获取API schema")
        
        # 停止服务器
        server_process.terminate()
        
    except Exception as e:
        print(f"❌ 生成API文档失败: {e}")
        return False
    
    return True


def create_migration():
    """创建数据迁移脚本"""
    print("🔄 创建数据迁移...")
    
    # TODO: 实现数据迁移功能
    print("⚠️  数据迁移功能开发中...")
    return True


def clean_project():
    """清理项目"""
    print("🧹 清理项目...")
    
    # 要清理的目录和文件模式
    patterns = [
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        ".mypy_cache",
        "*.log"
    ]
    
    removed_count = 0
    
    for pattern in patterns:
        for path in project_root.rglob(pattern):
            if path.is_file():
                path.unlink()
                removed_count += 1
            elif path.is_dir():
                import shutil
                shutil.rmtree(path)
                removed_count += 1
    
    print(f"✅ 清理完成，删除了 {removed_count} 个文件/目录")
    return True


def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖...")
    
    # 检查Python依赖
    print("\nPython依赖:")
    result = subprocess.run(
        ["pip", "check"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Python依赖正常")
    else:
        print("❌ Python依赖有问题:")
        print(result.stdout)

    # 检查关键依赖是否存在
    import importlib.util

    required_packages = ["pydantic", "httpx"]
    missing = [pkg for pkg in required_packages if importlib.util.find_spec(pkg) is None]
    if missing:
        print(f"⚠️  缺少必要依赖: {', '.join(missing)}")
        print("   请运行: pip install -r requirements.txt")
    else:
        print("✅ 关键依赖已安装")
    
    # 检查前端依赖
    print("\n前端依赖:")
    if (project_root / "web/frontend/node_modules").exists():
        print("✅ 前端依赖已安装")
    else:
        print("⚠️  前端依赖未安装，请运行: cd web/frontend && npm install")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="RuleK 开发工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python dev_tools.py format        # 格式化代码
  python dev_tools.py test          # 运行测试
  python dev_tools.py check         # 运行所有检查
  python dev_tools.py clean         # 清理项目
        """
    )
    
    parser.add_argument(
        "command",
        choices=[
            "format", "types", "test", "coverage",
            "docs", "migrate", "clean", "deps", "check"
        ],
        help="要执行的命令"
    )
    
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration"],
        default="all",
        help="测试类型"
    )
    
    args = parser.parse_args()
    
    # 执行命令
    if args.command == "format":
        format_code()
    elif args.command == "types":
        check_types()
    elif args.command == "test":
        run_tests(args.type)
    elif args.command == "coverage":
        run_tests("coverage")
    elif args.command == "docs":
        generate_api_docs()
    elif args.command == "migrate":
        create_migration()
    elif args.command == "clean":
        clean_project()
    elif args.command == "deps":
        check_dependencies()
    elif args.command == "check":
        # 运行所有检查
        print("🔍 运行完整检查...\n")
        results = []
        
        results.append(("格式化", format_code()))
        results.append(("类型检查", check_types()))
        results.append(("单元测试", run_tests("unit")))
        results.append(("依赖检查", check_dependencies()))
        
        print("\n📊 检查结果:")
        for name, passed in results:
            status = "✅" if passed else "❌"
            print(f"{status} {name}")
        
        if all(r[1] for r in results):
            print("\n✨ 所有检查通过！")
            sys.exit(0)
        else:
            print("\n❌ 部分检查失败")
            sys.exit(1)


if __name__ == "__main__":
    main()
