#!/usr/bin/env python3
"""项目清理和组织脚本"""

import os
import shutil
from pathlib import Path


def cleanup_project():
    """清理项目中的临时文件和缓存"""
    project_root = Path(__file__).parent.parent
    
    print("🧹 开始清理项目...")
    
    # 清理Python缓存
    cache_dirs_removed = 0
    for cache_dir in project_root.rglob("__pycache__"):
        print(f"删除缓存目录: {cache_dir}")
        shutil.rmtree(cache_dir)
        cache_dirs_removed += 1
    
    # 清理.pyc文件
    pyc_files_removed = 0
    for pyc_file in project_root.rglob("*.pyc"):
        print(f"删除编译文件: {pyc_file}")
        pyc_file.unlink()
        pyc_files_removed += 1
    
    # 清理pytest缓存
    pytest_cache = project_root / ".pytest_cache"
    if pytest_cache.exists():
        print(f"删除pytest缓存: {pytest_cache}")
        shutil.rmtree(pytest_cache)
    
    # 清理临时文件
    temp_files_removed = 0
    for temp_file in project_root.rglob("*.tmp"):
        print(f"删除临时文件: {temp_file}")
        temp_file.unlink()
        temp_files_removed += 1
    
    # 清理日志文件（可选）
    clear_logs = input("\n是否清理日志文件？(y/n): ").lower() == 'y'
    if clear_logs:
        log_files_removed = 0
        for log_file in (project_root / "logs").rglob("*.log"):
            print(f"删除日志文件: {log_file}")
            log_file.unlink()
            log_files_removed += 1
        print(f"删除了 {log_files_removed} 个日志文件")
    
    # 创建必要的目录
    directories = [
        "data/saves",
        "data/logs",
        "data/templates",
        "logs",
    ]
    
    for dir_path in directories:
        full_path = project_root / dir_path
        if not full_path.exists():
            print(f"创建目录: {full_path}")
            full_path.mkdir(parents=True, exist_ok=True)
    
    # 创建.gitkeep文件保持空目录
    for dir_path in directories:
        gitkeep = project_root / dir_path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
    
    print(f"\n✅ 项目清理完成")
    print(f"- 删除了 {cache_dirs_removed} 个缓存目录")
    print(f"- 删除了 {pyc_files_removed} 个.pyc文件")
    print(f"- 删除了 {temp_files_removed} 个临时文件")


def organize_project():
    """组织项目文件结构"""
    project_root = Path(__file__).parent.parent
    
    print("\n📁 组织项目结构...")
    
    # 检查是否有文件需要移动
    files_to_organize = []
    
    # 检查根目录下的Python文件
    for py_file in project_root.glob("*.py"):
        if py_file.name not in ["setup.py", "run_game.py", "main_game.py", "main_game_v2.py"]:
            files_to_organize.append(py_file)
    
    if files_to_organize:
        print(f"发现 {len(files_to_organize)} 个文件可能需要整理")
        for file in files_to_organize:
            print(f"  - {file.name}")
        
        organize = input("\n是否移动这些文件到合适的目录？(y/n): ").lower() == 'y'
        if organize:
            # 实施文件移动逻辑
            pass
    else:
        print("项目结构良好，无需调整")


def generate_project_tree():
    """生成项目结构树"""
    project_root = Path(__file__).parent.parent
    
    print("\n📊 项目结构树:")
    print("=" * 60)
    
    def print_tree(path, prefix="", is_last=True):
        """递归打印目录树"""
        # 跳过的目录和文件
        skip_dirs = {".git", "__pycache__", ".pytest_cache", "node_modules", ".DS_Store"}
        
        if path.name in skip_dirs:
            return
        
        connector = "└── " if is_last else "├── "
        print(prefix + connector + path.name)
        
        if path.is_dir():
            children = sorted(list(path.iterdir()))
            children = [c for c in children if c.name not in skip_dirs]
            
            for i, child in enumerate(children):
                extension = "    " if is_last else "│   "
                print_tree(child, prefix + extension, i == len(children) - 1)
    
    print_tree(project_root)
    print("=" * 60)


def check_project_health():
    """检查项目健康状态"""
    project_root = Path(__file__).parent.parent
    
    print("\n🏥 项目健康检查:")
    print("-" * 40)
    
    # 检查必要文件
    required_files = [
        ".env",
        "requirements.txt",
        "README.md",
    ]
    
    missing_files = []
    for file in required_files:
        file_path = project_root / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (缺失)")
            missing_files.append(file)
    
    # 检查环境变量
    if (project_root / ".env").exists():
        import os
        from dotenv import load_dotenv
        load_dotenv(project_root / ".env")
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key and api_key != "your_api_key_here":
            print("✅ DEEPSEEK_API_KEY 已配置")
        else:
            print("⚠️  DEEPSEEK_API_KEY 未配置或使用默认值")
    
    # 检查Python版本
    import sys
    if sys.version_info >= (3, 8):
        print(f"✅ Python版本: {sys.version.split()[0]}")
    else:
        print(f"❌ Python版本过低: {sys.version.split()[0]} (需要3.8+)")
    
    # 检查关键模块
    try:
        import pydantic
        print(f"✅ Pydantic已安装: {pydantic.__version__}")
    except ImportError:
        print("❌ Pydantic未安装")
    
    try:
        import pytest
        print(f"✅ Pytest已安装: {pytest.__version__}")
    except ImportError:
        print("❌ Pytest未安装")
    
    if missing_files:
        print(f"\n⚠️  缺少 {len(missing_files)} 个必要文件")
        print("运行 'python scripts/quick_start.py' 可能会帮助创建缺失的文件")
    else:
        print("\n✅ 项目配置完整")


def main():
    """主函数"""
    print("🛠️  规则怪谈管理者 - 项目维护工具")
    print("=" * 50)
    
    while True:
        print("\n选择操作:")
        print("1. 清理项目缓存和临时文件")
        print("2. 检查项目健康状态")
        print("3. 显示项目结构树")
        print("4. 组织项目文件")
        print("5. 执行所有维护任务")
        print("0. 退出")
        
        choice = input("\n请选择 (0-5): ")
        
        if choice == "0":
            break
        elif choice == "1":
            cleanup_project()
        elif choice == "2":
            check_project_health()
        elif choice == "3":
            generate_project_tree()
        elif choice == "4":
            organize_project()
        elif choice == "5":
            cleanup_project()
            check_project_health()
            generate_project_tree()
        else:
            print("无效的选择，请重试")
    
    print("\n👋 维护完成，再见！")


if __name__ == "__main__":
    main()
