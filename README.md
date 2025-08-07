# RuleK - 规则怪谈管理者

## 🎮 项目简介

RuleK 是一个基于规则触发的恐怖生存游戏，玩家扮演诡异空间的管理者，通过创建规则来收割恐惧。

## 🚀 快速开始

### 环境要求
- Python 3.10+ (CI 测试于 3.10、3.11、3.12)
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


### 预提交钩子

项目根目录包含唯一的预提交配置文件 `.pre-commit-config.yaml`，可使用 `pre-commit run --files <file>` 运行检查。

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
