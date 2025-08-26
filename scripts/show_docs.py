"""显示项目文档摘要"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> None:
    """打印关键文档的前几行"""
    docs = [
        ("README.md", "项目说明"),
        ("PROJECT_PLAN.md", "项目计划"),
        ("MAIN_AGENT.md", "开发规范"),
        ("PROJECT_STRUCTURE.md", "项目结构"),
    ]
    for filename, desc in docs:
        doc_path = PROJECT_ROOT / filename
        if doc_path.exists():
            print(f"\n{desc} ({filename}):")
            lines = doc_path.read_text(encoding="utf-8").splitlines()[:10]
            for line in lines:
                print(f"  {line}")
            print(f"  ...（查看完整文档: cat {filename}）")


if __name__ == "__main__":
    main()
