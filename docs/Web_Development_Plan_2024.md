# RuleK Web功能完善计划

## 📅 计划生成日期：2024-12-21

## 🔍 当前状态评估

### ✅ 已完成功能
1. **基础架构**
   - 前端Vue3 + TypeScript框架搭建完成
   - 后端FastAPI服务器运行正常
   - WebSocket连接已建立
   - 基础路由和页面结构完成

2. **游戏核心功能**
   - 游戏创建和初始化
   - 游戏状态管理（Pinia store）
   - NPC显示和状态更新
   - 事件日志显示
   - 回合推进基础功能

### ❌ 待修复问题

1. **规则创建功能未连接**
   - 问题：ActionButtons组件发出'create-rule'事件，但GameView未监听
   - 解决方案：在GameView.vue中添加事件监听器
   ```vue
   <ActionButtons @create-rule="showRuleCreator = true" />
   ```

2. **规则创建模态框未触发**
   - RuleCreatorModal组件存在但未正确触发显示
   - 需要修复事件绑定

3. **AI功能集成不完整**
   - AI规则解析端点存在但前端未完全集成
   - 需要添加AI规则创建选项

## 🎯 开发任务列表

### 第一阶段：修复规则创建（1-2天）

#### 1.1 修复规则创建触发
```typescript
// GameView.vue 修改
<ActionButtons 
  @create-rule="showRuleCreator = true"
/>

// 确保showRuleCreator响应式变量正确定义
const showRuleCreator = ref(false)
```

#### 1.2 完善规则创建表单
- [ ] 添加规则模板选择
- [ ] 实现自定义规则表单验证
- [ ] 添加成本计算显示
- [ ] 实现规则预览功能

#### 1.3 集成AI规则解析
```typescript
// 添加AI规则创建选项
interface RuleCreationMode {
  custom: '自定义规则',
  template: '模板规则',
  ai: 'AI智能创建'
}

// AI规则解析API调用
async function parseRuleWithAI(description: string) {
  const response = await api.post(`/games/${gameId}/ai/evaluate-rule`, {
    description,
    game_state: gameStore.gameState
  })
  return response.data
}
```

### 第二阶段：完善游戏交互（2-3天）

#### 2.1 规则管理界面
- [ ] 规则列表展示优化
- [ ] 规则详情查看
- [ ] 规则升级功能
- [ ] 规则删除/禁用

#### 2.2 NPC交互增强
- [ ] NPC详细信息弹窗
- [ ] NPC行动历史查看
- [ ] NPC状态实时更新动画
- [ ] 死亡NPC特殊显示

#### 2.3 回合推进优化
- [ ] 对话阶段展示
- [ ] 行动阶段动画
- [ ] 规则触发特效
- [ ] 回合结算详情

### 第三阶段：AI功能深度集成（3-4天）

#### 3.1 AI回合生成
```typescript
// 实现AI回合功能
interface AITurnResult {
  dialogues: NPCDialogue[]
  actions: NPCAction[]
  narrative: string
  events: GameEvent[]
}

async function generateAITurn(): Promise<AITurnResult> {
  const response = await api.post(`/games/${gameId}/ai/turn`)
  return response.data
}
```

#### 3.2 AI叙事生成
- [ ] 实时叙事生成
- [ ] 叙事风格选择
- [ ] 叙事历史查看
- [ ] 叙事导出功能

#### 3.3 智能提示系统
- [ ] 规则创建建议
- [ ] 策略提示
- [ ] 游戏进度分析
- [ ] 胜利条件预测

### 第四阶段：UI/UX优化（2-3天）

#### 4.1 视觉效果增强
- [ ] 暗黑恐怖主题优化
- [ ] 动画和过渡效果
- [ ] 音效集成（可选）
- [ ] 响应式设计完善

#### 4.2 用户体验改进
- [ ] 快捷键支持完善
- [ ] 拖拽操作支持
- [ ] 批量操作功能
- [ ] 撤销/重做功能

#### 4.3 性能优化
- [ ] 组件懒加载
- [ ] 状态管理优化
- [ ] WebSocket重连机制
- [ ] 缓存策略实施

### 第五阶段：测试和部署（2-3天）

#### 5.1 自动化测试
- [ ] 单元测试覆盖率提升
- [ ] E2E测试场景完善
- [ ] 性能测试
- [ ] 兼容性测试

#### 5.2 部署准备
- [ ] 生产环境配置
- [ ] Docker镜像优化
- [ ] CI/CD流程配置
- [ ] 监控和日志系统

## 📊 技术债务清理

1. **代码规范化**
   - TypeScript类型定义完善
   - 组件props验证
   - 错误边界处理
   - 代码注释补充

2. **架构优化**
   - 组件拆分和复用
   - 状态管理规范化
   - API请求统一处理
   - 错误处理机制

3. **文档完善**
   - API文档更新
   - 组件文档编写
   - 用户手册编写
   - 部署文档完善

## 🚀 快速修复脚本

### 修复规则创建按钮
```bash
cat << 'EOF' > fix_rule_creation.sh
#!/bin/bash

# 修复GameView.vue中的事件监听
sed -i '' 's/<ActionButtons \/>/<ActionButtons @create-rule="showRuleCreator = true" \/>/g' \
  web/frontend/src/views/GameView.vue

echo "✅ 规则创建按钮事件监听已修复"
EOF

chmod +x fix_rule_creation.sh
./fix_rule_creation.sh
```

### 测试规则创建功能
```python
# test_rule_creation.py
import asyncio
from playwright.async_api import async_playwright

async def test_rule_creation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 导航到游戏页面
        await page.goto("http://localhost:5173")
        
        # 创建新游戏
        await page.click("text=开始新游戏")
        await page.fill('input[type="number"]', "1000")
        await page.click("text=创建游戏")
        
        # 等待游戏页面加载
        await page.wait_for_url("**/game/**")
        
        # 点击创建规则按钮
        await page.click("text=创建规则")
        
        # 检查模态框是否出现
        modal = await page.wait_for_selector(".n-modal", timeout=5000)
        
        if modal:
            print("✅ 规则创建模态框成功显示")
        else:
            print("❌ 规则创建模态框未显示")
        
        await browser.close()

asyncio.run(test_rule_creation())
```

## 📈 预期成果

### 短期目标（1周内）
- ✅ 规则创建功能完全可用
- ✅ AI功能基础集成
- ✅ 核心游戏循环完整

### 中期目标（2周内）
- ✅ 所有主要功能实现
- ✅ UI/UX达到可发布标准
- ✅ 测试覆盖率>80%

### 长期目标（1个月内）
- ✅ 生产环境部署
- ✅ 性能优化完成
- ✅ 用户文档齐全
- ✅ 社区反馈机制建立

## 🔧 开发环境设置

```bash
# 前端开发
cd web/frontend
npm install
npm run dev

# 后端开发
cd web/backend
pip install -r requirements.txt
python app.py

# 运行测试
pytest tests/
npm run test

# 运行Playwright测试
npx playwright test
```

## 📝 注意事项

1. **优先级管理**
   - 先修复阻塞性bug
   - 核心功能优先于美化
   - 用户体验优于技术完美

2. **版本控制**
   - 每个功能独立分支
   - 频繁提交和推送
   - 详细的commit message

3. **测试驱动**
   - 先写测试再实现
   - 保持测试覆盖率
   - 自动化测试优先

4. **代码审查**
   - 重要功能需review
   - 遵循代码规范
   - 及时重构技术债务

---

*计划制定时间：2024-12-21*
*预计完成时间：2025-01-15*
*负责人：开发团队*
