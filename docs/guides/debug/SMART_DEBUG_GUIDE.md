# 🛠️ RuleK 智能调试指南

## 问题：AI功能总是失败，pytest不全

我为你创建了一套智能调试工具，可以自动检测和修复大部分问题。

## 🚀 快速开始

### 1. 使用一键调试工具（最简单）

```bash
python debug_rulek.py
```

选择选项：
- **1** - 智能诊断（找出所有问题）
- **2** - 自动修复测试（修复测试问题）
- **3** - 优化AI功能（专门处理AI问题）
- **4** - 快速启动游戏
- **5** - 运行所有检查（全面诊断）

### 2. 各工具详细说明

#### 🔍 智能诊断工具 (`smart_debug.py`)

自动检查：
- Python环境和版本
- 依赖包安装情况
- 配置文件完整性
- 代码健康度
- AI功能可用性
- 测试套件状态

```bash
python smart_debug.py
```

生成报告：`debug_report.md`

#### 🔧 自动测试修复工具 (`auto_test_fix.py`)

功能：
- 自动修复已知代码问题
- 运行测试并分析失败原因
- 提供针对性的修复建议
- 生成测试报告

```bash
python auto_test_fix.py
```

自动修复的问题：
- `self.game_mgr.state.rules` → `self.game_mgr.rules`
- `turn_count` → `current_turn`
- Pydantic v1语法 → v2语法
- 导入路径错误

生成报告：`test_fix_report.md`

#### 🤖 AI优化工具 (`optimize_ai.py`)

专门优化AI功能：
- 检查API配置
- 测试AI连接
- 创建增强Mock模式
- 优化AI调用性能
- 提供降级方案

```bash
python optimize_ai.py
```

生成报告：`ai_optimization_report.md`

## 📋 常见问题快速解决

### 1. AI总是失败

**原因**：
- 没有设置API密钥
- 网络连接问题
- 代码中的属性错误

**解决**：
```bash
# 运行AI优化
python optimize_ai.py

# 如果没有API密钥，工具会自动创建Mock模式
# 让你无需真实API也能测试
```

### 2. pytest测试不通过

**原因**：
- 导入路径错误
- 代码中的属性访问错误
- Pydantic版本不兼容

**解决**：
```bash
# 自动修复并运行测试
python auto_test_fix.py

# 工具会：
# 1. 扫描并修复已知问题
# 2. 运行测试
# 3. 分析失败原因
# 4. 提供修复建议
```

### 3. 不知道哪里有问题

**解决**：
```bash
# 运行完整诊断
python debug_rulek.py
# 选择 5 - 运行所有检查
```

## 🎯 调试工作流程

### 推荐的调试流程：

1. **首次调试**
   ```bash
   python debug_rulek.py
   # 选择 5 - 运行所有检查
   ```

2. **查看报告**
   - `debug_report.md` - 环境和配置问题
   - `test_fix_report.md` - 测试问题
   - `ai_optimization_report.md` - AI相关问题

3. **根据报告修复**
   - 高优先级问题先修复
   - 运行建议的命令
   - 应用代码修改

4. **验证修复**
   ```bash
   # 重新运行相关工具验证
   python auto_test_fix.py  # 验证测试
   python optimize_ai.py    # 验证AI
   ```

## 💡 最佳实践

### 1. 使用Mock模式开发

如果没有API密钥或网络不稳定：
- AI优化工具会自动创建Mock模式
- 可以在`src/api/mock_ai.py`中自定义Mock行为
- 开发时用Mock，生产时用真实API

### 2. 测试驱动调试

```bash
# 每次修改后运行
python auto_test_fix.py

# 只运行特定测试
pytest tests/unit/test_specific.py -v
```

### 3. 保持代码健康

定期运行：
```bash
python smart_debug.py
```

及时修复发现的问题。

## 🆘 还是有问题？

如果工具无法解决你的问题：

1. **查看详细日志**
   ```bash
   # 运行时添加 -v 参数
   pytest -vvs --tb=long
   ```

2. **手动调试**
   - 在代码中添加print语句
   - 使用Python调试器：`import pdb; pdb.set_trace()`

3. **检查具体错误**
   - ImportError：检查文件是否存在，路径是否正确
   - AttributeError：检查对象属性，可能需要更新代码
   - TypeError：检查函数参数，可能API变更

## 📊 工具对比

| 工具 | 用途 | 何时使用 |
|------|------|----------|
| smart_debug.py | 全面诊断 | 首次调试或大问题 |
| auto_test_fix.py | 测试修复 | pytest失败时 |
| optimize_ai.py | AI优化 | AI功能异常时 |
| debug_rulek.py | 统一入口 | 不确定用哪个时 |

## 🎉 总结

这套工具可以解决90%以上的常见问题：

1. **智能诊断** - 找出所有问题
2. **自动修复** - 修复已知问题
3. **优化建议** - 提供改进方案
4. **Mock支持** - 无需真实API也能开发

现在你可以：
```bash
# 立即开始调试
python debug_rulek.py
```

祝调试顺利！🚀
