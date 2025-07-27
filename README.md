# 规则怪谈管理者 (RuleK) 🎮

<div align="center">

[![CI Status](https://github.com/yourusername/rulek/workflows/CI/badge.svg)](https://github.com/yourusername/rulek/actions)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Vue Version](https://img.shields.io/badge/vue-3.3+-green.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**创造规则，收割恐惧，主宰命运**

[在线演示](#) | [文档](docs/) | [快速开始](#快速开始) | [开发指南](docs/guides/)

</div>

---

## 📖 游戏简介

在《规则怪谈管理者》中，你将扮演一个诡异空间的幕后主宰。通过消耗恐惧积分创造致命规则，操纵NPC的命运，收集更多恐惧能量。你既可以在幕后观察，也可以亲自下场引导剧情。

### 核心特性

- 🎯 **双模式玩法**：幕后管理 + 亲自下场
- 📜 **规则创造系统**：自定义触发条件和死亡效果
- 🤖 **智能NPC**：基于AI的动态对话和行为决策
- 📖 **叙事生成**：将游戏事件转化为恐怖小说
- 🌐 **多端支持**：命令行、Web界面、API接口

## 🚀 快速开始

### 方式一：一键启动（推荐）

```bash
# macOS/Linux
./start.sh

# Windows
start.bat
```

### 方式二：分别启动

```bash
# 1. 安装依赖
pip install -r requirements.txt
cd web/frontend && npm install

# 2. 启动后端
python rulek.py web

# 3. 启动前端（新终端）
cd web/frontend && npm run dev
```

访问 http://localhost:5173 开始游戏！

### 方式三：Docker

```bash
# 开发环境
docker-compose --profile dev up

# 生产环境
docker-compose --profile prod up
```

## 🎮 游戏模式

### 命令行模式
```bash
python rulek.py cli
```

### 演示模式
```bash
python rulek.py demo
```

### Web模式
```bash
python rulek.py web
```

## 🏗️ 项目结构

```
RuleK/
├── src/                    # 核心游戏逻辑
│   ├── core/              # 核心系统
│   ├── models/            # 数据模型
│   ├── managers/          # 管理器
│   └── api/               # API接口
├── web/                   # Web应用
│   ├── backend/          # FastAPI后端
│   └── frontend/         # Vue3前端
├── tests/                # 测试套件
├── docs/                 # 文档
└── rulek.py             # 统一入口
```

## 🛠️ 技术栈

### 后端
- Python 3.10+
- FastAPI
- Pydantic
- DeepSeek API

### 前端
- Vue 3
- TypeScript
- Vite
- Pinia

### 部署
- Docker
- Nginx
- GitHub Actions

## 📚 文档

- [快速开始指南](docs/guides/Quick_Start_Guide.md)
- [游戏设计文档](docs/game_design/game_design_v0.2.md)
- [API文档](http://localhost:8000/docs)
- [开发计划](docs/MCP_Development_Plan.md)

## 🧪 测试

```bash
# 运行所有测试
python rulek.py test

# 运行单元测试
python rulek.py test unit

# 运行集成测试
python rulek.py test integration
```

## 🔧 配置

### 环境变量

创建 `.env` 文件：

```env
DEEPSEEK_API_KEY=your_api_key_here
LOG_LEVEL=INFO  # 也可以使用數字值，例如 20
DEBUG=False
```

### 游戏配置

编辑 `config/config.json`：

```json
{
  "game": {
    "initial_fear_points": 1000,
    "max_npcs": 6,
    "default_difficulty": "normal"
  }
}
```

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md)。

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 了解详情。

## 🙏 致谢

- DeepSeek 提供的 AI 能力支持
- Vue.js 团队的优秀框架
- 所有贡献者和测试者

## 📞 联系方式

- Issue: [GitHub Issues](https://github.com/yourusername/rulek/issues)
- Email: your-email@example.com

---

<div align="center">
  <p>Made with ❤️ and 👻</p>
  <p>© 2024 RuleK Team</p>
</div>
