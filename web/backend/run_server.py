#!/usr/bin/env python
"""
启动 FastAPI 后端服务器
"""
import uvicorn
import sys
from pathlib import Path
import socket

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    # 尝试绑定端口，若被占用则依次递增寻找可用端口
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
                break
            except OSError:
                print(f"端口 {port} 已被占用，尝试使用 {port + 1}...")
                port += 1

    print(f"使用端口 {port} 启动服务器")

    uvicorn.run(
        "web.backend.app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
