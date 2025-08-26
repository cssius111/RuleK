# 🚀 RuleK 快速启动指南

## Web服务器启动方式

### 方式1：使用Makefile（推荐）
```bash
make serve
```

### 方式2：使用快速启动脚本
```bash
# 在项目根目录运行
python scripts/startup/quick_serve.py
```

### 方式3：直接使用uvicorn
```bash
# 在项目根目录
uvicorn web.backend.app:app --reload --host 0.0.0.0 --port 8000
```

### 方式4：使用rulek.py
```bash
python rulek.py web
```
> `rulek.py` 仅负责参数解析和调度，实际启动逻辑在 `scripts/` 模块中实现。

## 如果启动失败

### 检查清单
1. ✅ 确认在项目根目录
2. ✅ 安装了所有依赖：`pip install -r requirements.txt`
3. ✅ Python版本 >= 3.10
4. ✅ 端口8000未被占用

### 常见问题

#### 问题：ModuleNotFoundError: No module named 'web'
**解决**：确保在项目根目录运行命令

#### 问题：ImportError: cannot import name 'app'
**解决**：检查 `web/backend/app.py` 文件是否存在

#### 问题：[Errno 48] Address already in use
**解决**：端口被占用，关闭其他使用8000端口的程序

## 测试服务器

启动后访问：
- 主页：http://localhost:8000
- API文档：http://localhost:8000/docs
- 交互式API：http://localhost:8000/redoc

## CLI游戏启动

```bash
make cli
# 或
python rulek.py cli
```

---
*更新时间：2024-12-22*