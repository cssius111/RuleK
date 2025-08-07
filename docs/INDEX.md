# RuleK 文档索引

## 📚 文档分类

### 指南
- [快速开始指南](guides/Quick_Start_Guide.md)
- [CLI 测试与开发](guides/CLI_Testing_and_Development.md)
- [快速命令集](guides/quick_start.md)
- [重构实施指南](guides/RESTRUCTURE_GUIDE.md)
- [清理指南](guides/cleanup_guide.md)
- [游戏演示指南](guides/GAME_DEMO_GUIDE.md)

### 架构
- [AI 核心实现指南](architecture/AI_Core_Implementation_Guide.md)
- [Web UI 计划](architecture/Web_UI_Plan.md)
- [Web 端 AI 核心化优化计划](architecture/Web_AI_Core_Optimization_Plan.md)
- [Web 端 AI 实施检查清单](architecture/Web_AI_Core_Implementation_Checklist.md)
- [Web 端 AI 核心化实施进度](architecture/Web_AI_Core_Implementation_Progress.md)

### 计划
- [项目重构计划](plans/PROJECT_RESTRUCTURE_PLAN.md)
- [MCP 开发计划](plans/MCP_Development_Plan.md)
- [剩余任务](plans/REMAINING_TASKS.md)
- [下一步计划](plans/NEXT_STEPS.md)

### 遗留
- [游戏设计文档](legacy/game_design.md)

### 其他
- [部署指南](DEPLOYMENT.md)
- [快速参考](QUICK_REFERENCE.md)
- [贡献指南](contributing.md)
- [Agents 说明](agents.md)
- [清理完成报告](cleanup_complete.md)

---

## 🚀 快速命令参考

### 运行游戏
```bash
# CLI 模式
python rulek.py cli

# Web 模式
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
*最后更新：2025-08-07*
