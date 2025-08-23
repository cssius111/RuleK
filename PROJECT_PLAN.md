# RuleK 项目计划

## 🎯 当前状态

### 已完成功能
- ✅ CLI游戏完整实现
- ✅ Web基础版本上线
- ✅ AI集成第三阶段完成
- ✅ 统一入口 rulek.py
- ✅ 移除硬编码测试NPC (2024-12-22)
- ✅ 改进NPC名字生成系统 (2024-12-22)
- ✅ 修复前端API导入问题 (2025-01-08)

### 进行中
- 🔄 Web端AI核心化改造（第一阶段完成，第二阶段30%）
- 🔄 WebSocket流式推送实现

## 📋 下一步任务

### 本周任务（2024-12-22 ~ 2024-12-28）
1. [x] 修复NPC硬编码问题 ✅
2. [x] 修复测试失败问题 ✅
3. [ ] 完成WebSocket流式改造
4. [ ] 实现断线重连机制
5. [ ] 添加心跳机制
6. [ ] 前端组件改造
7. [ ] 调查Create Rule按钮问题

### 短期目标（1月）
- 完成AI核心化改造全部5个阶段
- 实现<2秒AI响应
- 达到100% AI功能使用率

## 🔧 技术改进

### WebSocket流式改造详细计划

#### 第二阶段：流式推送（当前进度30%）

**已完成：**
- ✅ StreamingService框架搭建
- ✅ 基础WebSocket连接

**待完成：**
- [ ] 消息队列实现
- [ ] 流式数据分片
- [ ] 前端流式渲染
- [ ] 断线重连机制
- [ ] 心跳检测

#### 实现文件清单：
```
web/backend/services/
├── streaming_service.py  # 流式服务核心
├── message_queue.py      # 消息队列管理
└── connection_manager.py # 连接管理

web/frontend/src/composables/
├── useWebSocket.ts       # WebSocket Hook
├── useStreaming.ts       # 流式数据处理
└── useReconnect.ts       # 重连逻辑
```

## 📊 性能目标

| 指标 | 当前 | 目标 |
|------|------|------|
| API响应时间 | 5-10s | <0.5s |
| NPC创建准确性 | 175% (额外的测试NPC) | 100% ✅ |
| 测试通过率 | 90% (6个失败) | 100% ✅ |
| AI生成时间 | 5-8s | <2s |
| WebSocket延迟 | N/A | <100ms |
| 缓存命中率 | 0% | >70% |
| 断线重连成功率 | 0% | >95% |

## 🚀 使用方法

### 启动项目
```bash
# 使用 Makefile（推荐）
make serve      # 启动Web服务器
make cli        # 启动CLI游戏
make test       # 运行测试

# 或使用 rulek.py
python rulek.py web     # 启动Web服务器
python rulek.py cli     # 启动CLI游戏
python rulek.py test    # 运行测试

# 注意：start_web_server.py 已被删除，请使用上述命令
```

### 开发工具
```bash
make clean      # 清理缓存
make install    # 安装依赖
make format     # 代码格式化
make lint       # 代码检查
```

## 📝 项目结构优化

### 当前问题
- 根目录文件过多（20+）
- 临时文件混杂
- 导入路径不规范

### 目标结构
```
RuleK/
├── src/           # 核心源代码
│   ├── core/      # 游戏核心
│   ├── ai/        # AI集成
│   └── api/       # API接口
├── web/
│   ├── backend/   # FastAPI后端
│   └── frontend/  # Vue3前端
├── tests/         # 测试文件
├── docs/          # 项目文档
├── scripts/       # 工具脚本
└── config/        # 配置文件
```

---
*更新时间：2025-01-08*