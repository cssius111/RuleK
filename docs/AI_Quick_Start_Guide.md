# AI功能快速启动指南

## 🚀 5分钟快速开始

### 1. 验证环境配置

```bash
# 在项目根目录运行
python verify_ai_integration.py
```

确保看到所有 ✅ 标记，特别是：
- DeepSeek API密钥已配置
- 所有模块导入成功
- GameService包含所有AI方法

### 2. 测试AI功能（无需启动服务器）

```bash
python test_ai_integration.py
# 选择 1 - 测试AI功能（直接调用）
```

这将测试：
- AI回合生成（对话和行动）
- 自然语言规则评估
- 叙事生成

### 3. 启动Web服务器

```bash
# 方式1：直接运行
python web/backend/app.py

# 方式2：使用启动脚本
./start.sh  # macOS/Linux
start.bat   # Windows
```

服务器将在 http://localhost:8000 启动

### 4. 测试Web API

#### 方式1：使用测试脚本
```bash
python test_ai_integration.py
# 选择 2 - 测试Web API
```

#### 方式2：使用交互式文档
访问 http://localhost:8000/docs

测试流程：
1. **创建游戏** - POST /api/games
2. **初始化AI** - POST /api/games/{game_id}/ai/init
3. **执行AI回合** - POST /api/games/{game_id}/ai/turn
4. **评估规则** - POST /api/games/{game_id}/ai/evaluate-rule

#### 方式3：使用curl命令
```bash
# 1. 创建游戏
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "normal", "npc_count": 4}'

# 记录返回的game_id

# 2. 初始化AI
curl -X POST http://localhost:8000/api/games/{game_id}/ai/init

# 3. 执行AI回合
curl -X POST http://localhost:8000/api/games/{game_id}/ai/turn \
  -H "Content-Type: application/json" \
  -d '{"force_dialogue": true}'

# 4. 评估规则
curl -X POST http://localhost:8000/api/games/{game_id}/ai/evaluate-rule \
  -H "Content-Type: application/json" \
  -d '{"rule_description": "晚上10点后不能开灯"}'
```

## 🎮 在CLI中使用AI

1. 运行CLI游戏：
```bash
python src/cli_game.py
```

2. 创建新游戏时选择启用AI
3. 在游戏中使用AI功能：
   - 准备阶段选择"使用AI生成对话和行动"
   - 创建规则时选择"AI解析自然语言规则"
   - 结算阶段选择"生成本回合叙事"

## 🔍 常见问题

### API密钥错误
确保 `.env` 文件中的 `DEEPSEEK_API_KEY` 正确设置

### 导入错误
在项目根目录运行所有脚本

### 连接超时
检查网络连接，DeepSeek API需要访问外网

### AI未初始化
确保先调用 `/api/games/{game_id}/ai/init` 端点

## 📊 监控和调试

### 查看日志
```bash
# API日志
tail -f logs/api.log

# AI请求日志
tail -f logs/ai_requests.log
```

### 调试模式
在 `.env` 中设置：
```
GAME_DEBUG=true
```

## 🎯 下一步

1. **探索更多功能**
   - 尝试不同的规则描述
   - 测试多轮对话
   - 观察NPC行为变化

2. **集成到前端**
   - 在Vue前端添加AI控制面板
   - 实现实时对话显示
   - 添加叙事展示组件

3. **性能优化**
   - 监控API响应时间
   - 实现缓存策略
   - 优化Token使用

---

祝您使用愉快！如有问题，请查看项目文档或提交Issue。
