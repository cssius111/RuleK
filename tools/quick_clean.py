#!/usr/bin/env python3
"""
快速清理项目
"""
import subprocess
import sys

print("""
════════════════════════════════════════════════════
           准备清理 RuleK 项目
════════════════════════════════════════════════════

这将移除：
  • 所有临时修复脚本
  • 测试文件
  • 过时文档
  • Python缓存
  
保留：
  • 核心代码 (src/, web/)
  • 配置文件
  • 主要启动脚本
  
""")

response = input("确定要清理吗？(y/n): ")
if response.lower() == 'y':
    subprocess.run([sys.executable, "cleanup_project.py"])
else:
    print("取消清理")
