"""运行测试套件"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)


def main() -> None:
    """使用pytest运行测试套件"""
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-v",
                "--tb=short",
                "--ignore=tests/web",
                "--ignore=tests/manual",
            ],
            check=True,
            env=env,
            cwd=PROJECT_ROOT,
        )
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
    except FileNotFoundError:
        print("❌ pytest未安装")
        print("   请运行: pip install pytest")
        sys.exit(1)


if __name__ == "__main__":
    main()
