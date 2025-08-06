# 🎯 重新组织项目结构

你说得对！根目录太乱了。我创建了一个重组工具来解决这个问题。

## 当前问题

根目录有太多文件（约15-20个），应该分类放到合适的目录中。

## 解决方案

### 运行重组工具

```bash
python restructure_project.py
```

这会自动：

### 1️⃣ 创建清晰的目录结构

```
RuleK/
├── tools/              # 管理工具（原来在根目录）
│   ├── manage.py      
│   ├── cleanup.py     
│   ├── status.py      
│   └── quick_clean.py 
│
├── docs/               # 所有文档（原来散在根目录）
│   ├── cleanup_guide.md
│   ├── contributing.md
│   ├── quick_start.md
│   └── ...
│
├── deploy/             # 部署文件（原来在根目录）
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── src/                # ✅ 保持不变
├── web/                # ✅ 保持不变
├── tests/              # ✅ 保持不变
├── config/             # ✅ 保持不变
├── data/               # ✅ 保持不变
├── logs/               # ✅ 保持不变
├── scripts/            # ✅ 保持不变
```

### 2️⃣ 根目录只保留核心文件

重组后，根目录只有这些文件：
```
rulek.py               # 统一入口
start_web_server.py    # Web启动脚本
start.sh / start.bat   # 快捷启动
requirements.txt       # Python依赖
README.md             # 项目说明
LICENSE               # 许可证
.env / .env.example   # 环境配置
.gitignore            # Git配置
pyproject.toml        # 项目配置
```

### 3️⃣ 自动更新所有引用

工具会自动更新所有文件中的引用路径，例如：
- `python project_status.py` → `python tools/status.py`
- `CLEANUP_GUIDE.md` → `docs/cleanup_guide.md`
- 等等...

## 文件迁移计划

| 原位置 | 新位置 | 类型 |
|--------|--------|------|
| manage.py | tools/manage.py | 管理工具 |
| cleanup_project.py | tools/cleanup.py | 管理工具 |
| project_status.py | tools/status.py | 管理工具 |
| clean.py | tools/quick_clean.py | 管理工具 |
| CLEANUP_GUIDE.md | docs/cleanup_guide.md | 文档 |
| CLEANUP_COMPLETE.md | docs/cleanup_complete.md | 文档 |
| START.md | docs/quick_start.md | 文档 |
| AGENTS.md | docs/agents.md | 文档 |
| CONTRIBUTING.md | docs/contributing.md | 文档 |
| Dockerfile | deploy/Dockerfile | 部署 |
| docker-compose.yml | deploy/docker-compose.yml | 部署 |
| nginx.conf | deploy/nginx.conf | 部署 |

## 使用方式更新

### 重组前：
```bash
python manage.py            # 根目录的管理工具
python cleanup_project.py   # 根目录的清理脚本
python project_status.py    # 根目录的状态检查
```

### 重组后：
```bash
python rulek.py manage      # 统一入口访问管理工具
python tools/manage.py      # 或直接访问
python tools/cleanup.py     # 直接访问清理脚本
python tools/status.py      # 直接访问状态检查
```

## 优势

### 重组前的根目录：
- 😵 15-20个散乱的文件
- 😵 管理工具、文档、配置混在一起
- 😵 难以区分核心文件和辅助文件
- 😵 不专业，看起来混乱

### 重组后的根目录：
- ✅ 只有8-10个核心文件
- ✅ 清晰的目录分类
- ✅ 一目了然的项目结构
- ✅ 专业规范的组织方式

## 安全性

- 所有文件移动前都会备份到 `.backups/` 目录
- 不会删除任何核心代码
- 可以随时从备份恢复

## 立即执行

### 步骤1：运行重组工具
```bash
python restructure_project.py
```

### 步骤2：确认重组
输入 `y` 确认

### 步骤3：完成！
重组完成后，你可以：
```bash
python rulek.py         # 查看新的帮助
python rulek.py web     # 启动服务器
python rulek.py manage  # 打开管理菜单
```

## 重组 + 清理 = 完美项目

1. **先重组结构**:
   ```bash
   python restructure_project.py
   ```

2. **再清理临时文件**:
   ```bash
   python rulek.py manage
   # 选择清理选项
   ```

3. **享受干净的项目**！

---

**立即运行 `python restructure_project.py` 让你的项目结构焕然一新！** 🚀

重组后，根目录会非常清爽，所有文件都在合适的位置，而且所有引用都会自动更新。
