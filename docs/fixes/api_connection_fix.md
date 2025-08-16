# 🔥 API连接问题解决方案

## 问题诊断

**根本原因**：缺少必要的Python包，导致`.env`文件中的API密钥无法被读取。

### 缺失的包：
1. **python-dotenv** - 用于读取.env文件
2. **tenacity** - 用于API重试机制

## ✅ 解决方案

### 方法1：安装缺失的依赖（推荐）

```bash
# 安装所有依赖
pip install -r requirements.txt

# 或单独安装缺失的包
pip install python-dotenv tenacity httpx
```

### 方法2：手动设置环境变量（临时方案）

```bash
# 在终端中设置（临时）
export DEEPSEEK_API_KEY=sk-dde32e8013274727a623a4e570be6916

# 然后运行测试
pytest tests/api/ -v
```

### 方法3：在测试文件中直接设置（仅用于测试）

```python
import os
os.environ['DEEPSEEK_API_KEY'] = 'sk-dde32e8013274727a623a4e570be6916'
```

## 📝 完整修复步骤

1. **安装依赖**
```bash
pip install python-dotenv==1.0.0 tenacity==9.1.2 httpx==0.25.2
```

2. **验证安装**
```bash
python scripts/test/diagnose_api_key.py
```

3. **运行测试**
```bash
pytest tests/api/test_deepseek_api.py -v
```

## 🔍 验证API密钥是否加载

运行诊断脚本：
```bash
python scripts/test/diagnose_api_key.py
```

应该看到：
```
✅ python-dotenv已安装
✅ .env文件存在
✅ 环境变量已设置
✅ Config加载成功
✅ 客户端使用真实API密钥
```

## ⚠️ 注意事项

1. **requirements.txt已更新** - 包含了python-dotenv
2. **.env文件格式** - 确保没有引号包围密钥值
3. **密钥安全** - 不要将真实密钥提交到Git

## 📊 预期结果

安装依赖后：
- API测试应该能正常连接
- Mock模式只在没有密钥时启用
- 测试通过率应该进一步提升

---

*更新时间：2024-12-22*
