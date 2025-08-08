# RuleK Web Frontend - 快速开始指南

## ✅ 当前状态

根据你的日志，以下已完成：
- ✅ Vue 3 + TypeScript 项目已初始化
- ✅ 依赖已安装（包括Naive UI、Tailwind等）
- ✅ 开发服务器运行在 http://localhost:5173

## 🔧 修复已完成

1. **package.json 已更新** - 添加了所有缺失的脚本
2. **路径已修正** - 脚本现在使用正确的相对路径

## 🚀 立即开始

### 1. 验证环境（在 web/frontend 目录）
```bash
node check-env.js
```

### 2. 安装Playwright（用于E2E测试）
```bash
npm run setup:playwright
```

### 3. 启动开发服务器（如果未运行）
```bash
npm run dev
```

### 4. 启动后端服务器（新终端，在项目根目录）
```bash
cd ../..  # 回到项目根目录
python start_web_server.py
```

### 5. 运行Phase 0测试验证
```bash
# 在 web/frontend 目录
npm run test:phase0
```

### 6. 查看进度报告
```bash
npm run track:phase0
```

## 📋 可用的npm脚本

### 开发相关
- `npm run dev` - 启动开发服务器
- `npm run build` - 构建生产版本
- `npm run preview` - 预览生产构建

### 测试相关（按阶段）
- `npm run test:phase0` - 环境验证
- `npm run test:phase1` - 基础框架测试
- `npm run test:phase2` - 游戏创建测试
- ... (phase3-6同理)

### 进度追踪
- `npm run track:phase0` - Phase 0进度检查
- `npm run report:phase0` - 生成Phase 0报告
- ... (其他phase同理)

### 工具
- `npm run setup:playwright` - 安装Playwright浏览器
- `npm run lint` - 代码检查
- `npm run format` - 代码格式化

## 🎯 Phase 0 成功标准

运行 `npm run test:phase0` 应该验证：
1. ✅ 前端服务器可访问 (localhost:5173)
2. ✅ 后端API可访问 (localhost:8000)
3. ✅ WebSocket连接正常
4. ✅ 响应式布局工作

## 📝 接下来的开发流程

### Phase 1: 基础框架 (Day 2-3)
1. 创建路由系统 (`src/router/`)
2. 配置Pinia状态管理 (`src/stores/`)
3. 实现基础布局组件

```bash
# 开始Phase 1开发后
npm run test:phase1    # 测试
npm run track:phase1   # 检查进度
```

### Phase 2: 游戏创建 (Day 4-5)
- 新游戏配置页面
- 存档加载功能
- API集成

### Phase 3: 游戏核心界面 (Day 6-8)
- GameDashboard组件
- WebSocket实时更新
- 状态同步

## ⚠️ 常见问题解决

### 问题: "Missing script" 错误
✅ **已修复** - package.json已更新，包含所有脚本

### 问题: 端口占用
```bash
# 查找占用5173端口的进程
lsof -i :5173
# 结束进程
kill -9 <PID>
```

### 问题: Playwright安装失败
```bash
# 手动安装
npx playwright install chromium
```

### 问题: 路径错误
确保在正确目录：
- 前端命令：在 `web/frontend/` 运行
- 后端命令：在项目根目录运行
- 测试命令：在 `web/frontend/` 运行

## 📊 项目结构（当前）

```
RuleK/
├── web/
│   ├── frontend/           # 你在这里
│   │   ├── src/           # Vue源代码
│   │   ├── public/        # 静态资源
│   │   ├── package.json   # ✅ 已更新
│   │   ├── vite.config.ts # Vite配置
│   │   ├── check-env.js   # ✅ 新增：环境检查
│   │   └── ...
│   └── backend/           # FastAPI后端
├── tests/
│   └── e2e/              # Playwright测试
│       ├── phase0.spec.ts # 环境验证测试
│       └── helpers.ts     # 测试助手
├── scripts/
│   ├── track-progress.js # 进度追踪
│   └── progress_reporter.py # 报告生成
└── start_web_server.py   # 后端启动脚本
```

## ✨ 立即验证一切正常

运行这个命令序列：
```bash
# 1. 检查环境
node check-env.js

# 2. 如果提示缺少依赖
npm install

# 3. 安装Playwright
npm run setup:playwright

# 4. 运行测试
npm run test:phase0

# 5. 查看报告
npm run track:phase0
```

如果所有测试通过，你就可以开始Phase 1的开发了！

---

💡 **提示**: 不要复制注释行（#开头的）到终端，只复制实际命令。

有问题随时询问！祝开发顺利 🚀
