# 未完成任务汇总

以下列表整合了项目文档中仍未完成的目标，方便集中追踪。

## Quick_Start_Guide
- [ ] 创建基础模型和工具：`models/base.py`、`utils/validators.py`、`config/settings.py` 等
- [ ] 实现核心系统：`managers/rule_manager.py`、`managers/npc_manager.py`、`core/turn_engine.py`、`core/event_system.py`
- [ ] AI集成模块：`api/deepseek_client.py`、`api/prompt_templates.py`、`utils/text_processor.py`
- [ ] 游戏逻辑：`core/rule_executor.py`、`core/npc_ai.py`、`core/fear_calculator.py`
- [ ] Web界面：`web/app.py`、`web/websocket_handler.py`、`web/static/game.js`

## RESTRUCTURE_GUIDE
- [ ] 提交当前更改并创建重构分支
- [ ] 运行 `analyze_project.py` 并备份重要文件
- [ ] 预览并执行 `scripts/utils/restructure.py`
- [ ] 更新导入路径并检查移动结果
- [ ] 删除 `.backups/` 和其他缓存
- [ ] 运行 `python rulek.py test` 验证功能
- [ ] 更新文档并合并到主分支

## PROJECT_RESTRUCTURE_PLAN
- [ ] 按计划移动脚本和文档到新目录
- [ ] 更新所有路径引用并清理 `.backup` 文件
- [ ] 运行完整测试套件并更新文档

## MCP_Development_Plan
- [ ] 完成核心管理类（GameManager、RuleManager 等）
- [ ] 定义数据模型与验证器
- [ ] 构建回合控制器和基础规则引擎
- [ ] 完成完整游戏循环与基础 Web UI
- [ ] 扩充规则模板、支持存档和多语言等

## CLI_Testing_and_Development
- [ ] 实现自定义规则界面与规则升级
- [ ] 提升用户体验（彩色输出、菜单导航、帮助系统等）
- [ ] 接入 DeepSeek API 与 NPC 智能行为
- [ ] 增加性能、端到端及压力测试
- [ ] 完善类型注解与异步结构
- [ ] 优化跨平台兼容与配置化支持
