#!/usr/bin/env python3
"""
RuleK Web服务器快速启动
用于快速启动Web服务器的简单脚本
"""
import uvicorn

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║           RuleK Web服务器                       ║
╚══════════════════════════════════════════════════╝
    
🚀 正在启动服务器...
   地址: http://localhost:8000
   文档: http://localhost:8000/docs
   
   按 Ctrl+C 停止服务器
--------------------------------------------------
    """)
    
    uvicorn.run(
        "web.backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
