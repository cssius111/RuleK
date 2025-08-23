# 前端API导入修复记录

## 问题描述
日期：2025-01-08

### 错误信息
```
No matching export in "src/api/index.ts" for import "api"
```

### 问题根因
- `src/stores/rules.ts` 尝试从 `@/api` 导入命名导出 `api`
- `src/api/index.ts` 只提供了默认导出 `apiClient`
- 导入/导出名称不匹配导致构建失败

## 解决方案

### 修改文件
`web/frontend/src/api/index.ts`

### 修改内容
在文件末尾添加命名导出：
```typescript
export default apiClient
export { apiClient as api }  // 添加命名导出，供 stores 使用
```

### 为什么选择这个方案
1. **最小改动原则**：只修改一个文件，不需要改动所有使用 `api` 的地方
2. **向后兼容**：保留原有的默认导出，不影响其他可能使用默认导出的组件
3. **符合项目规范**：遵循 MAIN_AGENT.md 的"优先修改，避免创建"原则

## 影响范围
- ✅ `src/stores/rules.ts` - 现在可以正常导入 `api`
- ✅ 其他使用默认导出的组件不受影响
- ✅ 前端构建和启动恢复正常

## 验证方法
1. 运行 `npm run dev` 确认没有构建错误
2. 访问 http://localhost:5173 确认前端正常加载
3. 检查浏览器控制台没有导入相关错误

## 相关文件
- `/web/frontend/src/api/index.ts` - API客户端主文件
- `/web/frontend/src/stores/rules.ts` - 规则管理Store
- `/web/frontend/src/api/gameApi.ts` - 游戏API（使用默认导入，不受影响）

## 后续建议
1. 考虑统一项目中的导入风格（全部使用命名导出或全部使用默认导出）
2. 在代码审查中注意导入/导出的一致性
3. 可以考虑添加 ESLint 规则检查导入问题

---
*修复人：AI Assistant*
*修复时间：2025-01-08*
