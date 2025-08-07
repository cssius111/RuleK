#!/usr/bin/env python
"""检查 FastAPI 配置和版本"""

import sys
import importlib

print("=" * 50)
print("检查 FastAPI 配置")
print("=" * 50)

# 检查 FastAPI 版本
try:
    import fastapi
    print(f"✅ FastAPI 版本: {fastapi.__version__}")
except ImportError:
    print("❌ FastAPI 未安装")
    sys.exit(1)

# 尝试导入并检查应用配置
try:
    sys.path.insert(0, '/Users/chenpinle/Desktop/杂/pythonProject/RuleK')
    from web.backend.app import app
    
    print(f"\n应用信息:")
    print(f"  标题: {app.title}")
    print(f"  版本: {app.version}")
    print(f"  文档URL: {app.docs_url if hasattr(app, 'docs_url') else '/docs (默认)'}")
    print(f"  Redoc URL: {app.redoc_url if hasattr(app, 'redoc_url') else '/redoc (默认)'}")
    print(f"  OpenAPI URL: {app.openapi_url if hasattr(app, 'openapi_url') else '/openapi.json (默认)'}")
    
    print(f"\n路由列表:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  - {route.methods if hasattr(route, 'methods') else 'WS'}: {route.path}")
    
except Exception as e:
    print(f"❌ 无法导入应用: {e}")

print("\n" + "=" * 50)
print("如果 /docs 不在路由列表中，可能需要:")
print("1. 确保没有设置 docs_url=None")
print("2. 检查 FastAPI 版本是否正确")
print("3. 重启服务器")
