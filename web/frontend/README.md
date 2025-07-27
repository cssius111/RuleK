# RuleK Frontend - 规则怪谈管理者前端

基于 Vue 3 + TypeScript + Vite 的现代化前端应用。

## 技术栈

- **框架**: Vue 3.3
- **语言**: TypeScript 5.0
- **构建工具**: Vite 5.0
- **路由**: Vue Router 4
- **状态管理**: Pinia 2
- **UI 组件库**: Naive UI
- **HTTP 客户端**: Axios
- **WebSocket**: Socket.io Client
- **样式**: SCSS

## 快速开始

### 安装依赖

```bash
cd web/frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
src/
├── api/              # API 客户端
│   ├── client.ts     # HTTP 客户端
│   └── websocket.ts  # WebSocket 管理
├── assets/           # 静态资源
├── components/       # 组件
│   ├── game/        # 游戏相关组件
│   └── layout/      # 布局组件
├── router/          # 路由配置
├── stores/          # Pinia 状态管理
├── styles/          # 全局样式
├── types/           # TypeScript 类型定义
├── views/           # 页面视图
├── App.vue          # 根组件
└── main.ts          # 入口文件
```

## 核心功能

### 1. 游戏管理
- 创建新游戏
- 加载存档
- 实时游戏状态同步

### 2. 规则系统
- 可视化规则创建器
- 规则列表展示
- 规则效果预览

### 3. NPC 管理
- NPC 状态卡片
- 实时状态更新
- 交互操作

### 4. 事件系统
- 事件日志
- 叙事展示
- 实时通知

### 5. WebSocket 实时通信
- 自动重连
- 心跳检测
- 消息队列

## 开发指南

### 添加新组件

1. 在 `src/components/` 下创建组件文件
2. 使用 `<script setup>` 语法
3. 遵循组件命名规范（PascalCase）

### 添加新页面

1. 在 `src/views/` 下创建页面组件
2. 在 `src/router/index.ts` 中添加路由
3. 更新导航菜单

### 状态管理

使用 Pinia 进行状态管理：

```typescript
import { useGameStore } from '@/stores/game'

const gameStore = useGameStore()
// 使用 gameStore 中的状态和方法
```

### API 调用

使用封装的 API 客户端：

```typescript
import { api } from '@/api/client'

// 创建游戏
const game = await api.createGame({ difficulty: 'normal', npc_count: 4 })
```

### 样式规范

- 使用 SCSS 编写样式
- 遵循 BEM 命名规范
- 优先使用 Naive UI 组件
- 自定义样式使用 scoped

## 环境变量

创建 `.env.local` 文件：

```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 构建优化

- 组件按需加载
- 路由懒加载
- 图片懒加载
- 代码分割

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 常见问题

### 1. 开发服务器无法启动
确保端口 5173 未被占用，或修改 `vite.config.ts` 中的端口配置。

### 2. API 请求失败
检查后端服务是否运行在 http://localhost:8000

### 3. WebSocket 连接失败
确保后端 WebSocket 服务正常运行，检查防火墙设置。

## 部署

### 使用 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 使用 Docker

参见项目根目录的 Dockerfile。

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License
