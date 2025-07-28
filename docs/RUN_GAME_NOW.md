# 🎮 运行游戏 - 立即开始！

## 最简单的方法

在项目根目录运行：

```bash
python play.py
```

就这么简单！

## 其他选项

```bash
# 方式2：专用CLI启动器
python play_cli.py

# 方式3：统一入口
python rulek.py cli

# 方式4：启动Web版
python play.py web
```

## 如果遇到问题

出现 "ModuleNotFoundError: No module named 'src'" 错误？

**不要**直接运行 `python src/cli_game.py` ❌

**请用**上面的方法之一 ✅

## 验证是否修复成功

```bash
python test_fixes.py
```

应该看到：
- ✅ AI生成了 2 条对话, 1 个行动
- ✅ 自定义规则创建器已加载
- ✅ CLI游戏已集成自定义规则创建

## 快速游戏流程

1. 运行 `python play.py`
2. 选择 **1** 新游戏
3. 选择是否启用AI（y/n）
4. 在准备阶段：
   - 选择 **1** 创建规则
   - 尝试三种创建方式
   - 选择 **4** 开始回合
5. 享受游戏！

---

有问题？查看 QUICK_START_FIXED.md 获取更多帮助！
