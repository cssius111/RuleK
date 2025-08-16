# 🤖 RuleK 主Agent - AI操作总指挥

## ⚠️ 重要：AI必须先读取此文件再进行任何操作！

## 📋 基本原则

### 1. 文件操作铁律
- **先查看，后操作** - 永远先用 `read_file` 查看文件是否存在
- **优先修改，避免创建** - 能用 `edit_file` 就不要用 `write_file`
- **禁止根目录污染** - 不要在根目录创建临时文件
- **禁止创建增强版** - 不要创建 `xxx_enhanced.py`、`xxx_new.py`、`xxx_fixed.py`

### 2. 正确的操作流程

```python
# ✅ 正确流程
1. filesystem:read_file -> 查看文件是否存在
2. filesystem:edit_file -> 修改现有文件
3. 只在文件不存在时使用 write_file
4. 修改代码后立即更新相关文档

# ❌ 错误流程
1. 直接 write_file 创建新文件
2. 创建 xxx_enhanced.py 而不是修改原文件
3. 修改代码但不更新文档
```

### 3. 文档同步铁律
- **修改即更新** - 修改代码后必须立即更新相关文档
- **验证引用** - 确保文档中引用的文件/命令真实存在
- **删除即清理** - 删除文件后必须清理所有文档引用
- **命令要准确** - 文档中的命令必须实际可运行

## 🗂️ 项目结构规则

### 文件应该放在哪里？

```
RuleK/
├── src/                # ✅ 游戏核心代码
│   ├── core/          # 核心逻辑
│   ├── ai/            # AI相关
│   ├── api/           # API接口
│   └── utils/         # 工具函数
│
├── web/               # ✅ Web相关
│   ├── backend/       # 后端代码
│   └── frontend/      # 前端代码
│
├── scripts/           # ✅ 脚本工具
│   ├── test/         # 测试脚本
│   ├── fix/          # 修复脚本
│   └── dev/          # 开发工具
│
├── tests/            # ✅ 测试文件
├── docs/             # ✅ 文档
└── ❌ 根目录不要放代码文件！
```

### 文件命名规则

```python
# ✅ 正确命名
- game_service.py      # 下划线分隔
- test_websocket.py    # 测试文件前缀test_
- fix_imports.py       # 修复脚本前缀fix_

# ❌ 错误命名
- gameService.py       # 不要用驼峰
- websocket-test.py    # 不要用连字符
- service_enhanced.py  # 不要加enhanced
- service_new.py       # 不要加new
- service_v2.py        # 不要加版本号
```

## 🔧 具体操作指南

### 1. 当需要修复bug时

```python
# ✅ 正确做法
1. 先读取原文件
   filesystem:read_file path="web/backend/app.py"
   
2. 使用edit_file修改
   filesystem:edit_file 
     path="web/backend/app.py"
     edits=[{"oldText": "buggy code", "newText": "fixed code"}]

# ❌ 错误做法
- 创建 app_fixed.py
- 创建 app_enhanced.py
- 直接覆盖整个文件
```

### 2. 当需要添加新功能时

```python
# ✅ 正确做法
1. 检查相关文件是否存在
   filesystem:list_directory path="web/backend/services"
   
2. 如果文件存在，修改它
   filesystem:edit_file path="existing_file.py"
   
3. 只有文件不存在时才创建
   filesystem:write_file path="web/backend/services/new_service.py"

# ❌ 错误做法
- 在根目录创建 new_feature.py
- 创建 service_with_new_feature.py
```

### 3. 当需要重构代码时

```python
# ✅ 正确做法
1. 备份原文件（如果需要）
   filesystem:read_file -> 保存内容到 .backups/
   
2. 直接修改原文件
   filesystem:edit_file -> 逐步修改

# ❌ 错误做法
- 创建 refactored_xxx.py
- 创建 xxx_new_structure.py
```

## 📊 检查清单

在执行任何操作前，AI必须回答：

- [ ] 我要操作的文件是否已存在？
- [ ] 我能用 edit_file 代替 write_file 吗？
- [ ] 文件路径是否正确（不在根目录）？
- [ ] 文件名是否符合规范（没有enhanced/new/fixed后缀）？
- [ ] 是否真的需要创建新文件？
- [ ] 修改后是否需要更新相关文档？
- [ ] 文档中的命令是否实际可运行？

## 🚨 禁止操作列表

1. **禁止在根目录创建**：
   - `fix_xxx.py`
   - `test_xxx.py`
   - `quick_xxx.py`
   - `temp_xxx.py`

2. **禁止创建这些后缀的文件**：
   - `*_enhanced.py`
   - `*_new.py`
   - `*_fixed.py`
   - `*_v2.py`
   - `*_updated.py`
   - `*_modified.py`

3. **禁止重复创建**：
   - 如果 `app.py` 存在，不要创建 `app2.py`
   - 如果 `service.py` 存在，不要创建 `service_new.py`

## 🎯 子Agent调用规则

当遇到特定任务时，调用对应的子Agent：

```yaml
任务分发:
  文档相关: -> 读取 docs/.DOCS_AGENT.md
  测试相关: -> 读取 tests/.TEST_AGENT.md
  前端相关: -> 读取 web/frontend/.FRONTEND_AGENT.md
  后端相关: -> 读取 web/backend/.BACKEND_AGENT.md
  脚本相关: -> 读取 scripts/.SCRIPTS_AGENT.md
  源码相关: -> 读取 src/.SRC_AGENT.md
```

## 💡 智能提示

### 文件已存在时的处理
```python
if file_exists:
    # 1. 先读取
    content = read_file(path)
    
    # 2. 分析需要改什么
    changes = analyze_changes(content)
    
    # 3. 使用edit_file精确修改
    edit_file(path, changes)
else:
    # 只有不存在时才创建
    write_file(path, content)
```

### 永远记住
> "缝缝补补"比"推倒重来"更好！
> 修改现有文件比创建新文件更好！
> 保持项目整洁比快速完成更重要！

---

## ⚡ 快速决策树

```
需要改代码？
├─ 文件存在吗？
│  ├─ 是 -> 用 edit_file 修改
│  └─ 否 -> 检查是否真的需要创建
│           └─ 确实需要 -> 在正确目录创建
└─ 文件在哪？
   ├─ 核心代码 -> src/
   ├─ Web相关 -> web/
   ├─ 测试 -> tests/
   ├─ 脚本 -> scripts/
   └─ 文档 -> docs/
```

---

*最后更新: 2024-12-22*
*版本: 1.1.0*
*强制执行: 是*