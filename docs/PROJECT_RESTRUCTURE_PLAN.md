# RuleK 项目重构计划

## 📋 重构目标

1. **清理根目录**：将所有临时脚本、修复文件移到合适位置
2. **规范化目录结构**：每个文件都应有明确归属
3. **优化文件组织**：相关文件归类，便于维护
4. **移除冗余文件**：删除不必要的备份和临时文件

## 🗂️ 标准目录结构

```
RuleK/
├── .github/                    # GitHub配置
│   └── workflows/             # CI/CD工作流
├── config/                     # 配置文件
│   ├── config.json            # 主配置
│   └── settings/              # 其他设置
├── data/                       # 数据文件
│   ├── saves/                 # 游戏存档
│   └── templates/             # 模板数据
├── docs/                       # 文档
│   ├── api/                   # API文档
│   ├── design/                # 设计文档
│   ├── guides/                # 使用指南
│   └── reports/               # 各类报告
├── logs/                       # 日志文件
├── scripts/                    # 脚本工具
│   ├── dev/                   # 开发脚本
│   ├── test/                  # 测试脚本
│   ├── utils/                 # 工具脚本
│   └── deploy/                # 部署脚本
├── src/                        # 源代码
│   ├── api/                   # API接口
│   ├── ai/                    # AI功能
│   ├── core/                  # 核心功能
│   ├── models/                # 数据模型
│   └── utils/                 # 工具函数
├── tests/                      # 测试代码
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   └── fixtures/              # 测试数据
├── web/                        # Web界面
│   ├── backend/               # 后端代码
│   └── frontend/              # 前端代码
├── .env.example                # 环境变量示例
├── .gitignore                  # Git忽略文件
├── docker-compose.yml          # Docker配置
├── Dockerfile                  # Docker镜像
├── LICENSE                     # 许可证
├── README.md                   # 项目说明
├── requirements.txt            # Python依赖
└── rulek.py                    # 统一入口
```

## 🔄 重构步骤

### 第一阶段：备份和准备

1. **创建备份**（如需保留）
   ```bash
   mkdir -p .archive/$(date +%Y%m%d)
   cp -r . .archive/$(date +%Y%m%d)/
   ```

2. **评估.backups文件夹**
   - 如果已有Git版本控制，.backups通常不必要
   - 检查是否有重要文件未在Git中
   - 建议：归档后删除

### 第二阶段：文件迁移

#### 1. 脚本文件整理
```bash
# 开发脚本 → scripts/dev/
play.py → scripts/dev/play.py
play_cli.py → scripts/dev/play_cli.py
debug_rulek.py → scripts/dev/debug_rulek.py
smart_debug.py → scripts/dev/smart_debug.py

# 测试脚本 → scripts/test/
cli_test_runner.py → scripts/test/cli_test_runner.py
quick_test_cli.py → scripts/test/quick_test_cli.py
simple_test.py → scripts/test/simple_test.py
quick_cli_test.py → scripts/test/quick_cli_test.py

# 修复脚本 → scripts/fixes/（完成后可删除）
fix_syntax.py → scripts/fixes/fix_syntax.py
quick_fix.py → scripts/fixes/quick_fix.py
auto_test_fix.py → scripts/fixes/auto_test_fix.py
optimize_ai.py → scripts/fixes/optimize_ai.py

# 部署脚本 → scripts/deploy/
start.sh → scripts/deploy/start.sh
start.bat → scripts/deploy/start.bat
start_enhanced.sh → scripts/deploy/start_enhanced.sh
cleanup.sh → scripts/utils/cleanup.sh
make_executable.sh → scripts/utils/make_executable.sh
```

#### 2. 文档整理
```bash
# 修复报告 → docs/reports/fixes/
FIXED_AND_READY.md → docs/reports/fixes/
FIXES_COMPLETE.md → docs/reports/fixes/
debug_report.md → docs/reports/fixes/
test_fix_report.md → docs/reports/fixes/
quick_fix_report.txt → docs/reports/fixes/

# 指南文档 → docs/guides/
SMART_DEBUG_GUIDE.md → docs/guides/debug/

# 贡献指南保留在根目录
CONTRIBUTING.md → 保持不变
```

#### 3. 配置文件（保持在根目录）
- .env
- .env.example
- .gitignore
- docker-compose.yml
- Dockerfile
- nginx.conf
- pyproject.toml
- requirements.txt
- game.sh

### 第三阶段：引用更新

#### 1. 更新启动脚本引用
修改 `rulek.py` 中的路径引用：
```python
# 旧引用
from play_cli import main as play_cli_main

# 新引用
from scripts.dev.play_cli import main as play_cli_main
```

#### 2. 更新文档中的命令
所有文档中的命令需要更新：
```bash
# 旧命令
python play.py

# 新命令
python scripts/dev/play.py
# 或创建别名
python rulek.py play
```

#### 3. 更新测试引用
修改测试文件中的导入路径

### 第四阶段：清理

#### 1. 删除备份文件
```bash
# 删除所有 .backup 后缀文件
find . -name "*.backup" -delete

# 删除 .backups 文件夹（确认无重要文件后）
rm -rf .backups/
```

#### 2. 删除临时文件
```bash
# 删除 Python 缓存
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# 删除测试缓存
rm -rf .pytest_cache/
rm -rf htmlcov/
```

#### 3. 删除过时的修复脚本
完成重构后，`scripts/fixes/` 目录可以删除

## 📝 文件命名规范

1. **Python文件**
   - 使用小写字母和下划线：`game_state.py`
   - 测试文件前缀：`test_game_state.py`

2. **文档文件**
   - 使用大写字母和下划线：`PROJECT_PLAN.md`
   - 报告类：`REPORT_YYYYMMDD.md`

3. **配置文件**
   - 使用小写字母：`config.json`
   - 环境配置：`.env.environment`

## 🔧 自动化重构脚本

创建 `scripts/utils/restructure.py`：
```python
#!/usr/bin/env python3
"""
项目重构自动化脚本
"""
import os
import shutil
from pathlib import Path

# 文件迁移映射
FILE_MOVES = {
    'play.py': 'scripts/dev/play.py',
    'play_cli.py': 'scripts/dev/play_cli.py',
    # ... 添加更多映射
}

def restructure_project():
    """执行项目重构"""
    # 实现重构逻辑
    pass

if __name__ == "__main__":
    restructure_project()
```

## ⚠️ 注意事项

1. **版本控制**
   - 在重构前确保所有更改已提交
   - 使用分支进行重构：`git checkout -b restructure`

2. **依赖更新**
   - 更新所有导入路径
   - 运行测试确保功能正常

3. **文档同步**
   - 更新README中的项目结构说明
   - 更新所有文档中的文件路径引用

4. **逐步执行**
   - 先移动一类文件，测试无误后继续
   - 保持项目可运行状态

## 📊 重构检查清单

- [ ] 备份重要文件
- [ ] 创建重构分支
- [ ] 移动脚本文件到scripts/
- [ ] 移动文档到docs/
- [ ] 更新所有引用路径
- [ ] 删除.backup文件
- [ ] 清理缓存文件
- [ ] 运行完整测试套件
- [ ] 更新文档
- [ ] 合并到主分支

## 🎯 预期结果

重构完成后：
- 根目录只保留必要的配置文件和入口文件
- 所有脚本归类到scripts/目录
- 文档结构清晰，易于查找
- 项目结构符合Python最佳实践
- 便于新开发者理解和维护

---

*本计划适用于所有Python项目的重构，可根据具体需求调整*