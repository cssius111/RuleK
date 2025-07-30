#!/usr/bin/env python3
"""
快速启动Web服务器
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 正在启动RuleK Web API服务器...")
    print("📖 访问 http://localhost:8000/docs 查看API文档")
    print("🛑 按 Ctrl+C 停止服务器\n")
    
    try:
        uvicorn.run(
            "web.backend.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n✅ 服务器已停止")
