# 📋 RuleK 渐进式重构计划

基于**MAIN_AGENT规则**，采用"缝缝补补"策略，不推倒重来。

## 🎯 重构目标

1. **清理根目录** - 只保留必要文件
2. **整理脚本** - 所有脚本归类到 `scripts/`
3. **删除空目录** - 清理无用目录
4. **保持稳定** - 不破坏现有功能

## 📊 当前状态

### 需要整理的文件
- `manage.py` → `scripts/manage.py`
- `start_web_server.py` → `scripts/startup/start_web_server.py`

### 需要删除的空目录
- `rulek/` - 空目录
- `.agents/` - 未知用途的空目录
- `test-results/` - 测试结果目录（如果为空）

### 保留的核心文件（根目录）
- ✅ `rulek.py` - 统一入口
- ✅ `Makefile` - 任务管理
- ✅ `requirements.txt` - 依赖管理
- ✅ `README.md` - 项目说明
- ✅ `MAIN_AGENT.md` - Agent规则
- ✅ `PROJECT_PLAN.md` - 项目计划
- ✅ 配置文件（.env, .gitignore等）

## 🛠️ 执行步骤

### 步骤1：预览模式测试
```bash
python scripts/smart_restructure.py
```

### 步骤2：执行重构
```bash
python scripts/smart_restructure.py --execute
```

### 步骤3：验证结果
```bash
# 检查文件是否正确移动
ls scripts/
ls -la

# 测试功能是否正常
make test
```

## ⚠️ 注意事项

1. **备份优先** - 所有操作前先备份到 `.backups/`
2. **渐进执行** - 分步骤进行，每步验证
3. **保持兼容** - 不破坏现有功能
4. **遵循规则** - 严格遵守MAIN_AGENT规则

## 📈 预期结果

### Before（重构前）
```
RuleK/
├── manage.py            # ❌ 根目录
├── start_web_server.py  # ❌ 根目录
├── rulek/               # ❌ 空目录
├── .agents/             # ❌ 空目录
└── 混乱的根目录...
```

### After（重构后）
```
RuleK/
├── scripts/
│   ├── manage.py              # ✅ 正确位置
│   └── startup/
│       └── start_web_server.py # ✅ 正确位置
├── rulek.py            # ✅ 保留
├── Makefile            # ✅ 保留
└── 整洁的根目录
```

## 🚀 后续优化

1. **导入路径更新** - 修复移动文件后的导入问题
2. **文档整理** - 继续整理docs目录
3. **测试完善** - 确保所有测试通过
4. **CI/CD配置** - 更新自动化脚本路径

## 📝 变更记录

- 2024-12-22: 创建渐进式重构计划
- 遵循MAIN_AGENT规则
- 优先修改而不是创建新文件

---

**核心理念：缝缝补补，稳步前进！**