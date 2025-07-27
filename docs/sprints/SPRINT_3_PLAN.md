# Sprint 3 开发计划 - Web UI 原型

## 🎯 Sprint 3 目标
将规则怪谈管理者带到Web！创建一个现代化的Web界面，让玩家通过浏览器体验游戏。

---

## 📋 开发任务清单

### Phase 1: FastAPI 后端（2天）
- [ ] 创建 `web/backend/app.py` - FastAPI主应用
- [ ] 实现游戏会话管理
- [ ] RESTful API端点设计
- [ ] WebSocket实时通信
- [ ] 游戏状态序列化

### Phase 2: 前端框架（1天）
- [ ] 选择框架（Vue 3 / React）
- [ ] 项目初始化和配置
- [ ] 路由设置
- [ ] 状态管理（Pinia/Redux）
- [ ] WebSocket客户端

### Phase 3: 核心UI组件（3天）
- [ ] 游戏大厅界面
- [ ] 主游戏界面布局
- [ ] NPC状态卡片组件
- [ ] 规则创建向导
- [ ] 地图可视化组件
- [ ] 对话显示组件
- [ ] 事件通知系统

### Phase 4: 游戏集成（2天）
- [ ] 前后端通信协议
- [ ] 实时游戏状态同步
- [ ] 动画和过渡效果
- [ ] 音效系统（可选）
- [ ] 响应式设计

### Phase 5: 测试和优化（1天）
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 错误处理
- [ ] 部署准备

---

## 🛠 技术栈建议

### 后端
```python
# requirements_web.txt
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
python-multipart==0.0.6
redis==5.0.1  # 用于会话管理
```

### 前端（Vue 3方案）
```json
{
  "dependencies": {
    "vue": "^3.3.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.5.0",
    "socket.io-client": "^4.6.0",
    "@vueuse/core": "^10.0.0",
    "naive-ui": "^2.35.0"  // UI组件库
  }
}
```

---

## 📁 建议的项目结构

```
web/
├── backend/
│   ├── app.py              # FastAPI主应用
│   ├── api/
│   │   ├── __init__.py
│   │   ├── game.py         # 游戏相关API
│   │   ├── rules.py        # 规则管理API
│   │   └── websocket.py    # WebSocket处理
│   ├── models/
│   │   └── session.py      # 会话模型
│   └── services/
│       └── game_service.py # 游戏服务层
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── GameBoard.vue
    │   │   ├── NPCCard.vue
    │   │   ├── RuleCreator.vue
    │   │   ├── DialoguePanel.vue
    │   │   └── MapView.vue
    │   ├── views/
    │   │   ├── Home.vue
    │   │   ├── Game.vue
    │   │   └── Settings.vue
    │   ├── stores/
    │   │   └── game.js
    │   └── api/
    │       └── client.js
    └── public/
        └── assets/
```

---

## 🚀 快速开始 Prompts

### Prompt 1: FastAPI 后端基础
```
基于现有的RuleK游戏架构，创建FastAPI Web后端。

要求：
1. 文件路径：web/backend/app.py
2. 实现以下功能：
   - 游戏会话管理（支持多个并行游戏）
   - RESTful API端点：
     - POST /api/game/new - 创建新游戏
     - GET /api/game/{game_id}/state - 获取游戏状态
     - POST /api/game/{game_id}/rule - 创建规则
     - POST /api/game/{game_id}/action - 执行玩家动作
     - GET /api/game/{game_id}/npcs - 获取NPC列表
   - WebSocket端点用于实时更新
   - CORS配置支持前端开发
3. 重用src目录下的游戏逻辑，不要重写
4. 使用异步处理提高性能
5. 实现简单的内存会话存储（后续可升级为Redis）

注意保持与现有代码的兼容性。
```

### Prompt 2: Vue 3 前端框架
```
创建Vue 3前端应用来展示规则怪谈管理者游戏。

要求：
1. 使用Vue 3 + Vite + Pinia
2. 创建响应式的游戏界面
3. 实现以下核心组件：
   - GameBoard.vue - 主游戏面板
   - NPCCard.vue - NPC状态卡片（显示HP、恐惧、位置等）
   - RuleCreator.vue - 规则创建向导
   - MapView.vue - 地图可视化（显示6个房间和NPC位置）
   - DialoguePanel.vue - 对话和叙事显示
4. 使用WebSocket接收实时更新
5. 暗色主题，营造恐怖氛围
6. 支持移动端响应式设计

设计要现代、直观，让玩家专注于游戏策略。
```

### Prompt 3: 游戏状态同步
```
实现前后端的游戏状态同步机制。

需求：
1. 后端：
   - 创建GameStateSerializer将Python对象转为JSON
   - 实现增量更新（只发送变化的数据）
   - WebSocket消息类型定义
2. 前端：
   - Pinia store管理游戏状态
   - WebSocket消息处理
   - 乐观更新提升响应速度
3. 消息协议设计：
   - 标准消息格式
   - 错误处理
   - 重连机制

确保低延迟和良好的用户体验。
```

---

## 🎨 UI/UX 设计指南

### 视觉风格
- **主色调**: 深紫色 (#2D1B69) + 血红色 (#8B0000)
- **背景**: 深灰/黑色渐变
- **字体**: 哥特式英文 + 楷体中文
- **动效**: 阴森的悬浮、闪烁效果

### 关键界面元素
1. **恐惧值显示**: 大号数字，血红色，带脉动效果
2. **NPC卡片**: 极简设计，状态变化时闪烁警告
3. **规则列表**: 羊皮纸质感，手写字体
4. **地图**: 俯视图，房间用不同亮度表示危险程度
5. **对话框**: 打字机效果，营造紧张感

### 交互设计
- 拖拽创建规则
- 点击NPC查看详情
- 悬浮显示提示
- 键盘快捷键支持

---

## 📊 性能目标

- 首屏加载 < 3秒
- WebSocket延迟 < 100ms
- 支持同时 10+ 个NPC流畅运行
- 移动端 60 FPS

---

## 🔧 开发工具推荐

- **API测试**: Postman / Thunder Client
- **WebSocket调试**: Socket.IO Admin UI
- **性能监控**: Vue DevTools + Chrome DevTools
- **部署**: Docker + Nginx

---

## 📅 时间估算

- **总工期**: 9个工作日
- **MVP版本**: 5天（仅核心功能）
- **完整版本**: 9天（含优化和测试）

---

## 🎯 MVP功能清单

必须包含：
- [x] 创建新游戏
- [x] 显示NPC状态
- [x] 创建基础规则
- [x] 显示游戏日志
- [x] 推进回合

可以延后：
- [ ] 地图可视化
- [ ] 音效系统
- [ ] 成就系统
- [ ] 多语言支持

---

## 📝 开始开发

```bash
# 1. 创建项目结构
mkdir -p web/backend web/frontend

# 2. 后端开发
cd web/backend
pip install fastapi uvicorn websockets

# 3. 前端开发
cd ../frontend
npm create vite@latest . -- --template vue
npm install

# 4. 启动开发服务器
# 后端: uvicorn app:app --reload
# 前端: npm run dev
```

---

准备好了吗？让我们把恐怖带到浏览器上！🎮🌐
