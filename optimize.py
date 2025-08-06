#!/usr/bin/env python3
"""
一键优化项目结构
"""
import subprocess
import sys
import os

def main():
    print("""
╔══════════════════════════════════════════════════╗
║         RuleK 项目优化工具                      ║
║         让你的项目结构焕然一新                  ║
╚══════════════════════════════════════════════════╝
    """)
    
    print("这个工具会帮你：")
    print("  1️⃣  重组项目结构（文件归类到合适目录）")
    print("  2️⃣  清理临时文件（删除修复脚本等）")
    print("  3️⃣  优化根目录（只保留核心文件）")
    
    print("\n" + "="*50)
    print("🎯 第一步：重组项目结构")
    print("="*50)
    print("将会：")
    print("  • 管理工具 → tools/ 目录")
    print("  • 文档文件 → docs/ 目录")
    print("  • 部署文件 → deploy/ 目录")
    
    response = input("\n开始重组吗？(y/n): ")
    if response.lower() == 'y':
        print("\n执行重组...")
        result = subprocess.run([sys.executable, "restructure_project.py"], input="y\n", text=True)
        
        if result.returncode == 0:
            print("\n✅ 重组完成！")
            
            print("\n" + "="*50)
            print("🎯 第二步：清理临时文件")
            print("="*50)
            
            # 检查 cleanup 脚本是否已经移动
            if os.path.exists("tools/cleanup.py"):
                cleanup_script = "tools/cleanup.py"
            elif os.path.exists("cleanup_project.py"):
                cleanup_script = "cleanup_project.py"
            else:
                print("⚠️  清理脚本未找到")
                return
            
            response2 = input("\n要清理临时文件吗？(y/n): ")
            if response2.lower() == 'y':
                print("\n执行清理...")
                subprocess.run([sys.executable, cleanup_script], input="y\n", text=True)
                print("\n✅ 清理完成！")
            
            print("\n" + "="*60)
            print("🎉 项目优化完成！")
            print("="*60)
            print("\n现在你的项目：")
            print("  ✅ 结构清晰")
            print("  ✅ 根目录整洁")
            print("  ✅ 文件归类合理")
            print("  ✅ 没有临时文件")
            
            print("\n🚀 使用方式：")
            print("  python rulek.py         # 查看帮助")
            print("  python rulek.py web     # 启动服务器")
            print("  python rulek.py manage  # 管理工具")
        else:
            print("\n❌ 重组失败，请检查错误信息")
    else:
        print("\n取消优化")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 操作被中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
