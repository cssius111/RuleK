# 测试问题修复说明

## 🔧 已修复的问题

### 1. **异步测试被跳过**
- **问题**: `async def` 测试函数被跳过，提示需要安装异步插件
- **解决**: 
  - 已在 `requirements.txt` 中包含 `pytest-asyncio==0.21.1`
  - 已在 `pyproject.toml` 中配置 `asyncio_mode = "auto"`
  - 所有异步测试已添加 `@pytest.mark.asyncio` 装饰器

### 2. **测试返回值警告**
- **问题**: 测试函数返回了值，pytest 期望不返回任何值
- **解决**: 已移除所有测试函数中的 `return True` 语句

### 3. **Pydantic 弃用警告**
- **问题**: 使用了 Pydantic v1 的语法
- **解决**: 
  - 将 `@validator` 改为 `@field_validator`
  - 将 `class Config` 改为 `model_config = ConfigDict()`

### 4. **项目文件组织**
- **问题**: 测试文件和配置分散
- **解决**: 已创建清晰的项目结构和维护脚本

## 🚀 如何运行测试

### 方法1: 使用快速测试脚本（推荐）
```bash
python scripts/test_quick.py
```

### 方法2: 使用测试运行器
```bash
python scripts/run_tests.py
# 然后选择要运行的测试类型
```

### 方法3: 直接使用 pytest
```bash
# 运行所有测试
pytest tests/ -v

# 只运行单元测试
pytest tests/unit/ -v

# 运行特定测试文件
pytest tests/unit/test_game.py -v

# 运行带覆盖率的测试
pytest tests/ --cov=src --cov-report=term-missing
```

## 📋 环境要求

1. **Python 版本**: 3.8+
2. **必要依赖**:
   ```bash
   pip install -r requirements.txt
   ```

3. **环境变量配置**:
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，添加你的 DEEPSEEK_API_KEY
   ```

## ⚠️ 已知警告（不影响功能）

1. **Pydantic ConfigDict 警告**: 这是 Pydantic v2 迁移的一部分，不影响功能
2. **JSON encoders 警告**: 已知的弃用警告，功能正常

## 🧹 项目维护

运行项目清理和健康检查：
```bash
python scripts/cleanup_project.py
```

## 📊 测试覆盖率

查看测试覆盖率报告：
```bash
pytest tests/ --cov=src --cov-report=html
# 然后打开 htmlcov/index.html
```

## 🐛 问题排查

如果测试仍然失败：

1. **确保在项目根目录运行测试**
2. **检查 Python 路径**:
   ```python
   import sys
   print(sys.path)
   ```
3. **验证异步支持**:
   ```bash
   python -m pytest --version
   pip show pytest-asyncio
   ```
4. **清理缓存**:
   ```bash
   python scripts/cleanup_project.py
   # 选择 1 清理缓存
   ```

## ✅ 下一步

1. 所有测试应该能正常运行
2. 可以开始开发新功能
3. 记得为新功能添加测试
4. 使用 Mock 模式可以不依赖 API 进行测试
