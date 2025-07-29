#!/usr/bin/env python3
"""修复CLI测试环境和已知问题"""
import os
import sys
from pathlib import Path

def fix_known_issues():
    """修复已知的CLI问题"""
    fixes = []
    
    # 修复1: 确保测试环境变量
    if 'PYTEST_RUNNING' not in os.environ:
        os.environ['PYTEST_RUNNING'] = '1'
        fixes.append("设置 PYTEST_RUNNING 环境变量")
    
    # 修复2: 添加项目路径到 Python path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        fixes.append(f"添加项目路径到 sys.path: {project_root}")
    
    # 修复3: 创建必要的目录
    dirs_to_create = [
        'test_results',
        'htmlcov',
        'logs',
        'data/saves',
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        fixes.append(f"创建目录: {dir_path}")
    
    # 修复4: 检查并安装测试依赖
    try:
        import pytest
        import pytest_asyncio
        import pytest_mock
        import pytest_cov
        import pytest_html
    except ImportError as e:
        fixes.append(f"警告: 缺少测试依赖 - {e}")
        print("\n请运行: pip install pytest pytest-asyncio pytest-mock pytest-cov pytest-html")
    
    return fixes

def check_cli_game_issues():
    """检查CLI游戏代码的已知问题"""
    issues = []
    cli_game_path = Path("src/cli_game.py")
    
    if cli_game_path.exists():
        content = cli_game_path.read_text(encoding='utf-8')
        
        # 检查已知问题
        if "state.turn_count" in content:
            issues.append("发现 turn_count 属性问题（应该是 current_turn）")
        
        if "self.game_manager.state.rules" in content:
            issues.append("发现 state.rules 属性问题（应该是 self.game_manager.rules）")
    
    return issues

def main():
    print("🔧 修复CLI测试环境...")
    print("=" * 50)
    
    # 修复环境问题
    fixes = fix_known_issues()
    for fix in fixes:
        print(f"  ✓ {fix}")
    
    # 检查代码问题
    print("\n🔍 检查代码问题...")
    issues = check_cli_game_issues()
    
    if issues:
        print("\n⚠️  发现以下问题：")
        for issue in issues:
            print(f"  - {issue}")
        print("\n请手动修复这些问题或运行相应的修复脚本")
    else:
        print("  ✓ 未发现已知代码问题")
    
    print(f"\n✅ 完成 {len(fixes)} 项环境修复")
    
    # 显示下一步
    print("\n📝 下一步：")
    print("1. 运行 chmod +x run_cli_tests.sh")
    print("2. 运行 ./run_cli_tests.sh")
    print("3. 查看测试结果并修复失败的测试")

if __name__ == "__main__":
    main()
