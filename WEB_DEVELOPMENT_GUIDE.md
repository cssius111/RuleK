# RuleK Web UI 开发指南

## 🎯 项目目标

将RuleK从CLI游戏转变为现代化的Web应用，实现：
- 100% 功能覆盖
- AI核心化集成
- 实时交互体验
- 响应式设计

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装依赖
npm run setup

# 安装Playwright浏览器
npm run setup:playwright

# 验证环境
npm run test:phase0
```

### 2. 启动开发
```bash
# 启动前后端
npm start

# 或分别启动
npm run backend  # 后端 http://localhost:8000
npm run dev      # 前端 http://localhost:3000
```

### 3. 运行测试
```bash
# 运行所有测试
npm test

# 运行特定阶段测试
npm run test:phase1

# 调试模式
npm run test:debug
```

## 📊 开发阶段与成功标准

### Phase 0: 环境准备 (Day 1)
**成功标准:**
- ✅ 开发服务器可访问
- ✅ API服务器可访问
- ✅ WebSocket连接正常

**验证命令:**
```bash
npm run test:phase0
npm run track:phase0
npm run report:phase0
```

### Phase 1: 基础框架 (Day 2-3)
**成功标准:**
- ✅ 路由系统工作
- ✅ 状态管理就绪
- ✅ 响应式布局

**关键文件:**
- `web/frontend/src/router/index.ts`
- `web/frontend/src/stores/game.ts`
- `web/frontend/src/App.vue`

### Phase 2: 游戏创建流程 (Day 4-5)
**成功标准:**
- ✅ 新游戏创建
- ✅ 存档加载
- ✅ 参数验证

**关键功能:**
- 游戏配置表单
- 存档列表展示
- API集成

### Phase 3: 游戏核心界面 (Day 6-8)
**成功标准:**
- ✅ 游戏主界面完成
- ✅ 回合推进正常
- ✅ WebSocket实时更新

**关键组件:**
- `GameDashboard.vue`
- `StatusBar.vue`
- `EventLog.vue`

### Phase 4: 规则管理系统 (Day 9-11)
**成功标准:**
- ✅ 规则创建向导
- ✅ AI解析功能
- ✅ 模板系统

### Phase 5: NPC和AI系统 (Day 12-14)
**成功标准:**
- ✅ NPC状态展示
- ✅ AI对话生成
- ✅ 流式内容推送

### Phase 6: 优化和完善 (Day 15-16)
**成功标准:**
- ✅ 性能达标 (Lighthouse > 90)
- ✅ 测试覆盖率 > 80%
- ✅ 0关键bug

## 🧪 测试策略

### 单元测试
```bash
npm run test:unit
npm run coverage
```

### E2E测试
```bash
# 无头模式
npm run test:e2e

# 有头模式（可视化）
npm run test:headed

# 调试模式
npm run test:debug
```

### 性能测试
```bash
# Lighthouse测试
npx lighthouse http://localhost:3000

# 查看报告
npm run report
```

## 📈 进度追踪

### 检查当前阶段
```bash
# 运行阶段测试并生成报告
npm run track:phase<n>

# 例如，Phase 1:
npm run track:phase1
```

### 生成进度报告
```bash
# 生成详细报告
npm run report:phase<n>

# 查看报告
open reports/phase<n>_latest.html
```

### 进度仪表板
报告包含：
- 测试结果（单元测试、E2E测试）
- 代码覆盖率
- 性能评分
- 成功标准检查
- 下一步建议

## 🤖 AI辅助开发

### 1. 使用测试助手
```typescript
import { setupHelpers } from './tests/e2e/helpers';

test('游戏流程测试', async ({ page }) => {
  const { game, rule, npc } = setupHelpers(page);
  
  // 创建游戏
  const gameId = await game.createGame({
    fearPoints: 1000,
    difficulty: 'normal'
  });
  
  // 创建规则
  await rule.createCustomRule({
    name: '测试规则',
    triggerType: 'time'
  });
  
  // 验证NPC状态
  await npc.expectNPCStatus('张三', {
    isAlive: true,
    fear: 0
  });
});
```

### 2. 自动生成测试
```bash
# 为组件生成测试
node scripts/generate-tests.js components/GameDashboard.vue
```

### 3. 代码审查
```bash
# AI代码审查
node scripts/code-review.js web/frontend/src/
```

## 📁 项目结构

```
RuleK/
├── web/
│   ├── frontend/          # Vue 3前端
│   │   ├── src/
│   │   │   ├── views/    # 页面组件
│   │   │   ├── components/ # 可复用组件
│   │   │   ├── stores/   # Pinia状态
│   │   │   └── router/   # 路由配置
│   │   └── setup.sh      # 初始化脚本
│   └── backend/          # FastAPI后端
├── tests/
│   └── e2e/             # Playwright测试
│       ├── phase*.spec.ts # 阶段测试
│       └── helpers.ts    # 测试助手
├── scripts/
│   ├── track-progress.js # 进度追踪
│   └── progress_reporter.py # 报告生成
├── reports/             # 测试报告
└── package.json        # 项目配置
```

## 🎯 每日工作流

### 早晨
1. 查看昨日进度报告
2. 确定今日目标
3. 更新任务清单

### 开发中
1. 编写功能代码
2. 编写测试代码
3. 运行测试验证

### 晚上
1. 运行完整测试
2. 生成进度报告
3. 提交代码

```bash
# 完整的每日流程
npm run test            # 运行测试
npm run track:phase<n>  # 检查进度
git add .
git commit -m "Phase <n>: 完成xxx功能"
git push
```

## 📊 成功指标监控

### 实时监控
```bash
# 启动监控面板
npm run monitor
```

监控内容：
- API响应时间
- WebSocket连接状态
- 内存使用
- CPU使用
- 错误率

### KPI仪表板
- 功能完成度: X/Y
- 测试通过率: X%
- 代码覆盖率: X%
- 性能评分: X/100
- Bug数量: X

## 🚨 问题排查

### 常见问题

#### 1. 端口占用
```bash
# 查找占用端口的进程
lsof -i :3000
lsof -i :8000

# 结束进程
kill -9 <PID>
```

#### 2. 测试失败
```bash
# 查看详细日志
npm run test:debug

# 生成测试报告
npm run report
```

#### 3. 性能问题
```bash
# 运行性能分析
npm run perf

# 查看bundle大小
npm run analyze
```

## 🎉 完成标准

项目完成时应满足：

### 功能
- [ ] 100% CLI功能覆盖
- [ ] AI完全集成
- [ ] 实时交互

### 质量
- [ ] 测试覆盖率 > 80%
- [ ] Lighthouse > 90
- [ ] 0关键bug

### 性能
- [ ] 首屏加载 < 2s
- [ ] 交互响应 < 100ms
- [ ] AI响应 < 2s

### 文档
- [ ] 用户手册
- [ ] API文档
- [ ] 开发文档

## 📚 资源链接

- [Vue 3 文档](https://vuejs.org/)
- [Playwright 文档](https://playwright.dev/)
- [Naive UI 组件](https://www.naiveui.com/)
- [项目设计文档](docs/Web_UI_Plan.md)

## 💡 提示

1. **先测试后开发**: 使用TDD方法
2. **小步快跑**: 频繁提交和测试
3. **及时追踪**: 每天生成进度报告
4. **保持同步**: 前后端同步开发

---

祝开发顺利！🚀

如有问题，请查看文档或运行 `npm run help`
