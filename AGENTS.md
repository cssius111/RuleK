# ChatGPT 协作指南

欢迎来到 **RuleK** 项目。本文件为 AI 代理提供协作说明。

## 开发流程

1. **代码格式化与检查**
   - 所有 Python 代码遵循 PEP 8，并使用 `ruff`/`black` 进行格式化。
   - 提交前请运行：
     ```bash
     python scripts/dev_tools.py check
     ```
     该命令会依次执行代码格式化、类型检查、单元测试以及依赖检查。

2. **提交信息**
   - 采用语义化提交格式：
     `feat`、`fix`、`docs`、`style`、`refactor`、`test`、`chore`。
   - 示例：`feat(rule): 添加时间范围检查功能`。

3. **文档更新**
   - 新功能或接口变更需同步更新相关文档（README 或 `docs/` 目录）。

4. **其他注意事项**
   - 保持提交粒度清晰、逻辑自洽。
   - 代码修改完成并通过检查后再创建 Pull Request。

如需更多细节，请查看 `CONTRIBUTING.md`。
