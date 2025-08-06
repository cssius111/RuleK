#!/usr/bin/env python3
"""
重新组织项目结构，让根目录更清晰
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent

def create_backup():
    """创建备份"""
    backup_dir = PROJECT_ROOT / ".backups" / f"restructure_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 备份目录: {backup_dir}")
    return backup_dir

def restructure_project():
    """重组项目结构"""
    
    # 创建必要的目录
    tools_dir = PROJECT_ROOT / "tools"
    tools_dir.mkdir(exist_ok=True)
    
    docs_dir = PROJECT_ROOT / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    deploy_dir = PROJECT_ROOT / "deploy"
    deploy_dir.mkdir(exist_ok=True)
    
    print("\n📦 开始重组项目结构...\n")
    
    # 1. 移动管理工具到 tools/
    management_tools = {
        "manage.py": "tools/manage.py",
        "cleanup_project.py": "tools/cleanup.py",
        "project_status.py": "tools/status.py",
        "clean.py": "tools/quick_clean.py",
    }
    
    print("📁 移动管理工具到 tools/ 目录:")
    for src, dst in management_tools.items():
        src_path = PROJECT_ROOT / src
        dst_path = PROJECT_ROOT / dst
        if src_path.exists():
            # 备份原文件
            backup_path = PROJECT_ROOT / ".backups" / src
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, backup_path)
            
            # 移动文件
            shutil.move(str(src_path), str(dst_path))
            print(f"  ✅ {src} → {dst}")
    
    # 2. 移动文档到 docs/
    docs_to_move = {
        "CLEANUP_GUIDE.md": "docs/cleanup_guide.md",
        "CLEANUP_COMPLETE.md": "docs/cleanup_complete.md",
        "START.md": "docs/quick_start.md",
        "AGENTS.md": "docs/agents.md",
        "CONTRIBUTING.md": "docs/contributing.md",
    }
    
    print("\n📚 移动文档到 docs/ 目录:")
    for src, dst in docs_to_move.items():
        src_path = PROJECT_ROOT / src
        dst_path = PROJECT_ROOT / dst
        if src_path.exists():
            # 备份
            backup_path = PROJECT_ROOT / ".backups" / src
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, backup_path)
            
            # 移动
            if not dst_path.exists():  # 避免覆盖
                shutil.move(str(src_path), str(dst_path))
                print(f"  ✅ {src} → {dst}")
    
    # 3. 移动部署相关文件到 deploy/
    deploy_files = {
        "nginx.conf": "deploy/nginx.conf",
        "docker-compose.yml": "deploy/docker-compose.yml",
        "Dockerfile": "deploy/Dockerfile",
    }
    
    print("\n🐳 移动部署文件到 deploy/ 目录:")
    for src, dst in deploy_files.items():
        src_path = PROJECT_ROOT / src
        dst_path = PROJECT_ROOT / dst
        if src_path.exists():
            # 备份
            backup_path = PROJECT_ROOT / ".backups" / src
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, backup_path)
            
            # 移动
            shutil.move(str(src_path), str(dst_path))
            print(f"  ✅ {src} → {dst}")
    
    # 4. 删除无用的 start 文件（没有扩展名的）
    start_file = PROJECT_ROOT / "start"
    if start_file.exists():
        start_file.unlink()
        print("\n🗑️  删除无用文件: start")
    
    # 5. 创建新的 tools/__init__.py
    tools_init = tools_dir / "__init__.py"
    tools_init.write_text('"""项目管理工具"""')
    
    # 6. 更新 tools/manage.py 中的引用
    update_tool_references()
    
    # 7. 创建简化的根目录启动脚本
    create_root_scripts()
    
    print("\n✅ 项目重组完成！")

def update_tool_references():
    """更新工具中的引用路径"""
    tools_dir = PROJECT_ROOT / "tools"
    
    # 更新 manage.py
    manage_path = tools_dir / "manage.py"
    if manage_path.exists():
        content = manage_path.read_text()
        # 更新引用路径
        content = content.replace('subprocess.run([sys.executable, "project_status.py"])', 
                                'subprocess.run([sys.executable, "tools/status.py"])')
        content = content.replace('subprocess.run([sys.executable, "cleanup_project.py"])', 
                                'subprocess.run([sys.executable, "tools/cleanup.py"])')
        content = content.replace('subprocess.run([sys.executable, "start_web_server.py"])', 
                                'subprocess.run([sys.executable, "start_web_server.py"])')
        content = content.replace('guide_path = "CLEANUP_GUIDE.md"', 
                                'guide_path = "docs/cleanup_guide.md"')
        manage_path.write_text(content)
    
    # 更新 cleanup.py
    cleanup_path = tools_dir / "cleanup.py"
    if cleanup_path.exists():
        content = cleanup_path.read_text()
        # 添加路径调整
        if "sys.path.insert" not in content:
            lines = content.split('\n')
            # 在导入后添加路径设置
            for i, line in enumerate(lines):
                if line.startswith('from pathlib import Path'):
                    lines.insert(i+1, '')
                    lines.insert(i+2, '# 调整路径到项目根目录')
                    lines.insert(i+3, 'PROJECT_ROOT = Path(__file__).parent.parent')
                    break
            content = '\n'.join(lines)
        else:
            content = content.replace('PROJECT_ROOT = Path(__file__).parent', 
                                    'PROJECT_ROOT = Path(__file__).parent.parent')
        cleanup_path.write_text(content)
    
    # 更新其他工具文件
    for tool_file in ["status.py", "quick_clean.py"]:
        tool_path = tools_dir / tool_file
        if tool_path.exists():
            content = tool_path.read_text()
            content = content.replace('PROJECT_ROOT = Path(__file__).parent', 
                                    'PROJECT_ROOT = Path(__file__).parent.parent')
            tool_path.write_text(content)

def create_root_scripts():
    """创建根目录的简化启动脚本"""
    
    # 创建 manage 快捷方式
    manage_content = '''#!/usr/bin/env python3
"""快速访问管理工具"""
import subprocess
import sys
subprocess.run([sys.executable, "tools/manage.py"])
'''
    (PROJECT_ROOT / "manage").write_text(manage_content)
    
    # 更新 rulek.py
    rulek_content = '''#!/usr/bin/env python3
"""
RuleK 统一入口
Usage:
    python rulek.py         # 显示帮助
    python rulek.py web     # 启动Web服务器
    python rulek.py cli     # 启动CLI游戏
    python rulek.py test    # 运行测试
    python rulek.py manage  # 项目管理
"""
import sys
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def print_banner():
    """打印横幅"""
    print("""
╔══════════════════════════════════════════════════╗
║           RuleK - 规则怪谈管理者                ║
╚══════════════════════════════════════════════════╝
    """)

def show_help():
    """显示帮助信息"""
    print("""
使用方法:
    python rulek.py <command>

可用命令:
    web     - 启动Web服务器 (http://localhost:8000)
    cli     - 启动命令行游戏
    test    - 运行测试套件
    manage  - 项目管理工具
    help    - 显示此帮助信息

示例:
    python rulek.py web     # 启动Web服务器
    python rulek.py manage  # 打开管理菜单
    """)

def start_web():
    """启动Web服务器"""
    print_banner()
    print("🚀 启动Web服务器...")
    print("   地址: http://localhost:8000")
    print("   文档: http://localhost:8000/docs")
    print("   按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            "web.backend.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ 错误: uvicorn 未安装")
        print("   请运行: pip install uvicorn fastapi")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\\n✅ 服务器已停止")

def start_cli():
    """启动CLI游戏"""
    print_banner()
    print("🎮 启动命令行游戏...")
    print("-" * 50)
    
    try:
        from src.cli_game import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"❌ 无法启动CLI游戏: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\\n👋 游戏已退出")

def run_tests():
    """运行测试"""
    print_banner()
    print("🧪 运行测试套件...")
    print("-" * 50)
    
    try:
        import pytest
        pytest.main(["-v", "tests/"])
    except ImportError:
        print("❌ pytest 未安装")
        print("   请运行: pip install pytest")
        sys.exit(1)

def manage_project():
    """打开项目管理工具"""
    subprocess.run([sys.executable, "tools/manage.py"])

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_banner()
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        "web": start_web,
        "cli": start_cli,
        "test": run_tests,
        "manage": manage_project,
        "help": lambda: (print_banner(), show_help()),
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ 未知命令: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    (PROJECT_ROOT / "rulek.py").write_text(rulek_content)

def show_new_structure():
    """显示新的项目结构"""
    print("\n" + "="*60)
    print("📁 新的项目结构:")
    print("="*60)
    print("""
RuleK/
├── src/                # 核心游戏逻辑
├── web/                # Web界面
├── tests/              # 测试用例
├── docs/               # 所有文档
│   ├── INDEX.md
│   ├── cleanup_guide.md
│   ├── contributing.md
│   └── ...
├── tools/              # 管理工具
│   ├── manage.py       # 项目管理中心
│   ├── cleanup.py      # 清理脚本
│   ├── status.py       # 状态检查
│   └── quick_clean.py  # 快速清理
├── deploy/             # 部署相关
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── config/             # 配置文件
├── data/               # 游戏数据
├── logs/               # 日志文件
├── scripts/            # 其他脚本
│
├── rulek.py           # 统一入口
├── start_web_server.py # Web启动
├── start.sh/bat       # 快捷启动
├── requirements.txt   # 依赖
├── README.md          # 项目说明
├── LICENSE            # 许可证
├── .env               # 环境变量
└── .gitignore         # Git配置
    """)
    
    print("\n✅ 根目录现在只有必要的文件了！")
    print("\n📝 使用方式:")
    print("  python rulek.py         # 查看帮助")
    print("  python rulek.py web     # 启动服务器")
    print("  python rulek.py manage  # 项目管理")

def main():
    print("""
╔══════════════════════════════════════════════════╗
║         项目结构重组工具                        ║
╚══════════════════════════════════════════════════╝
    """)
    
    print("这将重新组织项目结构，使根目录更清晰")
    print("\n将进行以下操作:")
    print("  • 移动管理工具到 tools/ 目录")
    print("  • 移动文档到 docs/ 目录")
    print("  • 移动部署文件到 deploy/ 目录")
    print("  • 更新所有引用路径")
    print("  • 清理根目录")
    
    response = input("\n确定要重组项目结构吗？(y/n): ")
    if response.lower() != 'y':
        print("❌ 取消重组")
        return
    
    # 创建备份
    backup_dir = create_backup()
    
    # 执行重组
    restructure_project()
    
    # 显示新结构
    show_new_structure()
    
    print(f"\n💾 原文件已备份到: {backup_dir}")
    print("\n🎉 项目重组完成！根目录现在清爽多了！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 重组被中断")
    except Exception as e:
        print(f"\n❌ 重组失败: {e}")
        import traceback
        traceback.print_exc()
