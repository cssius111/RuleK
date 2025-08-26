"""自动修复常见问题"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    """运行修复脚本或执行基本修复"""
    fix_script = PROJECT_ROOT / "scripts" / "fix" / "final_fix_and_test.sh"
    if fix_script.exists():
        subprocess.run(["bash", str(fix_script)], check=False)
        return

    print("修复脚本不存在，尝试基本修复...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    frontend_dir = PROJECT_ROOT / "web" / "frontend"
    if frontend_dir.exists():
        subprocess.run(["npm", "install"], cwd=frontend_dir)
    print("✅ 基本修复完成")


if __name__ == "__main__":
    main()
