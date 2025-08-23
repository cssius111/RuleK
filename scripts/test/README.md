# RuleK API 测试工具使用指南

## 🚀 快速开始

### 最简单的方法：一键重启和测试
```bash
python scripts/test/restart_and_test.py
```
这会自动：
1. 停止现有服务器
2. 启动新服务器
3. 验证所有修复
4. 可选运行完整测试

## 📦 工具列表

### 测试工具

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `restart_and_test.py` | 一键重启和测试 | 修改代码后快速验证 |
| `quick_api_test.py` | 快速API测试 | 日常开发测试 |
| `test_api_comprehensive.py` | 综合测试 | 完整功能验证 |
| `verify_fixes.py` | 修复验证 | 确认问题已解决 |

### 修复工具

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `fix_api.py` | 自动诊断和修复 | 发现问题时运行 |
| `quick_fix_api_issues.py` | 问题说明 | 查看已修复的问题 |

## 📝 使用示例

### 场景1：修改代码后测试
```bash
# 最佳选择：一键重启和测试
python scripts/test/restart_and_test.py
```

### 场景2：快速测试单个功能
```bash
# 使用交互式测试工具
python scripts/test/quick_api_test.py
# 选择想要测试的功能
```

### 场景3：完整测试所有API
```bash
# 确保服务器运行
python rulek.py web

# 新终端运行测试
python scripts/test/test_api_comprehensive.py
```

### 场景4：诊断和修复问题
```bash
# 运行诊断
python scripts/fix/fix_api.py

# 验证修复
python scripts/test/verify_fixes.py
```

## 🔍 测试覆盖

### 基础功能
- ✅ 健康检查
- ✅ 游戏创建和管理
- ✅ NPC管理

### 规则系统
- ✅ 创建规则
- ✅ 获取规则模板
- ✅ 计算规则成本

### AI功能
- ✅ AI初始化
- ✅ AI回合执行
- ✅ 叙事生成
- ✅ 规则解析

### 游戏流程
- ✅ 推进回合
- ✅ 保存游戏
- ✅ 加载游戏

## 📊 测试报告解读

### 成功输出示例
```
✅ 服务器运行正常
✅ 游戏创建成功: game_abc123
✅ 规则创建成功 - 问题1已修复
✅ 成本计算成功: 150点 - 问题2已修复
✅ 推进回合成功 - 问题3已修复
✅ 保存游戏成功: save_game_abc123.json - 问题4已修复
🎉 所有修复验证通过！
```

### 失败输出示例
```
❌ 规则创建失败: 422
   响应: {"detail": [{"type": "missing", "loc": ["body", "effect"]}]}
⚠️ 仍有问题需要解决
```

## 🛠️ 故障排查

### 服务器无法启动
```bash
# 检查端口占用
lsof -i:8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# 强制停止占用进程
kill -9 $(lsof -ti:8000)  # Mac/Linux
```

### 测试失败
1. 查看服务器日志（在运行服务器的终端）
2. 检查`logs/`目录下的日志文件
3. 使用交互式测试工具逐个测试

### 导入错误
```bash
# 安装缺失依赖
pip install -r requirements.txt
```

## 📈 性能基准

| 操作 | 期望时间 | 超时阈值 |
|------|---------|---------|
| 创建游戏 | <500ms | 5s |
| 创建规则 | <200ms | 3s |
| 推进回合 | <1s | 10s |
| AI回合 | <5s | 30s |
| 保存游戏 | <500ms | 5s |

## 🎯 最佳实践

1. **定期运行测试** - 每次重要修改后运行
2. **使用一键工具** - `restart_and_test.py`最方便
3. **查看日志** - 失败时检查服务器输出
4. **增量测试** - 先运行快速测试，再运行综合测试

## 📚 相关文档

- [API测试指南](../docs/API_TEST_GUIDE.md)
- [API修复报告](../docs/API_FIX_REPORT.md)
- [项目计划](../PROJECT_PLAN.md)

---

*更新时间: 2024-12-22*
