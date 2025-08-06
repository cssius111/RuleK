#!/usr/bin/env python3
"""
RuleK Web服务器启动脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """启动Web服务器"""
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
    
    try:
        import uvicorn
        uvicorn.run(
            "web.backend.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ 错误: 缺少依赖包")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n✅ 服务器已正常关闭")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        print("\n可能的原因:")
        print("1. 端口8000被占用")
        print("2. Python版本低于3.8")
        print("3. 文件权限问题")
        sys.exit(1)

if __name__ == "__main__":
    main()
