#!/usr/bin/env python3
"""
项目清理工具 - 移除临时文件和过时内容
"""
import os
import shutil
import sys
from pathlib import Path

# 调整路径到项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 需要清理的文件列表
FILES_TO_REMOVE = [
    # 临时修复脚本
    "auto_fix_and_start.py",
    "fix_and_start.py",
    "fix_encoding_issue.py",
    "fix_imports_and_start.py",
    "emergency_fix.py",
    "patch_encoding.py",
    "detect_issues.py",
    "diagnose.py",
    "safe_start.py",
    "smart_start.py",
    "go.py",
    "run.py",
    "check.py",
    "verify_fix.py",
    "verify_fixes.py",
    "analyze_project.py",
    
    # 临时测试文件
    "test_complete.py",
    "test_imports.py",
    "test_encoding_fix.py",
    "test_fixed.py",
    "test_startup.py",
    "quick_test.py",
    "simple_test.py",
    "simple_check.py",
    "basic_check.py",
    "quick_verify.py",
    "final_test.py",
    "final_verification.py",
    "run_all_tests.py",
    "run_basic_tests.py",
    
    # 过时的文档
    "FIXED_README.md",
    "FIX_COMPLETE.md",
    "SOLUTION_SUMMARY.md",
    "START_NOW.md",
    "ENCODING_FIX_REPORT.md",
    "FINAL_TEST_SUMMARY.md",
    "PROJECT_TEST_REPORT.md",
    "TEST_SUMMARY_FINAL.md",
    "RESTRUCTURE_SUMMARY.md",
    "QUICK_TEST_GUIDE.md",
    
    # 临时脚本
    "setup_permissions.sh",
    "restructure.sh",
    
    # 批处理文件（保留主要的）
    "quick_start.bat",
    "quick_start.sh",
]

# 需要保留的核心文件
CORE_FILES = [
    # 主入口
    "rulek.py",
    "start_web_server.py",
    
    # 管理工具
    "manage.py",
    "cleanup_project.py",
    "project_status.py",
    "clean.py",
    
    # 配置文件
    "requirements.txt",
    "pyproject.toml",
    ".env",
    ".env.example",
    ".gitignore",
    
    # 文档
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "CLEANUP_GUIDE.md",
    "CLEANUP_COMPLETE.md",
    "START.md",
    
    # Docker相关
    "docker-compose.yml",
    "Dockerfile",
    "nginx.conf",
    
    # 启动脚本
    "start.sh",
    "start.bat",
]

# 核心目录
CORE_DIRS = [
    "src",
    "web",
    "config",
    "data",
    "logs",
    "tests",
    "docs",
    "scripts",
    ".git",
    ".github",
]

def create_backup():
    """创建清理前的备份"""
    backup_dir = PROJECT_ROOT / ".backups" / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 备份要删除的文件
    backed_up = []
    for file in FILES_TO_REMOVE:
        file_path = PROJECT_ROOT / file
        if file_path.exists():
            backup_path = backup_dir / file
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            backed_up.append(file)
    
    if backed_up:
        print(f"✅ 已备份 {len(backed_up)} 个文件到: {backup_dir}")
    
    return backup_dir

def clean_files():
    """清理不必要的文件"""
    print("\n🧹 开始清理文件...")
    
    removed_count = 0
    for file in FILES_TO_REMOVE:
        file_path = PROJECT_ROOT / file
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"   ✅ 删除: {file}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ 无法删除 {file}: {e}")
    
    print(f"\n✅ 共删除 {removed_count} 个文件")
    
    return removed_count

def clean_pycache():
    """清理Python缓存"""
    print("\n🧹 清理Python缓存...")
    
    cache_count = 0
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_path = Path(root) / dir_name
                try:
                    shutil.rmtree(cache_path)
                    cache_count += 1
                except:
                    pass
    
    print(f"✅ 清理了 {cache_count} 个缓存目录")
    
    return cache_count

def clean_test_results():
    """清理测试结果目录"""
    test_results_dir = PROJECT_ROOT / "test_results"
    if test_results_dir.exists():
        try:
            shutil.rmtree(test_results_dir)
            print("✅ 清理了 test_results 目录")
            return True
        except:
            print("❌ 无法清理 test_results 目录")
            return False
    return False

def organize_docs():
    """整理文档"""
    print("\n📚 整理文档...")
    
    # 清理docs目录中的过时文档
    docs_to_clean = [
        "docs/QUICK_START_GAME.md",
        "docs/RUN_GAME_NOW.md",
    ]
    
    for doc in docs_to_clean:
        doc_path = PROJECT_ROOT / doc
        if doc_path.exists():
            try:
                doc_path.unlink()
                print(f"   ✅ 删除过时文档: {doc}")
            except:
                pass
    
    # 清理空的reports目录
    reports_dir = PROJECT_ROOT / "docs" / "reports"
    if reports_dir.exists():
        try:
            # 检查是否为空或只有无用文件
            fixes_dir = reports_dir / "fixes"
            if fixes_dir.exists() and fixes_dir.is_dir():
                shutil.rmtree(fixes_dir)
            
            # 删除restructure_report.json
            report_file = reports_dir / "restructure_report.json"
            if report_file.exists():
                report_file.unlink()
            
            # 如果目录空了就删除
            if not list(reports_dir.iterdir()):
                reports_dir.rmdir()
                print("   ✅ 清理了空的reports目录")
        except:
            pass

def create_clean_readme():
    """创建一个干净的README"""
    readme_content = """# RuleK - 规则怪谈管理者

## 🎮 项目简介

RuleK 是一个基于规则触发的恐怖生存游戏，玩家扮演诡异空间的管理者，通过创建规则来收割恐惧。

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+ (可选，用于前端开发)

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务器

#### 方式1：Python脚本
```bash
python start_web_server.py
```

#### 方式2：Shell脚本
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

#### 方式3：统一入口
```bash
python rulek.py web
```

### 访问游戏
- 主页: http://localhost:8000
- API文档: http://localhost:8000/docs
- 交互式文档: http://localhost:8000/redoc

## 📁 项目结构

```
RuleK/
├── src/              # 核心游戏逻辑
│   ├── core/        # 游戏核心系统
│   ├── models/      # 数据模型
│   ├── api/         # AI接口
│   └── ai/          # AI功能实现
├── web/              # Web界面
│   ├── backend/     # FastAPI后端
│   └── frontend/    # Vue前端
├── config/          # 配置文件
├── data/            # 游戏数据
├── tests/           # 测试用例
├── docs/            # 项目文档
└── scripts/         # 工具脚本
```

## 🎯 游戏特色

- **规则创建系统**: 玩家可以创建各种诡异规则
- **AI驱动**: 智能NPC行为和对话生成
- **恐怖氛围**: 沉浸式的恐怖游戏体验
- **多结局**: 根据玩家选择产生不同结局

## 🛠️ 开发

### 运行测试
```bash
pytest tests/
```

### Docker部署
```bash
docker-compose up -d
```

## 📚 文档

详细文档请查看 [docs/INDEX.md](docs/INDEX.md)

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

*享受恐怖规则的创造之旅！* 🎭
"""
    
    readme_path = PROJECT_ROOT / "README.md"
    
    # 备份原README
    if readme_path.exists():
        backup_path = PROJECT_ROOT / ".backups" / "README.md.backup"
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(readme_path, backup_path)
    
    # 写入新README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ 更新了 README.md")

def show_summary():
    """显示清理后的项目结构"""
    print("\n" + "="*60)
    print("📊 清理完成后的项目结构")
    print("="*60)
    
    print("\n✅ 保留的核心入口:")
    print("  - rulek.py (主入口)")
    print("  - start_web_server.py (Web服务器)")
    print("  - start.sh / start.bat (快捷启动)")
    
    print("\n✅ 核心目录:")
    for dir_name in CORE_DIRS:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists():
            print(f"  - {dir_name}/")
    
    print("\n✅ 启动方式:")
    print("  1. python start_web_server.py")
    print("  2. python rulek.py web")
    print("  3. ./start.sh (Linux/Mac)")
    print("  4. start.bat (Windows)")

def main():
    print("""
╔══════════════════════════════════════════════════╗
║           RuleK 项目清理工具                    ║
╚══════════════════════════════════════════════════╝
    """)
    
    # 确认清理
    print("⚠️  警告: 这将删除所有临时修复脚本和过时文档！")
    print("   (会先创建备份)")
    
    response = input("\n确定要清理吗？(y/n): ")
    if response.lower() != 'y':
        print("❌ 取消清理")
        return
    
    # 创建备份
    backup_dir = create_backup()
    
    # 执行清理
    removed_files = clean_files()
    cache_cleaned = clean_pycache()
    test_results_cleaned = clean_test_results()
    
    # 整理文档
    organize_docs()
    
    # 更新README
    create_clean_readme()
    
    # 显示总结
    show_summary()
    
    print("\n" + "="*60)
    print("✅ 清理完成！")
    print(f"   - 删除了 {removed_files} 个临时文件")
    print(f"   - 清理了 {cache_cleaned} 个缓存目录")
    if test_results_cleaned:
        print("   - 清理了测试结果目录")
    print(f"   - 备份位置: {backup_dir}")
    print("="*60)
    
    print("\n💡 提示:")
    print("  - 如需恢复文件，请查看 .backups 目录")
    print("  - 现在可以使用 'python start_web_server.py' 启动服务器")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 清理被中断")
    except Exception as e:
        print(f"\n❌ 清理失败: {e}")
        import traceback
        traceback.print_exc()
