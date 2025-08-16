# 🤖 RuleK Agent系统使用指南

## 概述

Agent系统是RuleK项目的**智能操作规范系统**，确保所有AI（包括Claude、ChatGPT等）在操作项目时遵循统一规范，避免：
- 在根目录乱创建文件
- 创建 `xxx_enhanced.py` 而不是修改原文件
- 不检查文件存在就创建新文件
- 在错误的目录放置文件

## 🏗️ Agent系统架构

```
主Agent (MAIN_AGENT.md)
    ├── 文档Agent (docs/.DOCS_AGENT.md)
    ├── 脚本Agent (scripts/.SCRIPTS_AGENT.md)
    ├── 后端Agent (web/backend/.BACKEND_AGENT.md)
    ├── 前端Agent (web/frontend/.FRONTEND_AGENT.md)
    ├── 测试Agent (tests/.TEST_AGENT.md)
    └── 源码Agent (src/.SRC_AGENT.md)
```

## 🎯 核心原则

### 1. 缝缝补补 > 推倒重来
- ✅ 优先使用 `edit_file` 修改现有文件
- ❌ 避免创建 `xxx_new.py`、`xxx_enhanced.py`

### 2. 检查优先
- ✅ 先 `read_file` 查看文件是否存在
- ❌ 不要直接 `write_file` 覆盖

### 3. 位置正确
- ✅ 测试文件放 `tests/`
- ✅ 脚本放 `scripts/`
- ❌ 不在根目录创建代码文件

## 📖 使用方法

### 对于AI助手

当你请求AI（Claude/ChatGPT）帮助时，可以这样说：

```
请先读取 MAIN_AGENT.md 文件了解项目规范，
然后帮我修复 web/backend/app.py 中的WebSocket问题。
记住：优先修改现有文件，不要创建新文件。
```

### 对于开发者

使用验证器检查操作：

```bash
# 检查文件操作是否合规
python scripts/agent_validator.py --check create --path /test.py

# 生成特定任务的Agent上下文
python scripts/agent_validator.py --context backend

# 验证AI的操作计划
python scripts/agent_validator.py --validate-plan plan.json
```

## 🔍 Agent规则速查

### 文件操作决策树

```
需要改代码？
├─ 文件存在吗？
│  ├─ 是 → edit_file 修改
│  └─ 否 → 真的需要创建吗？
│           └─ 是 → 在正确目录创建
└─ 放在哪里？
   ├─ 测试 → tests/
   ├─ 脚本 → scripts/
   ├─ 后端 → web/backend/
   ├─ 前端 → web/frontend/
   └─ 核心 → src/
```

### 命名规范速查

| 类型 | ✅ 正确 | ❌ 错误 |
|------|---------|---------|
| Python文件 | `game_service.py` | `gameService.py` |
| 测试文件 | `test_websocket.py` | `websocket_test.py` |
| Vue组件 | `GameBoard.vue` | `game-board.vue` |
| 修复脚本 | `fix_imports.py` | `fix_imports_new.py` |

### 禁止创建列表

永远不要创建这些文件：
- ❌ `*_enhanced.py`
- ❌ `*_new.py`
- ❌ `*_fixed.py`
- ❌ `*_v2.py`
- ❌ `*_updated.py`
- ❌ 根目录的 `test_*.py`
- ❌ 根目录的 `fix_*.py`

## 🛠️ Agent验证器

### 功能特性

1. **操作验证**：检查文件操作是否符合规范
2. **路径建议**：自动建议正确的文件位置
3. **命名检查**：验证文件命名是否规范
4. **上下文生成**：为AI生成必要的规则上下文
5. **计划验证**：验证AI的操作计划

### 使用示例

```python
# plan.json - AI的操作计划
[
    {"action": "read_file", "path": "web/backend/app.py"},
    {"action": "edit_file", "path": "web/backend/app.py", "changes": [...]},
    {"action": "write_file", "path": "tests/test_websocket.py", "content": "..."}
]

# 验证计划
python scripts/agent_validator.py --validate-plan plan.json
```

## 📊 效果对比

### 使用Agent系统前
```
RuleK/
├── test_websocket.py        # ❌ 根目录
├── fix_bug.py               # ❌ 根目录
├── app_enhanced.py          # ❌ 增强版
├── service_new.py           # ❌ 新版本
└── 一堆临时文件...          # ❌ 混乱
```

### 使用Agent系统后
```
RuleK/
├── scripts/
│   └── test/
│       └── test_websocket.py  # ✅ 正确位置
├── web/backend/
│   └── app.py                 # ✅ 直接修改
└── 整洁的项目结构             # ✅ 专业
```

## 🚀 快速开始

1. **AI开始任务前**
   ```
   先读取 MAIN_AGENT.md
   ```

2. **操作文件时**
   ```
   优先 edit_file，避免 write_file
   ```

3. **不确定时**
   ```
   运行 agent_validator.py 验证
   ```

## 💡 最佳实践

### DO ✅
- 先读取Agent规则
- 检查文件是否存在
- 使用正确的目录结构
- 保持命名一致性
- 修改而不是重写

### DON'T ❌
- 在根目录创建代码文件
- 创建增强版/新版本文件
- 跳过文件存在检查
- 使用随意的命名
- 重复造轮子

## 🔧 维护与更新

Agent规则会随项目发展更新。更新规则时：

1. 修改对应的 `*_AGENT.md` 文件
2. 运行验证器确保规则一致
3. 通知团队成员更新

## 📞 需要帮助？

- 查看主Agent：`MAIN_AGENT.md`
- 查看具体Agent：各目录下的 `.xxx_AGENT.md`
- 运行验证器：`python scripts/agent_validator.py`

---

**记住核心理念：缝缝补补，而不是推倒重来！**

*Agent系统版本：1.0.0*
*最后更新：2024-12-22*