"""启动前端开发服务器"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = PROJECT_ROOT / "web" / "frontend"


def main() -> Optional[int]:
    """启动前端开发服务器"""
    if not FRONTEND_DIR.exists():
        print("❌ 前端目录不存在")
        return None

    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("📦 安装前端依赖...")
        try:
            subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, check=True)
        except subprocess.CalledProcessError:
            print("❌ 前端依赖安装失败")
            return None

    try:
        subprocess.run(["npm", "run", "dev"], cwd=FRONTEND_DIR, check=True)
    except subprocess.CalledProcessError:
        print("❌ 前端启动失败")
        return None
    return 0


if __name__ == "__main__":
    main()
