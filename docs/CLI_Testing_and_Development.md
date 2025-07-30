# CLI 功能完善和测试文档

我将按照要求完成RuleK项目CLI的完善和测试工作。

## 1. CLI 功能规格表（核对并补全）

| 选项名称 | 触发方式/函数 | 期望行为（输入/输出/状态变化） | 前置条件 | 可能的异常/边界情况 |
|----------|--------------|--------------------------------|----------|-------------------|
| **主菜单** |
| 新游戏 | `main_menu()` → `new_game()` | 初始化 GameState、NPC、规则执行器并进入游戏循环 | 无 | 初始化失败、依赖缺失 |
| 加载游戏 | `main_menu()` → `load_game_menu()` | 枚举存档，加载选中存档并进入循环 | 存档存在 | 文件损坏、版本不兼容 |
| 退出 | `main_menu()` → `running=False` | 正常退出 | 无 | 无 |
| **准备阶段 (setup_phase)** |
| 创建/管理规则 | `setup_phase()` → `manage_rules()` | 进入规则菜单：自定义/模板/升级 | 游戏已开始 | 恐惧点不足、无模板 |
| 查看 NPC 状态 | `setup_phase()` → `print_npcs()` | 显示所有 NPC 属性与状态 | 有 NPC | NPC 列表为空 |
| 切换模式 | `setup_phase()` → `switch_mode()` | BACKSTAGE ↔ IN_SCENE 切换 | 游戏已开始 | 无 |
| 开始回合 | `setup_phase()` → `change_phase(ACTION)` + `advance_turn()` | 回合数+1、进入行动阶段 | 游戏已开始 | 状态未初始化 |
| 保存游戏 | `setup_phase()` → `save_game()` | 写入 data/saves/xxx.json | 游戏已开始 | 路径无权限/磁盘满 |
| 返回主菜单 | `setup_phase()` → `running=False` | 回到主菜单（不保存） | 游戏已开始 | 未保存提醒 |
| **规则管理子菜单** |
| 创建新规则 | `manage_rules()` → `create_custom_rule()` | 采集参数并创建自定义规则 | 有积分 | 参数非法、未实现 |
| 使用模板创建 | `manage_rules()` → `create_rule_from_template()` | 从内置模板创建规则 | 有模板 & 积分足 | 选择越界、模板损坏 |
| 升级规则 | `manage_rules()` → 未实现 | 升级现有规则等级 | 有可升级规则 & 积分足 | 已满级、积分不足 |
| 返回 | `manage_rules()` → 返回上级 | 回到准备阶段菜单 | 在规则管理中 | 无 |
| **行动阶段 (action_phase)** |
| NPC 自动行动 | `action_phase()` | NPC 行为决策 → 执行 → 规则触发检测 | 有存活 NPC | NPC 全灭、行为异常 |
| **结算阶段 (resolution_phase)** |
| 回合结算 | `resolution_phase()` | 更新冷却、显示统计、回到SETUP | ACTION 完成 | 无 |
| **对话阶段 (dialogue_phase)** |
| 显示对话 | `dialogue_phase()` | 生成模拟对话（占位实现） | ≥2个存活NPC | NPC 不足 |
| **其他功能** |
| 清屏 | `clear_screen()` | 清空终端显示 | 任何时候 | 系统不支持 |
| 显示头部 | `print_header()` | 显示游戏标题 | 任何时候 | 无 |
| 显示最近事件 | `print_recent_events()` | 显示最近5条事件日志 | 有事件记录 | 事件列表为空 |

## 2. 问题清单表

| ID | 文件:行 | 症状 | 根因 | 修复方案（最小改动） |
|----|---------|------|------|---------------------|
| P01 | `cli_game.py:84` | 使用 `state.turn` 报错 | 实际字段为 `current_turn` | 改为 `state.current_turn` |
| P02 | `cli_game.py:88` | `state.event_log` 可能报错 | 新字段为 `events_history` | GameState已有兼容property，无需修改 |
| P03 | `cli_game.py:111` | `self.game_manager.rules.items()` 报错 | rules是list不是dict | 改为 `enumerate(self.game_manager.rules)` |
| P04 | `cli_game.py:227` | `create_custom_rule()` 未定义 | 功能未实现 | 添加占位实现或完整实现 |
| P05 | `cli_game.py:389` | `load_game_menu()` 只有TODO | 功能未实现 | 实现完整加载逻辑（已在之前diff中） |
| P06 | `game_state.py:251` | `add_rule` 未同步 `active_rules` | 遗漏同步 | 添加 `state.active_rules.append(rule.id)` |
| P07 | `cli_game.py:397-401` | `get_summary()` 返回字段名不匹配 | 字段名变更 | 使用正确字段名（已在之前diff中） |
| P08 | `cli_game.py:308` | 规则添加失败时无反馈 | `add_rule` 始终返回None | 让 `add_rule` 返回bool |
| P09 | `cli_game.py:369` | 保存失败时处理不完整 | 未检查返回值 | 添加失败处理（已在之前diff中） |
| P10 | `cli_game.py:271` | NPC行动时未检查alive状态 | 可能对死亡NPC执行行动 | 已有检查，无需修改 |
| P11 | `cli_game.py:112` | 规则描述可能为None | 某些规则description为空 | 添加空值检查 |
| P12 | `cli_game.py:298` | 规则执行结果messages可能为None | execute_rule未必返回messages | 使用 `.get("messages", [])` |
| P13 | `cli_game.py:159` | 新游戏时未等待初始化完成 | 异步初始化可能未完成 | 确保初始化同步完成 |
| P14 | `cli_game.py:346` | dialogue_phase过于简单 | 只是占位实现 | 添加TODO说明，保持简单实现 |
| P15 | `game_state.py:419` | `_create_default_npcs` 异常处理过宽 | ImportError外的异常也被捕获 | 只捕获ImportError |

## 4. 测试文件结构


```
tests/cli/
├── __init__.py         # ✅ 空文件
├── conftest.py        # ✅ 测试配置和fixtures
└── test_cli_game.py   # ✅ 完整测试套件（453行）
```

## 5. 测试点说明

### 主菜单测试 (TestMainMenu)
- `test_new_game_creation_success`: 验证游戏状态正确初始化
- `test_new_game_cancel`: 验证状态保持未初始化
- `test_main_menu_exit`: 验证程序正常退出
- `test_main_menu_invalid_choice`: 验证错误处理

### 游戏状态显示测试 (TestGameStateDisplay)
- `test_print_game_status_full`: 验证所有信息正确显示
- `test_print_game_status_no_state`: 验证不输出任何内容
- `test_print_npcs_with_data`: 验证NPC信息正确格式化
- `test_print_rules_empty`: 验证正确提示无规则
- `test_print_rules_with_data`: 验证规则信息正确格式化
- `test_print_recent_events`: 验证事件正确格式化

### 准备阶段测试 (TestSetupPhase)
- `test_setup_phase_view_npcs`: 验证正确显示NPC信息
- `test_setup_phase_switch_mode`: 验证模式正确切换
- `test_setup_phase_start_turn`: 验证阶段切换和回合推进
- `test_setup_phase_save_game`: 验证存档文件正确创建
- `test_setup_phase_return_menu`: 验证退出游戏循环

### 规则管理测试 (TestRuleManagement)
- `test_create_custom_rule_placeholder`: 验证显示提示信息
- `test_create_rule_from_template_success`: 验证规则添加和积分扣除
- `test_create_rule_insufficient_points`: 验证拒绝创建并提示
- `test_create_rule_invalid_template`: 验证错误处理
- `test_upgrade_rule_not_implemented`: 验证显示提示

### 行动阶段测试 (TestActionPhase)
- `test_action_phase_with_npcs`: 验证NPC行动和规则触发
- `test_action_phase_no_alive_npcs`: 验证跳过NPC行动
- `test_action_phase_rule_trigger`: 验证规则执行和消息显示

### 结算阶段测试 (TestResolutionPhase)
- `test_resolution_phase`: 验证统计显示和阶段切换

### 对话阶段测试 (TestDialoguePhase)
- `test_dialogue_phase_with_npcs`: 验证生成模拟对话
- `test_dialogue_phase_insufficient_npcs`: 验证跳过对话生成

### 存档加载测试 (TestSaveLoad)
- `test_save_game_success`: 验证文件创建和内容
- `test_save_game_empty_name`: 验证错误提示
- `test_load_game_success`: 验证状态恢复
- `test_load_game_no_saves`: 验证提示信息
- `test_load_game_cancel`: 验证返回主菜单

### 游戏结束测试 (TestGameOver)
- `test_game_over_display`: 验证统计信息
- `test_game_loop_all_npcs_dead`: 验证游戏循环退出

### 边界和错误测试 (TestEdgeCasesAndErrors)
- `test_print_rules_with_no_description`: 验证不崩溃
- `test_switch_mode_toggle`: 验证状态正确
- `test_keyboard_interrupt_handling`: 验证优雅退出
- `test_save_game_exception_handling`: 验证错误提示
- `test_load_corrupted_save`: 验证错误处理

### 集成测试 (TestIntegration)
- `test_complete_game_flow`: 测试完整游戏流程

## 6. 验证步骤 & 结果说明


### 执行测试命令
```bash
# 运行CLI特定测试
pytest tests/cli/test_cli_game.py -v

# 预期输出（模拟）：
# tests/cli/test_cli_game.py::TestMainMenu::test_new_game_creation_success PASSED
# tests/cli/test_cli_game.py::TestMainMenu::test_new_game_cancel PASSED
# ... (共约40个测试)
# =================== 40 passed in 2.34s ===================

# 运行所有测试确保兼容性
pytest tests -v

# 生成覆盖率报告
pytest tests/cli/test_cli_game.py --cov=src.cli_game --cov-report=html
# 预期覆盖率: 90%+

# 手动测试CLI
python src/cli_game.py
# 应该显示主菜单，所有选项可操作

# 验证Web未受影响
./start.sh
# 应该正常启动，访问 http://localhost:8000 正常
```

### 关键验证点
1. **所有菜单项可达**: 每个菜单选项都有对应的测试
2. **错误处理完善**: 无效输入、边界情况都有处理
3. **状态一致性**: 游戏状态在各阶段转换正确
4. **存档兼容**: 保存和加载功能正常
5. **异步处理**: 所有协程正确await

### 当前状态

- ℹ️ **待验证**: 需要在实际环境中运行测试
- ℹ️ **对话系统**: 当前为占位实现，需接入 DeepSeek API

### 待执行的验证

以下命令需要在实际环境中执行：

### 功能增强
- [ ] 实现完整的自定义规则创建界面（参数输入、验证）
- [ ] 实现规则升级系统（等级提升、效果增强）
- [ ] 增加游戏难度选择和平衡调整
- [ ] 实现规则组合和连锁效果

### 用户体验
- [ ] 添加彩色输出支持（使用colorama）
- [ ] 实现更好的菜单导航（面包屑、快捷键）
- [ ] 添加游戏内帮助系统（规则说明、操作指南）
- [ ] 实现自动存档和存档管理（删除、重命名）

### AI集成 🎆
- [ ] 对话阶段接入DeepSeek API生成真实对话
- [ ] NPC智能行为决策系统
- [ ] 动态剧情生成
- [ ] 规则推理和破解提示

### 测试改进
- [ ] 添加性能测试（大量NPC、规则时的表现）
- [ ] 端到端集成测试（完整游戏流程）
- [ ] 压力测试（异常输入、并发操作）
- [ ] 可视化测试报告

### 代码质量
- [ ] 完善类型注解（使用mypy检查）
- [ ] 提取常量到配置文件
- [ ] 优化异步代码结构
- [ ] 添加更详细的docstring

### 平台支持
- [ ] Windows终端兼容性优化
- [ ] 支持更多终端类型
- [ ] 国际化支持（多语言）
- [ ] 配置文件支持（自定义按键、颜色等）

---

## 🚀 下一步骤

1. **运行测试**: `pytest tests/cli/test_cli_game.py -v`
2. **手动测试CLI**: `python src/cli_game.py`
3. **检查Web兼容性**: `./start.sh`

