# Phase 2 - 新游戏配置页面实施计划

## 🎯 目标
实现完整的新游戏配置页面，包括参数设置、API集成和游戏初始化

## 📋 实施步骤

### 1. 更新 NewGame.vue - 新游戏配置页面
- 游戏参数表单
- 难度选择
- NPC数量设置
- 初始恐惧点数
- AI功能开关

### 2. 创建 API 服务 - src/api/gameApi.ts
- 创建游戏API
- 初始化游戏API
- 错误处理

### 3. 更新游戏状态管理 - src/stores/game.ts
- 完善initGame方法
- 添加配置验证
- 错误状态管理

### 4. 创建通用组件
- LoadingSpinner.vue - 加载动画
- ErrorMessage.vue - 错误提示
- GameConfigForm.vue - 配置表单组件

### 5. 添加表单验证
- 参数范围验证
- 必填项检查
- 实时反馈

### 6. 实现游戏创建流程
- 提交配置
- 调用API
- 处理响应
- 跳转到游戏界面

## ✅ 验收标准
- [ ] 完整的配置表单界面
- [ ] 参数验证功能
- [ ] API调用成功
- [ ] 错误处理机制
- [ ] 成功创建游戏后跳转

## 📝 文件清单
1. src/views/NewGame.vue - 更新
2. src/api/gameApi.ts - 创建
3. src/api/index.ts - 创建
4. src/components/common/LoadingSpinner.vue - 创建
5. src/components/common/ErrorMessage.vue - 创建
6. src/types/game.ts - 创建（类型定义）
