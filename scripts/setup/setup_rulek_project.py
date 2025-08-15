#!/usr/bin/env python3
"""
RuleK 项目专业化设置脚本
一键设置专业的项目结构
"""

import os
import sys
from pathlib import Path

def create_makefile():
    """创建 Makefile"""
    content = '''# RuleK Project Makefile

.PHONY: help serve test clean install web cli manage

help:
	@echo "╔══════════════════════════════════════════╗"
	@echo "║         RuleK 项目任务管理                ║"
	@echo "╚══════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 运行命令:"
	@echo "  make serve   - 启动Web服务器"
	@echo "  make web     - 启动Web服务器(同serve)"
	@echo "  make cli     - 启动CLI游戏"
	@echo "  make manage  - 项目管理工具"
	@echo ""
	@echo "🧪 开发命令:"
	@echo "  make test    - 运行测试"
	@echo "  make clean   - 清理缓存文件"
	@echo "  make install - 安装依赖"
	@echo ""
	@echo "💡 提示: 也可以使用 python rulek.py [命令]"

serve:
	@echo "🚀 启动Web服务器..."
	@python start_web_server.py

web:
	@python rulek.py web

cli:
	@python rulek.py cli

test:
	@echo "🧪 运行测试..."
	@python rulek.py test

manage:
	@echo "🔧 打开项目管理..."
	@python rulek.py manage

clean:
	@echo "🧹 清理缓存文件..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@find . -type f -name "*~" -delete 2>/dev/null || true
	@echo "✅ 清理完成！"

install:
	@echo "📦 安装依赖..."
	@pip install -r requirements.txt
	@echo "✅ 安装完成！"

# 快捷命令
s: serve
w: web
c: cli
t: test
m: manage
'''
    
    with open('Makefile', 'w') as f:
        f.write(content)
    print("✅ Makefile 已创建")

def create_project_plan():
    """创建项目计划"""
    content = '''# RuleK 项目计划

## 🎯 当前状态

### 已完成功能
- ✅ CLI游戏完整实现
- ✅ Web基础版本上线
- ✅ AI集成第三阶段完成
- ✅ 统一入口 rulek.py

### 进行中
- 🔄 Web端AI核心化改造（第一阶段完成，第二阶段30%）
- 🔄 WebSocket流式推送实现

## 📋 下一步任务

### 本周任务
1. [ ] 完成WebSocket流式改造
2. [ ] 实现断线重连机制
3. [ ] 添加心跳机制
4. [ ] 前端组件改造

### 使用方法

#### 启动项目
```bash
# 使用 Makefile（推荐）
make serve      # 启动Web服务器
make cli        # 启动CLI游戏
make test       # 运行测试

# 或使用 rulek.py
python rulek.py web
python rulek.py cli
python rulek.py test
```

## 📊 性能目标

| 指标 | 当前 | 目标 |
|------|------|------|
| API响应时间 | 5-10s | <0.5s |
| AI生成时间 | 5-8s | <2s |
| 缓存命中率 | 0% | >70% |

---
*更新时间：2024-12-22*
'''
    
    with open('PROJECT_PLAN.md', 'w') as f:
        f.write(content)
    print("✅ PROJECT_PLAN.md 已创建")

def create_agent_guide():
    """创建AI协作指南"""
    content = '''# AI 协作指南

## 📋 项目信息

项目名：RuleK - 规则怪谈管理者
语言：Python 3.10+
框架：FastAPI + Vue 3

## 🎯 代码规范

### Python代码
- 遵循 PEP 8
- 使用类型注解
- 编写docstring
- 异步优先

### 提交格式
```
<type>(<scope>): <subject>

feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试相关
```

## 💻 项目结构

```
RuleK/
├── src/            # 源代码
├── web/            # Web界面
├── tests/          # 测试代码
├── docs/           # 文档
├── config/         # 配置
└── rulek.py        # 主入口
```

## 🚀 开发流程

1. 理解需求
2. 编写测试
3. 实现功能
4. 运行测试
5. 提交代码

## ⚠️ 注意事项

- 不要删除现有功能
- 保持向后兼容
- 添加适当的错误处理
- 更新相关文档

---
*AI助手请遵循此指南*
'''
    
    with open('AGENT.md', 'w') as f:
        f.write(content)
    print("✅ AGENT.md 已创建")

def create_scripts_directory():
    """创建脚本目录和文件"""
    os.makedirs('scripts', exist_ok=True)
    
    # 创建清理脚本
    clean_script = '''#!/usr/bin/env python3
"""项目清理脚本"""
import os
import shutil
from pathlib import Path

def clean_project():
    """清理项目临时文件"""
    patterns = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "*.pyc",
        "*.pyo",
        ".DS_Store",
        ".coverage",
        "htmlcov",
        "*~"
    ]
    
    print("🧹 开始清理项目...")
    count = 0
    
    for pattern in patterns:
        for path in Path(".").rglob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                count += 1
                print(f"  删除: {path}")
            except:
                pass
    
    print(f"✅ 清理完成！删除了 {count} 个文件/目录")

if __name__ == "__main__":
    clean_project()
'''
    
    with open('scripts/clean.py', 'w') as f:
        f.write(clean_script)
    
    # 创建状态检查脚本
    status_script = '''#!/usr/bin/env python3
"""项目状态检查脚本"""
import os
from pathlib import Path

def check_status():
    """检查项目状态"""
    print("📊 RuleK 项目状态")
    print("=" * 40)
    
    # 检查关键文件
    files = [
        'rulek.py',
        'start_web_server.py',
        'requirements.txt',
        'Makefile',
        'README.md'
    ]
    
    print("📁 关键文件检查:")
    for file in files:
        status = "✅" if Path(file).exists() else "❌"
        print(f"  {status} {file}")
    
    # 检查目录
    dirs = ['src', 'web', 'tests', 'docs', 'config', 'scripts']
    print("\\n📂 目录结构检查:")
    for dir_name in dirs:
        status = "✅" if Path(dir_name).exists() else "❌"
        print(f"  {status} {dir_name}/")
    
    # 统计Python文件
    py_files = list(Path(".").rglob("*.py"))
    print(f"\\n📊 Python文件数量: {len(py_files)}")
    
    # 检查缓存文件
    cache_dirs = list(Path(".").rglob("__pycache__"))
    print(f"🗑️  缓存目录数量: {len(cache_dirs)}")
    
    if cache_dirs:
        print("   提示: 运行 'make clean' 清理缓存")

if __name__ == "__main__":
    check_status()
'''
    
    with open('scripts/status.py', 'w') as f:
        f.write(status_script)
    
    print("✅ scripts/ 目录已创建")

def create_readme_update():
    """更新README的快速开始部分"""
    quick_start = '''
## 🚀 快速开始（更新版）

### 使用 Makefile（推荐）
```bash
# 查看所有命令
make help

# 启动Web服务器
make serve

# 启动CLI游戏
make cli

# 运行测试
make test

# 清理缓存
make clean
```

### 使用 rulek.py
```bash
python rulek.py web     # 启动Web服务器
python rulek.py cli     # 启动CLI游戏
python rulek.py test    # 运行测试
python rulek.py manage  # 管理工具
```
'''
    
    # 检查是否有README
    if Path('README.md').exists():
        print("ℹ️  README.md 已存在，请手动添加以下内容:")
        print("-" * 40)
        print(quick_start)
        print("-" * 40)
    else:
        with open('README_QUICKSTART.md', 'w') as f:
            f.write(quick_start)
        print("✅ README_QUICKSTART.md 已创建")

def main():
    """主函数"""
    print("=" * 50)
    print("🚀 RuleK 项目专业化设置")
    print("=" * 50)
    
    # 检查是否在RuleK目录
    if not Path('rulek.py').exists():
        print("❌ 错误：请在RuleK项目根目录运行此脚本！")
        print("   当前目录:", os.getcwd())
        print("   需要文件: rulek.py")
        sys.exit(1)
    
    print("📁 当前目录:", os.getcwd())
    print()
    
    # 创建文件
    create_makefile()
    create_project_plan()
    create_agent_guide()
    create_scripts_directory()
    create_readme_update()
    
    print()
    print("=" * 50)
    print("✅ 设置完成！")
    print("=" * 50)
    print()
    print("🎯 现在你可以使用:")
    print("  make help    - 查看所有命令")
    print("  make serve   - 启动Web服务器")
    print("  make cli     - 启动CLI游戏")
    print("  make clean   - 清理缓存")
    print()
    print("📊 检查项目状态:")
    print("  python scripts/status.py")
    print()
    print("🧹 清理项目:")
    print("  python scripts/clean.py")
    print("  或: make clean")
    print()
    print("享受你的专业化项目！🎉")

if __name__ == "__main__":
    main()
