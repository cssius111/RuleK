# RuleK开发 - 下一步Prompt模板

## 🎯 当前任务状态

**项目**: RuleK - 规则怪谈管理者游戏
**日期**: 2024-12-21
**当前阶段**: Web界面功能完善
**优先级**: 修复规则创建功能

## 📝 下一步开发Prompt

### Prompt 1: 修复规则创建功能
```
我正在开发RuleK游戏的Web界面。当前问题是规则创建按钮点击后没有反应。

技术栈：
- 前端: Vue3 + TypeScript + Naive UI + Pinia
- 后端: FastAPI + Python

问题描述：
1. GameView.vue中有RuleCreatorModal组件
2. ActionButtons.vue发出'create-rule'事件
3. 但GameView.vue没有监听这个事件

请帮我：
1. 修复GameView.vue中ActionButtons的事件监听
2. 确保showRuleCreator变量正确触发模态框显示
3. 添加规则创建成功后的处理逻辑

相关文件路径：
- web/frontend/src/views/GameView.vue
- web/frontend/src/components/game/ActionButtons.vue
- web/frontend/src/components/game/RuleCreatorModal.vue
```

### Prompt 2: 实现AI规则解析
```
RuleK游戏需要实现AI规则解析功能，让玩家用自然语言描述规则，AI自动解析成游戏规则。

后端API已存在：
POST /api/games/{game_id}/ai/evaluate-rule

请求格式：
{
  "description": "规则的自然语言描述",
  "game_state": {...}
}

响应格式：
{
  "rule_name": "生成的规则名",
  "estimated_cost": 300,
  "difficulty": "medium",
  "effects": [...],
  "potential_loopholes": [...]
}

请帮我在前端实现：
1. 创建AIRuleCreator.vue组件
2. 添加文本输入区域和解析按钮
3. 显示AI解析结果
4. 允许用户确认创建或修改后创建
5. 集成到规则创建流程中
```

### Prompt 3: 完善游戏回合系统
```
RuleK游戏的回合系统需要完善，当前只有基础的回合推进。

需要实现的功能：
1. 对话阶段 - 显示NPC之间的对话
2. 行动阶段 - 展示NPC的行动和结果
3. 规则触发 - 高亮显示触发的规则和效果
4. 结算阶段 - 显示本回合的统计信息

请帮我：
1. 创建TurnPhases.vue组件管理不同阶段
2. 实现阶段切换动画
3. 添加跳过/自动播放选项
4. 集成WebSocket实时更新

技术要求：
- 使用Vue3 Composition API
- TypeScript类型安全
- Naive UI组件
- 流畅的过渡动画
```

### Prompt 4: 添加Playwright E2E测试
```
RuleK游戏需要完整的E2E测试覆盖。

测试场景：
1. 完整游戏流程测试
   - 创建游戏
   - 创建规则（自定义/模板/AI）
   - 推进多个回合
   - 游戏结束条件

2. 规则系统测试
   - 创建各种类型的规则
   - 规则触发验证
   - 规则成本计算

3. AI功能测试
   - AI规则解析
   - AI回合生成
   - AI叙事生成

请帮我编写Playwright测试：
- 使用TypeScript
- Page Object模式
- 并行测试执行
- 截图和视频录制
- 测试报告生成

测试文件位置：tests/e2e/
```

### Prompt 5: 性能优化
```
RuleK游戏需要性能优化，当前存在以下问题：
1. 首次加载时间过长
2. 大量NPC时界面卡顿
3. WebSocket消息处理延迟
4. 内存使用持续增长

请帮我优化：
1. 实现组件懒加载和代码分割
2. 使用虚拟滚动处理NPC列表
3. 优化WebSocket消息批处理
4. 添加内存泄漏检测和修复
5. 实现状态管理优化（Pinia）

性能目标：
- FCP < 2s
- TTI < 3s
- 60fps滚动
- 内存使用 < 100MB
```

## 🔧 通用开发指导

### 代码规范
- 使用ESLint和Prettier
- 遵循Vue3风格指南
- TypeScript严格模式
- 组件名使用PascalCase
- 函数名使用camelCase

### 提交规范
```
feat: 添加规则创建功能
fix: 修复规则创建按钮无响应
docs: 更新README
style: 格式化代码
refactor: 重构游戏状态管理
test: 添加规则创建测试
chore: 更新依赖
```

### 测试要求
- 单元测试覆盖率 > 80%
- E2E测试覆盖核心流程
- 每个PR必须通过CI测试

### 性能要求
- Lighthouse分数 > 90
- 无内存泄漏
- 响应时间 < 200ms

## 📚 参考资源

### 项目文档
- [游戏设计文档](docs/game_design/game_design_v0.2.md)
- [API文档](http://localhost:8000/docs)
- [Web开发计划](docs/Web_Development_Plan_2024.md)

### 技术文档
- [Vue3官方文档](https://vuejs.org/)
- [Naive UI组件库](https://www.naiveui.com/)
- [Pinia状态管理](https://pinia.vuejs.org/)
- [Playwright测试](https://playwright.dev/)

### 代码示例
```typescript
// 规则创建示例
interface Rule {
  id: string
  name: string
  description: string
  trigger: RuleTrigger
  effects: RuleEffect[]
  cost: number
}

async function createRule(rule: Partial<Rule>): Promise<Rule> {
  const response = await api.post(`/games/${gameId}/rules`, rule)
  return response.data
}
```

## 🚀 快速开始命令

```bash
# 修复规则创建
python fix_rule_creation.py

# 运行测试
python tests/web/test_game_full_flow.py

# 启动开发服务器
python quick_start_server.py

# 查看项目状态
python test_server_status.py

# 构建生产版本
cd web/frontend && npm run build
```

## ⚠️ 注意事项

1. **AI API密钥**: 确保.env文件中配置了DEEPSEEK_API_KEY
2. **跨域问题**: 开发时前端5173端口需要代理到后端8000端口
3. **WebSocket**: 确保WebSocket连接使用正确的URL
4. **状态同步**: Pinia store和后端状态保持一致

---

*使用这些Prompt时，请提供具体的代码上下文和错误信息，以获得更准确的帮助。*
