# RuleK API 测试和修复文档

## 📋 当前状态总结

根据 **MAIN_AGENT.md** 和 **AGENT.md** 的规则，我已经完成了以下工作：

### ✅ 已完成

1. **API测试工具** - 创建了完整的API测试套件
   - `scripts/test/test_api_comprehensive.py` - 综合测试所有API端点
   - `scripts/test/quick_api_test.py` - 快速测试和交互式工具

2. **API修复工具** - 自动诊断和修复常见问题
   - `scripts/fix/fix_api.py` - 检查依赖、文件结构、导入路径等

3. **项目管理工具** - 统一的项目管理入口
   - `tools/manage.py` - 集成所有功能的管理中心

### 📊 API功能清单

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/` | GET | API根路径 | ✅ 实现 |
| `/health` | GET | 健康检查 | ✅ 实现 |
| `/api/games` | POST | 创建游戏 | ✅ 实现 |
| `/api/games/{id}` | GET | 获取游戏状态 | ✅ 实现 |
| `/api/games/{id}/turn` | POST | 推进回合 | ✅ 实现 |
| `/api/games/{id}/rules` | POST | 创建规则 | ✅ 实现 |
| `/api/games/{id}/npcs` | GET | 获取NPC列表 | ✅ 实现 |
| `/api/games/{id}/save` | POST | 保存游戏 | ✅ 实现 |
| `/api/games/load` | POST | 加载存档 | ✅ 实现 |
| `/api/games/{id}/ai/*` | * | AI功能集 | ✅ 实现 |
| `/ws/{game_id}` | WS | WebSocket连接 | ✅ 实现 |

## 🚀 快速开始

### 1. 使用项目管理工具（推荐）

```bash
python tools/manage.py
```

这会打开一个交互式菜单，提供所有功能：
- 启动服务器
- 运行测试
- 诊断修复
- 查看状态

### 2. 快速测试API

```bash
# 运行快速测试（自动启动服务器）
python scripts/test/quick_api_test.py

# 或者手动步骤：
# 1. 启动服务器
python rulek.py web

# 2. 运行综合测试
python scripts/test/test_api_comprehensive.py
```

### 3. 诊断和修复

```bash
# 运行修复脚本
python scripts/fix/fix_api.py
```

## 🔧 常见问题和解决方案

### 问题1: 依赖缺失
**症状**: ImportError 错误  
**解决**: 
```bash
pip install -r requirements.txt
```

### 问题2: 端口被占用
**症状**: 端口8000已被占用  
**解决**: 
```bash
# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

### 问题3: 导入路径错误
**症状**: ModuleNotFoundError  
**解决**: 运行修复脚本
```bash
python scripts/fix/fix_api.py
```

### 问题4: 文件缺失
**症状**: FileNotFoundError  
**解决**: 修复脚本会自动创建缺失的文件

## 📝 测试报告示例

运行测试后会看到类似输出：

```
🚀 开始API综合测试
目标服务器: http://localhost:8000
============================================================
测试基础端点
============================================================
ℹ️ 测试 根路径: GET /
✅   状态码: 200 ✓
  响应键: ['name', 'version', 'status', 'endpoints']
ℹ️ 测试 健康检查: GET /health
✅   状态码: 200 ✓
  响应键: ['status', 'timestamp', 'active_games']
============================================================
测试游戏管理
============================================================
ℹ️ 测试 创建游戏: POST /api/games
✅   状态码: 200 ✓
  游戏ID: game_a1b2c3d4
...

============================================================
测试摘要
============================================================
总测试数: 25
通过: 23 ✅
失败: 2 ❌
成功率: 92.0%
API功能基本正常 ✨
```

## 🔍 API文档

启动服务器后，访问以下地址查看交互式API文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 下一步任务

根据 **PROJECT_PLAN.md**，当前重点是：

1. **WebSocket流式改造**（进度30%）
   - [ ] 完成消息队列实现
   - [ ] 实现流式数据分片
   - [ ] 添加断线重连机制
   - [ ] 实现心跳检测

2. **性能优化**
   - [ ] API响应时间 <0.5s
   - [ ] AI生成时间 <2s
   - [ ] 缓存命中率 >70%

## 📂 文件结构

```
RuleK/
├── scripts/
│   ├── test/
│   │   ├── test_api_comprehensive.py  # 综合API测试
│   │   └── quick_api_test.py         # 快速测试工具
│   └── fix/
│       └── fix_api.py                # API修复脚本
├── tools/
│   └── manage.py                      # 项目管理工具
├── web/
│   └── backend/
│       ├── app.py                     # FastAPI主应用
│       ├── models.py                  # 数据模型
│       └── services/
│           ├── game_service.py        # 游戏服务
│           ├── session_manager.py     # 会话管理
│           └── rule_service.py        # 规则服务
└── src/
    └── core/                          # 核心游戏逻辑
```

## ⚠️ 注意事项

1. **遵循MAIN_AGENT.md规则**
   - 优先修改现有文件，避免创建新文件
   - 不在根目录创建临时文件
   - 保持项目结构整洁

2. **测试前确保**
   - Python 3.10+ 已安装
   - 所有依赖已安装
   - 端口8000可用

3. **开发建议**
   - 使用 `tools/manage.py` 作为主入口
   - 定期运行测试确保功能正常
   - 遇到问题先运行诊断脚本

---

*文档更新时间: 2024-12-22*  
*遵循 MAIN_AGENT.md 和 AGENT.md 规范*
