# RuleK 快速参考手册

## 🎮 项目概述

规则怪谈管理者（RuleK）是一个基于规则触发的恐怖生存游戏，玩家扮演诡异空间的管理者，通过创建规则来收割恐惧。

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository_url>
cd RuleK

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 添加 DEEPSEEK_API_KEY
```

### 2. 运行游戏

#### 统一入口
```bash
# CLI 模式
python rulek.py cli

# Web 模式
python rulek.py web

# 演示模式
python rulek.py demo
```

#### 快捷脚本
```bash
# Linux/Mac
./start.sh

# Windows  
start.bat

# 纯 CLI 游戏
python play_cli.py
```

## 📁 项目结构

```
RuleK/
├── rulek.py          # 统一入口
├── src/              # 核心代码
│   ├── core/        # 游戏核心系统
│   ├── models/      # 数据模型
│   ├── api/         # AI接口（DeepSeek）
│   └── ai/          # AI功能实现
├── web/              # Web界面
├── tests/            # 测试套件
├── docs/             # 文档
└── config/           # 配置文件
```

## 🔧 核心组件

### GameStateManager
游戏状态管理器，管理整个游戏的状态。

```python
from src.core.game_state import GameStateManager

# 创建游戏
game_mgr = GameStateManager()
game_mgr.new_game("my_game")

# 访问组件
game_mgr.state         # 游戏状态
game_mgr.rules         # 规则列表 ⚠️ 不是 game_mgr.state.rules
game_mgr.npcs          # NPC列表
```

### AI 功能
```python
# 启用 AI
game_mgr.ai_enabled = True

# 初始化 AI（异步）
await game_mgr.init_ai_pipeline()

# 运行 AI 回合
plan = await game_mgr.run_ai_turn()

# 生成叙事
narrative = await game_mgr.generate_narrative()

# 评估自然语言规则
result = await game_mgr.evaluate_rule_nl("晚上不能开灯")
```

## ⚠️ 常见问题

### 1. AttributeError: 'GameState' object has no attribute 'rules'
**解决方案**：使用 `game_mgr.rules` 而不是 `game_mgr.state.rules`

### 2. AI 功能不工作
**解决方案**：
- 确保设置了 `DEEPSEEK_API_KEY` 环境变量
- 确保 `game_mgr.ai_enabled = True`
- 在异步环境中调用 AI 方法

### 3. 导入错误
**解决方案**：
- 从项目根目录运行
- 使用 `python rulek.py` 而不是直接运行子模块

## 🧪 测试

```bash
# 运行所有测试
python rulek.py test

# 只运行单元测试
python rulek.py test unit

# 验证环境
python rulek.py verify
```

## 📚 文档

- [完整文档索引](docs/INDEX.md)
- [游戏设计文档](docs/game_design/game_design_v0.2.md)
- [AI集成指南](docs/AI_Integration_Implementation_Guide.md)
- [API文档](http://localhost:8000/docs) (Web模式运行时)

## 🛠️ 开发

### 添加新功能
1. 在相应的模块中添加代码
2. 添加测试
3. 更新文档
4. 运行测试确保通过

### 目录说明
- `src/core/`: 核心游戏逻辑
- `src/models/`: 数据模型定义
- `src/api/`: 外部API集成
- `src/ai/`: AI功能实现
- `web/`: Web界面相关

---
*更新时间：2024-12-20*
