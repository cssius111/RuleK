# 工具脚本目录

本目录包含项目维护和管理的工具脚本。

## 脚本列表

### restructure.py
项目重构自动化脚本，用于整理项目文件结构。

使用方法：
```bash
# 预览模式
python restructure.py --dry-run

# 执行重构
python restructure.py

# 仅清理
python restructure.py --clean-only
```

### 其他工具脚本
- cleanup.sh - 清理缓存和临时文件
- make_executable.sh - 批量设置脚本可执行权限

## 添加新工具

在此目录创建新的工具脚本时，请遵循：
1. 使用描述性的文件名
2. 添加文件头注释说明用途
3. 提供 `--help` 选项
4. 更新此 README

## 注意事项

这些脚本应该从项目根目录运行，例如：
```bash
python scripts/utils/restructure.py
```
