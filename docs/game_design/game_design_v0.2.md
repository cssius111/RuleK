# 规则怪谈管理者 (RuleK)

> 一款AI驱动的恐怖规则管理游戏，让你扮演幕后黑手，通过制定诡异的规则来收集恐惧值。

## 🎮 游戏特色

- **双重身份**：既可作为管理者制定规则，也可亲自下场参与
- **AI驱动**：智能NPC对话和动态叙事生成
- **丰富规则库**：12+种独特的恐怖规则模板
- **随机事件**：10+种环境和超自然事件
- **地图系统**：6个互联区域的探索空间
- **心理系统**：NPC的恐惧、理智、信任度动态变化

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository_url>
cd RuleK

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API（可选）

如果想使用真实的AI对话功能：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的DeepSeek API密钥
# DEEPSEEK_API_KEY=your_api_key_here
```

> 没有API密钥？游戏会自动使用Mock模式，仍可正常游玩！

### 3. 运行游戏

```bash
# 运行主游戏（推荐）
python main_game_v2.py

# 或运行快速演示
python scripts/demo_sprint2.py
```

## 📁 项目结构

```
RuleK/
├── src/                    # 源代码
│   ├── api/               # API客户端
│   ├── core/              # 核心游戏逻辑
│   ├── models/            # 数据模型
│   ├── ui/                # 用户界面
│   └── utils/             # 工具函数
├── tests/                  # 测试文件
│   ├── unit/              # 单元测试
│   └── integration/       # 集成测试
├── scripts/                # 脚本文件
│   ├── demo_sprint2.py    # Sprint 2功能演示
│   └── run_tests.py       # 测试运行器
├── data/                   # 游戏数据
│   ├── saves/             # 存档文件
│   └── cache/             # API缓存
├── docs/                   # 文档
│   ├── guides/            # 使用指南
│   └── sprints/           # 开发文档
├── config/                 # 配置文件
└── web/                    # Web UI（开发中）
```

## 🧪 运行测试

```bash
# 运行测试脚本（推荐）
python scripts/run_tests.py

# 或直接使用pytest
pytest tests/

# 运行覆盖率测试
python -m coverage run -m pytest tests/
python -m coverage report
```

## 🎯 游戏玩法

1. **创建规则**：花费恐惧值创建各种诡异的规则
2. **观察NPC**：看他们在恐怖环境中的反应
3. **收集恐惧**：通过规则触发和事件获得恐惧值
4. **升级体系**：用恐惧值创建更强大的规则
5. **达成目标**：在NPC全灭前收集足够的恐惧值

## 📖 文档

- [快速开始指南](docs/guides/Quick_Start_Guide.md)
- [游戏演示指南](docs/guides/GAME_DEMO_GUIDE.md)
- [Sprint 2 功能总结](docs/sprints/SPRINT_2_SUMMARY.md)
- [Web UI 开发计划](docs/sprints/SPRINT_3_PLAN.md)

## 🛠️ 开发

### 添加新规则

编辑 `src/models/rule.py` 中的 `RULE_TEMPLATES`：

```python
"your_rule_id": {
    "name": "规则名称",
    "description": "规则描述",
    "trigger": {...},
    "effect": {...},
    "base_cost": 100
}
```

### 添加新事件

编辑 `src/core/event_system.py`，在 `_initialize_default_events` 中添加。

### 扩展地图

使用 `src/models/map.py` 中的 `MapManager` 创建新地图。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 许可证

[待定]

## 🙏 致谢

- 使用 DeepSeek API 提供 AI 功能
- 灵感来自各种规则怪谈作品

---

**当前版本**: Sprint 2 完成 | **下一步**: Web UI 开发中

享受你的恐怖管理之旅！ 👻
