#!/usr/bin/env python3
"""
RuleK 一键诊断和修复工具
自动检测并修复常见问题
"""

import sys
import os
import subprocess
import time
import json
import httpx
import asyncio
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class RuleKDiagnostic:
    """RuleK 诊断工具"""
    
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.server_url = "http://localhost:8000"
        
    def print_header(self):
        """打印标题"""
        print("=" * 70)
        print("🔧 RuleK 一键诊断和修复工具")
        print("=" * 70)
        print()
    
    def check_python_version(self) -> bool:
        """检查Python版本"""
        print("🔍 检查Python版本...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            self.issues.append(f"Python版本过低: {version.major}.{version.minor}")
            print(f"   ❌ 需要Python 3.10+，当前: {version.major}.{version.minor}")
            return False
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_dependencies(self) -> bool:
        """检查依赖包"""
        print("🔍 检查依赖包...")
        required = {
            'fastapi': '0.104.1',
            'uvicorn': '0.24.0',
            'httpx': '0.25.2',
            'pydantic': '2.5.0',
            'websockets': '12.0'
        }
        
        missing = []
        outdated = []
        
        for package, min_version in required.items():
            try:
                mod = __import__(package)
                # 简单检查，不做版本比较
                print(f"   ✅ {package}")
            except ImportError:
                missing.append(package)
                print(f"   ❌ {package} 未安装")
        
        if missing:
            self.issues.append(f"缺少依赖包: {', '.join(missing)}")
            return False
        
        return True
    
    def check_project_structure(self) -> bool:
        """检查项目结构"""
        print("🔍 检查项目结构...")
        required_dirs = [
            'src', 'web', 'web/backend', 'web/frontend',
            'config', 'data', 'logs', 'tests'
        ]
        required_files = [
            'web/backend/app.py',
            'web/backend/models.py',
            'web/backend/services/game_service.py',
            'web/backend/services/session_manager.py'
        ]
        
        missing_dirs = []
        missing_files = []
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
                print(f"   ❌ 目录缺失: {dir_path}")
            else:
                print(f"   ✅ {dir_path}")
        
        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                print(f"   ❌ 文件缺失: {file_path}")
        
        if missing_dirs or missing_files:
            self.issues.append("项目结构不完整")
            return False
        
        return True
    
    def check_env_file(self) -> bool:
        """检查环境配置"""
        print("🔍 检查环境配置...")
        env_file = project_root / '.env'
        
        if not env_file.exists():
            print("   ⚠️ .env 文件不存在，创建默认配置...")
            self.create_default_env()
            self.fixes_applied.append("创建了默认 .env 文件")
        
        # 检查必要的环境变量
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
                if 'DEEPSEEK_API_KEY' not in content:
                    print("   ⚠️ 未配置 DEEPSEEK_API_KEY (AI功能将不可用)")
                else:
                    print("   ✅ AI API密钥已配置")
        
        print("   ✅ 环境配置就绪")
        return True
    
    def create_default_env(self):
        """创建默认环境配置"""
        env_content = """# RuleK 环境配置
# API配置
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 服务器配置  
HOST=0.0.0.0
PORT=8000
RELOAD=true

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/rulek.log

# 游戏配置
MAX_SESSIONS=100
SESSION_TIMEOUT=3600
"""
        env_file = project_root / '.env'
        with open(env_file, 'w') as f:
            f.write(env_content)
    
    def check_server_running(self) -> bool:
        """检查服务器是否运行"""
        print("🔍 检查服务器状态...")
        try:
            response = httpx.get(f"{self.server_url}/", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 服务器运行中: {data['name']} v{data['version']}")
                return True
        except:
            pass
        
        print("   ❌ 服务器未运行")
        self.issues.append("服务器未运行")
        return False
    
    async def test_api_endpoints(self) -> bool:
        """测试API端点"""
        print("🔍 测试API端点...")
        
        async with httpx.AsyncClient() as client:
            # 测试创建游戏
            try:
                response = await client.post(
                    f"{self.server_url}/api/games",
                    json={"difficulty": "normal", "npc_count": 4},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    game_id = data['game_id']
                    print(f"   ✅ 创建游戏: {game_id}")
                    
                    # 测试获取状态
                    response = await client.get(
                        f"{self.server_url}/api/games/{game_id}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        print(f"   ✅ 获取游戏状态")
                        return True
                    else:
                        print(f"   ❌ 获取状态失败: {response.status_code}")
                else:
                    print(f"   ❌ 创建游戏失败: {response.status_code}")
            except Exception as e:
                print(f"   ❌ API测试失败: {e}")
                self.issues.append("API端点异常")
        
        return False
    
    def fix_issues(self):
        """尝试修复发现的问题"""
        print("\n🔧 尝试自动修复...")
        
        # 修复依赖
        if "缺少依赖包" in str(self.issues):
            print("   📦 安装缺失的依赖包...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.fixes_applied.append("安装了缺失的依赖包")
                print("   ✅ 依赖包安装完成")
            else:
                print("   ❌ 依赖包安装失败")
        
        # 创建缺失的目录
        if "项目结构不完整" in str(self.issues):
            print("   📁 创建缺失的目录...")
            for dir_name in ['logs', 'data', 'data/saves']:
                dir_path = project_root / dir_name
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.fixes_applied.append(f"创建了目录: {dir_name}")
            print("   ✅ 目录结构修复完成")
        
        # 启动服务器
        if "服务器未运行" in str(self.issues):
            print("   🚀 尝试启动服务器...")
            print("   请在新终端运行: python start_server_enhanced.py")
            self.fixes_applied.append("提供了服务器启动指令")
    
    def print_summary(self):
        """打印诊断总结"""
        print("\n" + "=" * 70)
        print("📊 诊断报告")
        print("=" * 70)
        
        if not self.issues:
            print("✅ 未发现问题，系统运行正常!")
        else:
            print("⚠️ 发现以下问题:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        if self.fixes_applied:
            print("\n✅ 已应用的修复:")
            for fix in self.fixes_applied:
                print(f"   - {fix}")
        
        print("\n" + "=" * 70)
        print("💡 建议操作:")
        print("=" * 70)
        
        if "服务器未运行" in str(self.issues):
            print("1. 启动服务器:")
            print("   python start_server_enhanced.py")
            print()
        
        print("2. 运行API测试:")
        print("   python fix_api.py")
        print()
        
        print("3. 查看API文档:")
        print("   http://localhost:8000/docs")
        print()
        
        if "DEEPSEEK_API_KEY" in str(self.issues):
            print("4. 配置AI密钥 (可选):")
            print("   编辑 .env 文件，添加你的 DEEPSEEK_API_KEY")
            print()
    
    async def run_diagnostic(self):
        """运行完整诊断"""
        self.print_header()
        
        # 基础检查
        self.check_python_version()
        self.check_dependencies()
        self.check_project_structure()
        self.check_env_file()
        
        # 服务器检查
        server_running = self.check_server_running()
        
        # API测试（仅在服务器运行时）
        if server_running:
            await self.test_api_endpoints()
        
        # 自动修复
        if self.issues:
            self.fix_issues()
        
        # 打印总结
        self.print_summary()


def main():
    """主函数"""
    diagnostic = RuleKDiagnostic()
    
    try:
        # 运行诊断
        asyncio.run(diagnostic.run_diagnostic())
        
        # 询问是否运行测试
        if not diagnostic.issues or "服务器未运行" not in str(diagnostic.issues):
            response = input("\n是否运行完整的API测试？(y/n): ")
            if response.lower() == 'y':
                print("\n运行API测试...")
                subprocess.run([sys.executable, "fix_api.py"])
        
    except KeyboardInterrupt:
        print("\n\n👋 诊断中断")
    except Exception as e:
        print(f"\n❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
