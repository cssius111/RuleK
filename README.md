# RuleK - 规则怪谈管理者 🎮

一个恐怖生存游戏，玩家扮演诡异空间的管理者，通过创建规则来收割恐惧。

## 🚀 快速开始

### 最简单的方法（推荐）
```bash
python start_all.py
```
这会同时启动前后端服务，然后访问 http://localhost:5173

### 分别启动

#### 1. 启动后端
```bash
# 使用 Makefile
make serve
# 或使用 rulek.py
python rulek.py web
```
- 运行在: http://localhost:8000
- API文档: http://localhost:8000/docs

#### 2. 启动前端
新开终端：
```bash
cd web/frontend
npm install  # 首次运行
npm run dev
```
- 运行在: http://localhost:5173

## 📋 系统要求

- Python 3.10+
- Node.js 16+
- npm 或 yarn

## 📦 安装依赖

### Python依赖
```bash
pip install -r requirements.txt
```

### 前端依赖
```bash
cd web/frontend
npm install
```

## 🗂️ 项目结构
```
RuleK/
├── src/           # 游戏核心逻辑
│   ├── core/      # 核心系统
│   ├── models/    # 数据模型
│   └── api/       # API接口
├── web/
│   ├── backend/   # FastAPI后端
│   └── frontend/  # Vue3前端
├── config/        # 配置文件
├── tests/         # 测试用例
└── docs/          # 项目文档
```

## 🎮 游戏特色

- **规则创建系统**: 创建各种诡异规则来控制NPC
- **AI驱动**: 智能NPC行为和对话生成
- **恐怖氛围**: 沉浸式的恐怖游戏体验
- **多结局**: 根据玩家选择产生不同结局

## 🔧 故障排查

### 后端无法启动
1. 检查Python版本: `python --version` (需要3.10+)
2. 安装依赖: `pip install -r requirements.txt`
3. 检查端口8000是否被占用

### 前端无法启动
1. 检查Node版本: `node --version` (需要16+)
2. 安装依赖: `cd web/frontend && npm install`
3. 检查端口5173是否被占用

### 页面空白或报错
1. 确保后端已启动（http://localhost:8000）
2. 确保前端已启动（http://localhost:5173）
3. 检查浏览器控制台错误信息

## 📝 开发

### 运行测试
```bash
pytest tests/
```

### 代码格式化
```bash
black src/
```

## 📄 许可证

MIT License

---

如有问题，请查看 `docs/` 目录下的详细文档。
