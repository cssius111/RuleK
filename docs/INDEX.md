# RuleK 文档索引

## 📚 文档分类

### 快速开始
- [README](../README.md) - 项目概述和快速开始
- [快速开始指南](guides/Quick_Start_Guide.md) - 详细的快速开始教程

### 游戏设计
- [游戏设计文档](game_design/game_design_v0.2.md) - 完整的游戏设计
- [MCP开发计划](MCP_Development_Plan.md) - 开发路线图

### API文档
- [API文档](api/) - API接口文档
- [AI集成快速参考](AI_Integration_Quick_Reference.md) - AI功能快速查询

### 开发指南
- [AI集成实施指南](AI_Integration_Implementation_Guide.md) - AI功能集成详细步骤
- [AI集成计划](AI_Integration_Plan.md) - AI集成架构设计
- [CLI测试和开发](CLI_Testing_and_Development.md) - CLI开发指南
- [Web端AI核心化优化计划](Web_AI_Core_Optimization_Plan.md) - ⭐️ Web端AI核心化技术方案
- [Web端AI实施检查清单](Web_AI_Core_Implementation_Checklist.md) - ⭐️ AI核心化实施追踪
- [AI核心化实施进度报告](Web_AI_Core_Implementation_Progress.md) - 🆕 最新进度报告（2024-12-21）
- [AI核心化实施指南](AI_Core_Implementation_Guide.md) - 🆕 优化代码整合指南
- [项目重构计划](PROJECT_RESTRUCTURE_PLAN.md) - 通用项目重构规范
- [重构实施指南](RESTRUCTURE_GUIDE.md) - RuleK重构具体步骤

### 部署
- [部署指南](DEPLOYMENT.md) - 生产环境部署

### 进度报告
- [Sprint计划和报告](sprints/) - 各个Sprint的计划和报告
- [AI集成进度报告](AI_Integration_Progress_Report_Phase3_Complete.md) - AI功能实施进度
- [Web端AI核心化实施进度](Web_AI_Core_Implementation_Progress.md) - 🆕 第一阶段完成（2024-12-21）

### 测试和问题修复
- [测试修复指南](TEST_FIX_GUIDE.md) - 测试问题解决方案

---

## 🚀 快速命令参考

### 运行游戏
```bash
# CLI模式
python rulek.py cli

# Web模式
python rulek.py web

# 演示模式
python rulek.py demo
```

### 运行测试
```bash
# 运行所有测试
python rulek.py test

# 只运行单元测试
python rulek.py test unit

# 运行集成测试
python rulek.py test integration
```

### 环境验证
```bash
python rulek.py verify
```

### 项目重构
```bash
# 分析项目状态
python analyze_project.py

# 执行重构
./restructure.sh
```

---
*最后更新：2024-12-21*
