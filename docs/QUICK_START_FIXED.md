# 🎮 RuleK 快速启动指南

## 推荐启动方式（修复路径问题）

### 方式1：使用启动器（推荐✨）
```bash
# 运行CLI游戏
python play.py

# 或指定模式
python play.py cli    # CLI游戏
python play.py web    # Web服务器
python play.py test   # 运行测试
```

### 方式2：专用CLI启动器
```bash
python play_cli.py
```

### 方式3：使用统一入口
```bash
python rulek.py cli
```

### ❌ 不要直接运行
```bash
# 这会导致模块导入错误
python src/cli_game.py  # ❌ 不推荐
```

## 问题解决

### 如果遇到 "ModuleNotFoundError: No module named 'src'"
使用上面推荐的启动方式之一，它们会自动设置正确的Python路径。

### 验证修复是否成功
```bash
python test_fixes.py
```

预期输出：
- ✅ AI生成了 X 条对话, Y 个行动
- ✅ 自定义规则创建器已加载
- ✅ CLI游戏已集成自定义规则创建

## 游戏快速指南

### 1. 启动游戏
```bash
python play.py
```

### 2. 主菜单选项
- **1** - 新游戏
- **2** - 加载存档
- **3** - 退出

### 3. 创建规则
准备阶段选择 "1. 创建/管理规则"，然后：
- **1** - 自定义创建（交互式向导）
- **2** - 模板创建（预定义规则）
- **3** - AI解析（自然语言）

### 4. 游戏循环
1. **准备阶段** - 创建规则、查看状态
2. **行动阶段** - NPC自动行动
3. **结算阶段** - 查看结果、获得积分

## 文件说明

- `play.py` - 万能启动器
- `play_cli.py` - CLI专用启动器
- `rulek.py` - 项目统一入口
- `src/custom_rule_creator.py` - 自定义规则创建器
- `src/cli_game.py` - CLI游戏主程序

## 注意事项

- 总是从项目根目录运行命令
- 使用推荐的启动器避免路径问题
- AI功能需要有效的API密钥（可选）

---

现在开始你的恐怖规则之旅吧！🎭
