# RuleK - 规则怪谈管理者 🎮

一个恐怖生存游戏，玩家扮演诡异空间的管理者，通过创建规则来收割恐惧。

## 🚀 快速开始 - 统一入口

### ✨ 新！统一管理入口 v2.0

RuleK现在提供了多种启动方式：

```bash
# 方式1: 快速启动（自动打开浏览器） 🆕
🔥 python scripts/quick_start.py

# 方式2: 交互式菜单（推荐新手）
python rulek.py

# 方式3: 直接启动完整游戏
python rulek.py start

# 查看所有命令
python rulek.py help
```
> `rulek.py` 现仅负责参数解析和调度，实际功能由 `scripts/` 模块实现，命令用法保持不变。

### 📋 交互式菜单

运行 `python rulek.py` 进入交互式菜单：

```
╔══════════════════════════════════════════════════════════╗
║              🎮 RuleK - 规则怪谈管理者 🎮              ║
║                    统一管理入口 v2.0                     ║
╚══════════════════════════════════════════════════════════╝

请选择操作:

  [1] 🎮 启动完整游戏        前端+后端
  [2] 🔧 启动Web API         仅后端服务
  [3] 🎨 启动前端界面        仅前端服务
  [4] 💻 启动CLI游戏         命令行版本
  ----------------------------------------
  [5] 🧪 运行测试            完整测试套件
  [6] 🔍 诊断系统            检查环境和依赖
  [7] 🔧 修复问题            自动修复常见问题
  [8] 🧹 清理项目            清理缓存和临时文件
  ----------------------------------------
  [9] 📚 查看文档            项目文档
  [0] 📊 项目状态            查看项目信息
  ----------------------------------------
  [h] ❓ 帮助                命令行帮助
  [q] 👋 退出                退出程序
```

### 🎯 命令行模式

所有功能都可以通过命令行直接访问：

```bash
# 游戏相关
python rulek.py start      # 启动完整游戏（前端+后端）
python rulek.py web        # 仅启动后端API
python rulek.py frontend   # 仅启动前端界面
python rulek.py cli        # 启动命令行版游戏

# 开发工具
python rulek.py test       # 运行测试套件
python rulek.py diagnose   # 诊断系统问题
python rulek.py fix        # 自动修复常见问题
python rulek.py clean      # 清理项目缓存

# 信息查看
python rulek.py status     # 查看项目状态
python rulek.py docs       # 查看文档
python rulek.py help       # 显示帮助信息
```

## 📋 系统要求

- Python 3.10+
- Node.js 16+
- npm 或 yarn

## 📦 安装依赖

### 自动安装（推荐）
```bash
python rulek.py fix    # 自动安装所有依赖
```

### 手动安装

#### Python依赖
```bash
pip install -r requirements.txt
```

#### 前端依赖
```bash
cd web/frontend
npm install
```

## ⚙️ 配置

项目使用 `src/utils/config.py` 统一加载 `.env` 与 `config/config.json`。

1. 复制 `.env.example` 为 `.env` 并填写必要参数：
   ```bash
   cp .env.example .env
   ```
   建议在生产环境通过 CI Secrets 等安全方式存储 API Key。

2. 根据需求修改 `config/config.json`。

在代码中可以这样访问配置：

```python
from src.utils.config import config

deepseek = config.get_deepseek_config()
web = config.get_web_config()
```

## 🗂️ 项目结构
```
RuleK/
├── rulek.py       # 🚀 统一入口程序
├── src/           # 游戏核心逻辑
│   ├── core/      # 核心系统
│   ├── models/    # 数据模型
│   └── api/       # API接口
├── web/
│   ├── backend/   # FastAPI后端
│   └── frontend/  # Vue3前端
├── scripts/       # 工具脚本
├── tests/         # 测试用例
├── docs/          # 项目文档
└── config/        # 配置文件
```

## 🎮 游戏特色

- **规则创建系统**: 创建各种诡异规则来控制NPC
- **AI驱动**: 智能NPC行为和对话生成
- **恐怖氛围**: 沉浸式的恐怖游戏体验
- **多结局**: 根据玩家选择产生不同结局

## 🎆 游戏操作指南

### 创建规则的正确方式

1. **启动游戏**
   ```bash
   python scripts/quick_start.py  # 推荐，自动打开浏览器
   ```

2. **创建新游戏**
   - 点击主页的"新游戏"按钮
   - 选择难度和NPC数量

3. **创建规则**
   - 在游戏页面点击**"创建规则"按钮**
   - 选择创建方式：
     - 📚 **使用模板**: 从预设的恐怖规则模板快速创建
     - ✏️ **自定义规则**: 手动配置规则的触发条件和效果
     - 🤖 **AI解析**: 用自然语言描述，让AI帮你生成规则

### ⚠️ 重要提示

- ❌ **错误**: 直接访问 `http://localhost:5173/game/create-rule`
- ✅ **正确**: 在游戏内点击"创建规则"按钮
- 💡 **说明**: 规则创建是游戏内的模态框功能，不是独立页面

### 快捷键

- `空格` - 推进回合
- `R` - 打开规则创建面板
- `S` - 快速保存
- `Esc` - 关闭弹窗

## 🔧 故障排查

### 使用诊断工具
```bash
python rulek.py diagnose   # 自动诊断所有问题
python rulek.py fix        # 自动修复常见问题
```

### 常见问题

#### 后端无法启动
1. 运行 `python rulek.py diagnose` 检查问题
2. 运行 `python rulek.py fix` 自动修复
3. 检查端口8000是否被占用

#### 前端无法启动
1. 确保Node.js已安装: `node --version`
2. 运行 `python rulek.py fix` 安装依赖
3. 检查端口5173是否被占用

#### 页面空白或报错
1. 运行 `python rulek.py status` 检查服务状态
2. 确保后端已启动（http://localhost:8000）
3. 确保前端已启动（http://localhost:5173）

## 📝 开发指南

### 运行测试
```bash
python rulek.py test
```

### 清理项目
```bash
python rulek.py clean
```

### 查看项目状态
```bash
python rulek.py status
```

## 📚 文档

- [项目计划](PROJECT_PLAN.md)
- [开发规范](MAIN_AGENT.md)
- [项目结构](PROJECT_STRUCTURE.md)
- [AI协作指南](AGENT.md)

## 📄 许可证

MIT License

---

**提示**: 推荐使用 `python rulek.py` 交互式菜单，它提供了所有功能的便捷访问！

如有问题，请查看 `docs/` 目录下的详细文档。
