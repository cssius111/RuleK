# 项目变更报告

## 1. 删除和移动文件统计
- 删除文件：327 个，总计 3,072,508 字节（约 3.0 MB）
- 移动文件：84 个，总计 436,005 字节（约 0.43 MB）

## 2. 更新文档
- `docs/INDEX.md`：更新索引内容以反映新的文档结构
- `docs/AI_Core_Implementation_Guide.md` → `docs/architecture/AI_Core_Implementation_Guide.md`
- `docs/Web_AI_Core_Implementation_Checklist.md` → `docs/architecture/Web_AI_Core_Implementation_Checklist.md`
- `docs/Web_AI_Core_Implementation_Progress.md` → `docs/architecture/Web_AI_Core_Implementation_Progress.md`
- `docs/Web_AI_Core_Optimization_Plan.md` → `docs/architecture/Web_AI_Core_Optimization_Plan.md`
- `docs/Web_UI_Plan.md` → `docs/architecture/Web_UI_Plan.md`
- `docs/CLI_Testing_and_Development.md` → `docs/guides/CLI_Testing_and_Development.md`
- `docs/RESTRUCTURE_GUIDE.md` → `docs/guides/RESTRUCTURE_GUIDE.md`
- `docs/cleanup_guide.md` → `docs/guides/cleanup_guide.md`
- `docs/quick_start.md` → `docs/guides/quick_start.md`
- `docs/game_design/game_design_v0.2.md` → `docs/legacy/game_design.md`
- `docs/MCP_Development_Plan.md` → `docs/plans/MCP_Development_Plan.md`
- `docs/NEXT_STEPS.md` → `docs/plans/NEXT_STEPS.md`
- `docs/PROJECT_RESTRUCTURE_PLAN.md` → `docs/plans/PROJECT_RESTRUCTURE_PLAN.md`
- `docs/REMAINING_TASKS.md` → `docs/plans/REMAINING_TASKS.md`

## 3. 待处理 TODO
- web/frontend/src/api/client.ts:26 添加认证 token
- web/backend/services/game_service.py:205 实现基于新的事件模型的随机事件逻辑
- docs/guides/CLI_Testing_and_Development.md:44 完成 `load_game_menu` 实现
- docs/guides/CLI_Testing_and_Development.md:53 在 `dialogue_phase` 添加 TODO 说明
- web/frontend/src/router/index.ts:50 检查是否有有效的游戏会话
- web/frontend/src/views/SettingsView.vue:104 保存设置到本地存储或服务器
- src/core/game_state.py:637 实现具体位置追踪
- web/frontend/src/components/game/NPCGrid.vue:26 显示 NPC 详细信息对话框
- web/frontend/src/views/HomePage.vue:160 实现加载存档功能
- web/frontend/src/views/HomePage.vue:170 实现删除存档功能
- web/frontend/src/views/HomePage.vue:179 从 API 加载存档列表
- web/frontend/src/components/game/ActionButtons.vue:86 显示叙事文本
- web/frontend/src/components/game/ActionButtons.vue:99 实现模式切换

