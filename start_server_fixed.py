#!/usr/bin/env python
"""
修复版 Web 服务器启动脚本
确保 FastAPI 文档正确启用
"""

import sys
from pathlib import Path
import uvicorn

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("\n" + "=" * 54)
    print("║           RuleK Web服务器 (文档修复版)          ║")
    print("=" * 54)
    print("""
🚀 正在启动服务器...
   主页: http://localhost:8000
   API文档: http://localhost:8000/docs
   Redoc文档: http://localhost:8000/redoc
   OpenAPI规范: http://localhost:8000/openapi.json
   
   按 Ctrl+C 停止服务器
--------------------------------------------------
    """)
    
    # 使用正确的模块路径启动
    uvicorn.run(
        "web.backend.app:app",  # 完整的模块路径
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
