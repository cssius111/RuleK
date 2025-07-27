# RuleK Web Backend

基于 FastAPI 的规则怪谈管理者游戏后端服务。

## 快速开始

### 1. 安装依赖

```bash
# 在项目根目录
pip install fastapi uvicorn websockets python-multipart
```

### 2. 启动服务器

```bash
# 方式1：使用启动脚本
cd web/backend
python run_server.py

# 方式2：直接使用 uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API根路径: http://localhost:8000/

## API端点

### 游戏管理
- `POST /api/games` - 创建新游戏
- `GET /api/games/{game_id}` - 获取游戏状态
- `DELETE /api/games/{game_id}` - 删除游戏

### 游戏操作
- `POST /api/games/{game_id}/turn` - 推进回合
- `POST /api/games/{game_id}/rules` - 创建规则
- `GET /api/games/{game_id}/rules` - 获取规则列表
- `GET /api/games/{game_id}/npcs` - 获取NPC列表

### 存档管理
- `POST /api/games/{game_id}/save` - 保存游戏
- `POST /api/games/load` - 加载存档

### WebSocket
- `WS /ws/{game_id}` - 实时游戏更新

## 测试API

### 创建新游戏
```bash
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "normal", "npc_count": 4}'
```

### 获取游戏状态
```bash
curl http://localhost:8000/api/games/{game_id}
```

### 创建规则
```bash
curl -X POST http://localhost:8000/api/games/{game_id}/rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "午夜照镜死",
    "description": "午夜时分照镜子会导致死亡",
    "requirements": {
      "time": {"from": "00:00", "to": "04:00"},
      "areas": ["bathroom"]
    },
    "trigger": {
      "action": "look_mirror"
    },
    "effect": {
      "type": "instant_death",
      "fear_gain": 200
    },
    "cost": 150
  }'
```

## WebSocket 测试

使用 websocat 或其他 WebSocket 客户端：

```bash
# 安装 websocat
brew install websocat  # macOS
# 或
cargo install websocat  # 使用 Rust

# 连接 WebSocket
websocat ws://localhost:8000/ws/{game_id}

# 发送消息
{"type": "ping"}
{"type": "action", "data": {"action_type": "advance_turn"}}
```

## 开发说明

### 项目结构
```
backend/
├── app.py              # FastAPI 主应用
├── models.py           # Pydantic 数据模型
├── services/           # 业务逻辑层
│   ├── game_service.py # 游戏服务
│   └── session_manager.py # 会话管理
└── run_server.py       # 启动脚本
```

### 环境变量

创建 `.env` 文件（如果需要）：
```
DEEPSEEK_API_KEY=your_api_key_here
LOG_LEVEL=INFO  # 或數值，例如 20
```

### 日志

日志文件保存在 `logs/` 目录下。

## 下一步

1. 前端开发：查看 `web/frontend/` 目录
2. 添加认证：实现用户登录和会话管理
3. 数据持久化：集成数据库（PostgreSQL/MongoDB）
4. 部署：使用 Docker 容器化部署
