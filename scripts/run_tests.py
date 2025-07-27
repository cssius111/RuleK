#!/usr/bin/env python3
"""
测试运行器脚本
用于运行所有测试或特定测试
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd):
    """运行命令并显示输出"""
    print(f"运行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode

def main():
    """主函数"""
    print("🧪 规则怪谈管理者 - 测试运行器")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # 测试选项
    print("\n选择要运行的测试:")
    print("1. 运行所有单元测试")
    print("2. 运行集成测试")
    print("3. 运行Sprint 2功能测试")
    print("4. 运行API测试（需要配置.env）")
    print("5. 运行覆盖率测试")
    print("0. 退出")
    
    choice = input("\n请选择 (0-5): ")
    
    if choice == "0":
        return
    
    # 根据选择运行测试
    if choice == "1":
        print("\n运行单元测试...")
        return_code = run_command([sys.executable, "-m", "pytest", "tests/unit/", "-v"])
    
    elif choice == "2":
        print("\n运行集成测试...")
        return_code = run_command([sys.executable, "-m", "pytest", "tests/integration/", "-v"])
    
    elif choice == "3":
        print("\n运行Sprint 2功能测试...")
        return_code = run_command([sys.executable, "tests/unit/test_sprint2.py"])
    
    elif choice == "4":
        print("\n运行API测试...")
        # 检查是否有.env文件
        env_file = project_root / ".env"
        if not env_file.exists():
            print("⚠️  警告: 未找到.env文件，使用Mock模式")
            print("   要使用真实API，请复制.env.example为.env并填入API密钥")
        return_code = run_command([sys.executable, "-m", "pytest", "tests/unit/test_sprint2.py::test_api_client", "-v"])
    
    elif choice == "5":
        print("\n运行覆盖率测试...")
        # 先安装coverage
        print("确保已安装coverage: pip install coverage")
        return_code = run_command([sys.executable, "-m", "coverage", "run", "-m", "pytest", "tests/"])
        if return_code == 0:
            run_command([sys.executable, "-m", "coverage", "report"])
            run_command([sys.executable, "-m", "coverage", "html"])
            print("\n✅ 覆盖率报告已生成: htmlcov/index.html")
    
    else:
        print("无效选择")
        return
    
    if return_code == 0:
        print("\n✅ 测试通过!")
    else:
        print("\n❌ 测试失败!")

if __name__ == "__main__":
    main()
