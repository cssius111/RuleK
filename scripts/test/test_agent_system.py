#!/usr/bin/env python3
"""
Agent系统快速测试
验证所有Agent文件是否正确配置
"""

import os
from pathlib import Path

def test_agent_system():
    """测试Agent系统是否完整"""
    project_root = Path.cwd()
    
    # 需要检查的Agent文件
    agent_files = {
        'MAIN_AGENT.md': '主Agent',
        'docs/.DOCS_AGENT.md': '文档Agent',
        'scripts/.SCRIPTS_AGENT.md': '脚本Agent',
        'web/backend/.BACKEND_AGENT.md': '后端Agent',
        'web/frontend/.FRONTEND_AGENT.md': '前端Agent',
        'tests/.TEST_AGENT.md': '测试Agent',
        'src/.SRC_AGENT.md': '源码Agent',
    }
    
    print("🔍 检查Agent系统配置...")
    print("=" * 50)
    
    all_ok = True
    for file_path, name in agent_files.items():
        full_path = project_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {name:15} -> {file_path} ({size} bytes)")
        else:
            print(f"❌ {name:15} -> {file_path} (缺失)")
            all_ok = False
    
    print("=" * 50)
    
    if all_ok:
        print("✅ Agent系统配置完整！")
        print("\n📝 使用提示：")
        print("1. 让AI先读取 MAIN_AGENT.md")
        print("2. 根据任务类型读取对应的子Agent")
        print("3. 使用 agent_validator.py 验证操作")
    else:
        print("❌ Agent系统配置不完整，请检查缺失的文件")
    
    return all_ok


def show_usage_example():
    """显示使用示例"""
    print("\n📖 使用示例：")
    print("-" * 50)
    print("""
# 1. 验证文件操作
python scripts/agent_validator.py --check create --path /test.py

# 2. 生成Agent上下文
python scripts/agent_validator.py --context backend

# 3. 让AI遵循规则
"请先读取MAIN_AGENT.md，然后帮我修改web/backend/app.py"
    """)


if __name__ == "__main__":
    if test_agent_system():
        show_usage_example()
