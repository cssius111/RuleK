#!/usr/bin/env python3
"""直接启动后端服务器"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 切换到后端目录
os.chdir(os.path.join(project_root, 'web', 'backend'))

# 导入并运行app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
