# 更新日志

## 2025-08-26
### 重构
- 更新 MAIN_AGENT 与脚本规则，新增 startup 脚本分类
- modularize run_pytest，确保测试环境包含项目根目录

### 修复
- 解决 `python rulek.py test` 无法导入 `web.backend` 的问题

## 2025-08-23
### 新增
- 支持向 DeepSeekClient 注入自定义 httpx.AsyncClient，可在 AITurnPipeline 与 GameService 中传递。
### 修复
- 处理 DeepSeek API 返回空内容或无效 JSON 的容错逻辑，并添加相关单元测试。

