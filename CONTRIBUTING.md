# 贡献指南

感谢你对规则怪谈管理者项目的关注！我们欢迎各种形式的贡献。

## 📋 贡献类型

- 🐛 **Bug修复**: 发现并修复bug
- ✨ **新功能**: 添加新的游戏功能
- 📚 **文档**: 改进或翻译文档
- 🎨 **UI/UX**: 改进界面和用户体验
- 🧪 **测试**: 添加测试用例
- 🔧 **重构**: 改进代码结构

## 🚀 开始贡献

### 1. Fork 项目

点击项目页面右上角的 "Fork" 按钮。

### 2. 克隆仓库

```bash
git clone https://github.com/你的用户名/rulek.git
cd rulek
```

### 3. 创建分支

```bash
git checkout -b feature/你的功能名
# 或
git checkout -b fix/修复的问题
```

### 4. 设置开发环境

```bash
# 安装依赖
pip install -r requirements.txt
cd web/frontend && npm install

# 运行测试确保环境正常
python rulek.py test
```

## 💻 开发规范

### 代码风格

- Python: 遵循 PEP 8，使用 `ruff` 进行格式化
- TypeScript/Vue: 使用项目配置的 ESLint 规则
- 提交前运行: `python scripts/dev_tools.py check`

### 提交信息格式

使用语义化的提交信息：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

示例：
```
feat(rule): 添加时间范围检查功能

- 实现了跨午夜时间范围判断
- 添加了完整的单元测试
- 更新了相关文档

Closes #123
```

### 测试要求

- 新功能必须包含测试用例
- 修改现有功能需要确保测试通过
- 测试覆盖率不应降低

### 文档要求

- 新功能需要更新相关文档
- API变更需要更新API文档
- 复杂功能需要添加使用示例

## 📝 Pull Request 流程

1. **确保代码质量**
   ```bash
   python scripts/dev_tools.py check
   ```

2. **更新文档**
   - 更新 README.md（如需要）
   - 更新相关技术文档
   - 添加/更新代码注释

3. **创建 Pull Request**
   - 使用清晰的标题描述你的更改
   - 在描述中说明：
     - 更改的原因
     - 实现方式
     - 测试方法
   - 关联相关的 Issue

4. **代码审查**
   - 耐心等待维护者审查
   - 积极回应审查意见
   - 根据反馈进行修改

## 🐛 报告问题

### 提交 Bug 报告

使用 Issue 模板，包含：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息（OS、Python版本等）
- 相关日志或截图

### 功能请求

- 描述功能需求
- 说明使用场景
- 提供可能的实现方案

## 🏗️ 项目结构说明

```
src/
├── core/          # 核心游戏逻辑
├── models/        # 数据模型
├── managers/      # 管理器类
└── api/           # API相关

web/
├── backend/       # FastAPI后端
└── frontend/      # Vue前端

tests/
├── unit/          # 单元测试
└── integration/   # 集成测试
```

## 🔧 开发工具

使用开发工具脚本：

```bash
# 格式化代码
python scripts/dev_tools.py format

# 运行类型检查
python scripts/dev_tools.py types

# 运行测试
python scripts/dev_tools.py test

# 生成测试覆盖率报告
python scripts/dev_tools.py coverage

# 清理项目
python scripts/dev_tools.py clean
```

## 📮 联系方式

- Issue: 项目Issue页面
- 讨论: GitHub Discussions
- 邮件: project-email@example.com

## 🙏 致谢

感谢所有贡献者！你们的每一份贡献都让项目变得更好。

---

**Happy Coding! 👻**
