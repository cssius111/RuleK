# RuleK 项目重构实施指南

## 📋 快速开始

### 1. 分析当前状态
```bash
python analyze_project.py
```

### 2. 查看重构计划
```bash
cat docs/PROJECT_RESTRUCTURE_PLAN.md
```

### 3. 执行重构
```bash
# 方式1：使用交互式脚本
./restructure.sh

# 方式2：直接执行
# 预览模式
python scripts/utils/restructure.py --dry-run

# 实际执行
python scripts/utils/restructure.py
```

## 🔍 关于 .backups 文件夹

### 是否需要保留？

**通常不需要**，如果：
- ✅ 项目使用 Git 版本控制
- ✅ 所有重要更改已提交
- ✅ 可以从 Git 历史恢复任何文件

**考虑保留**，如果：
- ⚠️ 有未提交的重要更改
- ⚠️ 包含不在版本控制中的配置文件
- ⚠️ 有手动创建的重要备份

### 检查方法
```bash
# 查看 .backups 内容
ls -la .backups/

# 检查是否有未在 Git 中的文件
find .backups -type f -exec git check-ignore {} \; -print
```

## 📝 重构步骤清单

### 准备阶段
- [ ] 提交所有当前更改：`git add -A && git commit -m "Before restructure"`
- [ ] 创建重构分支：`git checkout -b project-restructure`
- [ ] 运行项目分析：`python analyze_project.py`
- [ ] 备份重要文件（如需要）

### 执行阶段
- [ ] 预览重构计划：`python scripts/utils/restructure.py --dry-run`
- [ ] 确认无误后执行：`python scripts/utils/restructure.py`
- [ ] 检查移动结果
- [ ] 更新导入路径（根据生成的报告）

### 清理阶段
- [ ] 删除 .backups 目录（确认后）：`rm -rf .backups/`
- [ ] 清理缓存：`python scripts/utils/restructure.py --clean-only`
- [ ] 删除不再需要的文件

### 验证阶段
- [ ] 运行测试：`python rulek.py test`
- [ ] 测试主要功能
- [ ] 更新文档中的路径引用

### 完成阶段
- [ ] 提交更改：`git add -A && git commit -m "Project restructure complete"`
- [ ] 合并到主分支（如果一切正常）

## 🛠️ 手动清理命令

### 删除备份文件
```bash
# 删除所有 .backup 文件
find . -name "*.backup" -type f -delete

# 删除 .backups 目录
rm -rf .backups/
```

### 清理 Python 缓存
```bash
# 删除所有 __pycache__ 目录
find . -name "__pycache__" -type d -exec rm -rf {} +

# 删除所有 .pyc 文件
find . -name "*.pyc" -type f -delete

# 删除测试缓存
rm -rf .pytest_cache/
rm -rf htmlcov/
rm -f .coverage
```

### 清理系统文件
```bash
# macOS
find . -name ".DS_Store" -type f -delete

# 临时文件
find . -name "*~" -type f -delete
```

## ⚠️ 注意事项

1. **始终先预览**：使用 `--dry-run` 参数查看将要执行的操作
2. **分步执行**：可以先移动一部分文件，测试后再继续
3. **保持可运行**：每步操作后确保项目仍能正常运行
4. **更新引用**：移动文件后记得更新所有引用路径

## 📊 预期结果

重构完成后的目录结构：
```
RuleK/
├── config/          # 配置文件
├── data/            # 数据文件
├── docs/            # 所有文档
├── logs/            # 日志
├── scripts/         # 所有脚本
│   ├── dev/        # 开发工具
│   ├── test/       # 测试脚本
│   └── utils/      # 工具脚本
├── src/             # 源代码
├── tests/           # 测试代码
├── web/             # Web界面
└── rulek.py         # 主入口
```

根目录将只保留：
- 配置文件（.env, .gitignore等）
- 构建文件（Dockerfile, requirements.txt等）
- 文档文件（README.md, LICENSE等）
- 主入口（rulek.py）

---

执行重构后，项目将更加整洁、易于维护！
