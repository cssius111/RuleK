#!/usr/bin/env python3
"""
RuleK 项目管理工具
"""
import subprocess
import sys
import os

def show_menu():
    print("""
╔══════════════════════════════════════════════════╗
║           RuleK 项目管理工具                    ║
╚══════════════════════════════════════════════════╝

请选择操作：

1. 🔍 查看项目状态（推荐先执行）
2. 🧹 清理项目（移除临时文件）
3. 🚀 启动服务器
4. 📖 查看清理指南
5. ❌ 退出

""")

def main():
    while True:
        show_menu()
        choice = input("请输入选择 (1-5): ").strip()
        
        if choice == '1':
            print("\n" + "="*50)
            subprocess.run([sys.executable, "tools/status.py"])
            print("="*50)
            input("\n按回车继续...")
            
        elif choice == '2':
            print("\n" + "="*50)
            subprocess.run([sys.executable, "tools/cleanup.py"])
            print("="*50)
            input("\n按回车继续...")
            
        elif choice == '3':
            print("\n启动服务器...")
            subprocess.run([sys.executable, "start_web_server.py"])
            break
            
        elif choice == '4':
            # 如果文件存在，显示内容
            guide_path = "docs/cleanup_guide.md"
            if not os.path.exists(guide_path):
                guide_path = "docs/CLEANUP_GUIDE.md"
            
            if os.path.exists(guide_path):
                with open(guide_path, 'r', encoding='utf-8') as f:
                    print("\n" + "="*50)
                    print(f.read())
                    print("="*50)
            else:
                print("\n清理指南文件不存在")
            input("\n按回车继续...")
            
        elif choice == '5':
            print("\n👋 再见！")
            break
            
        else:
            print("\n❌ 无效选择，请重试")
            input("按回车继续...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
