# 📚 RuleK 文档中心

## 项目文档结构

```
docs/
├── 01-agents/           # Agent规则系统
│   ├── README.md       # Agent系统说明
│   └── validator/      # 验证工具文档
│
├── 02-architecture/     # 架构文档
│   ├── README.md       # 架构概览
│   ├── websocket.md    # WebSocket架构
│   └── ai-integration.md # AI集成架构
│
├── 03-development/      # 开发指南
│   ├── setup.md        # 环境配置
│   ├── workflow.md     # 开发流程
│   └── guidelines/     # 编码规范
│
├── 04-api/             # API文档
│   ├── rest-api.md     # REST API
│   ├── websocket.md    # WebSocket API
│   └── schemas/        # 数据模式
│
├── 05-progress/        # 进度追踪
│   ├── roadmap.md      # 路线图
│   ├── changelog.md    # 变更日志
│   └── current/        # 当前进度
│
└── templates/          # 文档模板
    ├── feature.md      # 功能文档模板
    └── api.md          # API文档模板
```

## 📖 快速导航

### 🤖 Agent系统
- [Agent系统使用指南](01-agents/README.md)
- [Agent验证器文档](01-agents/validator/README.md)

### 🏗️ 架构设计
- [系统架构概览](02-architecture/README.md)
- [WebSocket流式架构](02-architecture/websocket.md)
- [AI集成架构](02-architecture/ai-integration.md)

### 💻 开发指南
- [环境配置](03-development/setup.md)
- [开发流程](03-development/workflow.md)
- [编码规范](03-development/guidelines/coding-standards.md)

### 📡 API文档
- [REST API参考](04-api/rest-api.md)
- [WebSocket协议](04-api/websocket.md)
- [数据模式定义](04-api/schemas/README.md)

### 📊 项目进度
- [项目路线图](05-progress/roadmap.md)
- [变更日志](05-progress/changelog.md)
- [当前进度](05-progress/current/STATUS.md)

## 🔍 文档搜索

按类型查找：
- **操作指南**: `*_GUIDE.md`
- **计划文档**: `*_PLAN.md`
- **进度报告**: `*_PROGRESS.md`
- **Agent规则**: `*_AGENT.md`

## 📝 文档规范

### 命名规则
- 目录使用数字前缀：`01-`, `02-`
- 文档使用小写：`readme.md`, `setup.md`
- 特殊文档大写：`README.md`, `LICENSE.md`

### 更新原则
- **修改优于新建**：更新现有文档而不是创建新版本
- **保留历史**：使用版本记录而不是删除
- **标注日期**：每次更新标注修改日期

---

*文档中心版本: 1.0.0*
*最后更新: 2024-12-22*