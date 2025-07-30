#!/usr/bin/env python3
"""
RuleK 游戏启动器
自动处理Python路径问题
"""
import sys
import os
from pathlib import Path

# 确保项目根目录在Python路径中
def setup_python_path():
    """设置Python路径"""
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    
    # 如果当前在项目根目录，直接添加
    if (script_dir / "src").exists():
        sys.path.insert(0, str(script_dir))
    # 如果在其他目录，尝试找到项目根目录
    else:
        # 向上查找包含src的目录
        current = script_dir
        while current != current.parent:
            if (current / "src").exists():
                sys.path.insert(0, str(current))
                break
            current = current.parent

def main():
    """主函数"""
    # 设置路径
    setup_python_path()
    
    # 选择运行模式
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "cli"
    
    if mode == "cli":
        print("🎮 启动CLI版规则怪谈管理者...")
        from src.cli_game import main as cli_main
        import asyncio
        asyncio.run(cli_main())
        
    elif mode == "web":
        print("🌐 启动Web服务器...")
        os.system("python start_web_server.py")
        
    elif mode == "test":
        print("🧪 运行测试...")
        os.system("python test_fixes.py")
        
    else:
        print("用法:")
        print("  python play.py         # 运行CLI游戏（默认）")
        print("  python play.py cli     # 运行CLI游戏")
        print("  python play.py web     # 启动Web服务器")
        print("  python play.py test    # 运行测试")

if __name__ == "__main__":
    main()
