#!/usr/bin/env python3
"""
RuleK 快速启动脚本
一键启动服务器并创建测试游戏
"""

import sys
import os
import subprocess
import time
import httpx
import asyncio
import webbrowser
from pathlib import Path
import signal

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class RuleKQuickStart:
    """RuleK 快速启动器"""
    
    def __init__(self):
        self.server_process = None
        self.server_url = "http://localhost:8000"
        self.game_id = None
        
    def print_banner(self):
        """打印欢迎横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  ██████╗ ██╗   ██╗██╗     ███████╗██╗  ██╗                ║
║  ██╔══██╗██║   ██║██║     ██╔════╝██║ ██╔╝                ║
║  ██████╔╝██║   ██║██║     █████╗  █████╔╝                 ║
║  ██╔══██╗██║   ██║██║     ██╔══╝  ██╔═██╗                 ║
║  ██║  ██║╚██████╔╝███████╗███████╗██║  ██╗                ║
║  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝                ║
║                                                              ║
║         规则怪谈管理者 - Rule-based Horror Game             ║
║                      快速启动器 v1.0                        ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_port(self, port=8000):
        """检查端口是否被占用"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def start_server(self):
        """启动服务器"""
        print("🚀 启动服务器...")
        
        # 确保日志目录存在
        os.makedirs("logs", exist_ok=True)
        
        # 检查端口
        if not self.check_port():
            print("⚠️ 端口 8000 已被占用")
            print("尝试停止现有服务...")
            try:
                # Windows
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                                 capture_output=True, check=False)
                # Unix/Linux/Mac
                else:
                    subprocess.run(['pkill', '-f', 'uvicorn'], check=False)
                time.sleep(2)
            except:
                pass
            
            if not self.check_port():
                print("❌ 无法释放端口，请手动停止占用端口的程序")
                return False
        
        # 启动命令
        cmd = [
            sys.executable, "-m", "uvicorn",
            "web.backend.app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "warning"  # 减少日志输出
        ]
        
        # 启动服务器进程
        self.server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,  # 隐藏输出
            stderr=subprocess.DEVNULL,
            start_new_session=True  # 独立进程组
        )
        
        # 等待服务器启动
        print("⏳ 等待服务器就绪...")
        for i in range(10):
            time.sleep(1)
            try:
                response = httpx.get(f"{self.server_url}/", timeout=1)
                if response.status_code == 200:
                    print("✅ 服务器启动成功!")
                    return True
            except:
                continue
        
        print("❌ 服务器启动超时")
        return False
    
    async def create_test_game(self):
        """创建测试游戏"""
        print("\n🎮 创建测试游戏...")
        
        async with httpx.AsyncClient() as client:
            try:
                # 创建游戏
                response = await client.post(
                    f"{self.server_url}/api/games",
                    json={"difficulty": "normal", "npc_count": 4},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.game_id = data['game_id']
                    
                    print(f"✅ 游戏创建成功!")
                    print(f"   游戏ID: {self.game_id}")
                    print(f"   NPC数量: {len(data['npcs'])}")
                    print(f"   初始恐惧点: {data['fear_points']}")
                    
                    # 创建一个示例规则
                    await self.create_sample_rule()
                    
                    return True
                else:
                    print(f"❌ 创建失败: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ 创建游戏异常: {e}")
                return False
    
    async def create_sample_rule(self):
        """创建示例规则"""
        print("\n📝 创建示例规则...")
        
        async with httpx.AsyncClient() as client:
            try:
                rules = [
                    {
                        "name": "午夜禁言",
                        "description": "午夜时分，任何说话的人都会受到惩罚",
                        "requirements": {"time": "midnight"},
                        "trigger": {"type": "time"},
                        "effect": {"type": "damage", "value": 10},
                        "cost": 100
                    },
                    {
                        "name": "禁止奔跑",
                        "description": "在走廊中奔跑的人会被诅咒",
                        "requirements": {"location": "corridor"},
                        "trigger": {"type": "action", "action": "run"},
                        "effect": {"type": "fear", "value": 20},
                        "cost": 150
                    }
                ]
                
                for rule in rules:
                    response = await client.post(
                        f"{self.server_url}/api/games/{self.game_id}/rules",
                        json=rule,
                        timeout=5
                    )
                    if response.status_code == 200:
                        print(f"   ✅ 创建规则: {rule['name']}")
                    else:
                        print(f"   ❌ 创建失败: {rule['name']}")
                        
            except Exception as e:
                print(f"❌ 创建规则异常: {e}")
    
    def open_browser(self):
        """打开浏览器"""
        urls = [
            ("API文档", f"{self.server_url}/docs"),
            ("交互式文档", f"{self.server_url}/redoc")
        ]
        
        print("\n🌐 打开浏览器...")
        for name, url in urls:
            print(f"   {name}: {url}")
        
        # 默认打开API文档
        webbrowser.open(f"{self.server_url}/docs")
    
    def print_instructions(self):
        """打印使用说明"""
        print("\n" + "=" * 60)
        print("✨ RuleK 已准备就绪!")
        print("=" * 60)
        
        print("\n📍 访问地址:")
        print(f"   主页: {self.server_url}")
        print(f"   API文档: {self.server_url}/docs")
        print(f"   交互式文档: {self.server_url}/redoc")
        
        if self.game_id:
            print(f"\n🎮 测试游戏:")
            print(f"   游戏ID: {self.game_id}")
            print(f"   获取状态: GET /api/games/{self.game_id}")
            print(f"   推进回合: POST /api/games/{self.game_id}/turn")
        
        print("\n💡 快速测试命令:")
        print("   python fix_api.py          # 运行完整API测试")
        print("   python diagnose_and_fix.py  # 诊断和修复问题")
        
        print("\n🔧 常用操作:")
        print("   1. 在API文档页面测试各个端点")
        print("   2. 使用提供的游戏ID进行操作")
        print("   3. 查看 logs/ 目录下的日志")
        
        print("\n⌨️ 按 Ctrl+C 停止服务器")
        print("=" * 60)
    
    def cleanup(self):
        """清理资源"""
        if self.server_process:
            print("\n🛑 正在停止服务器...")
            try:
                # 发送终止信号
                if os.name == 'nt':
                    self.server_process.terminate()
                else:
                    os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                
                # 等待进程结束
                self.server_process.wait(timeout=5)
                print("✅ 服务器已停止")
            except:
                # 强制终止
                try:
                    if os.name == 'nt':
                        subprocess.run(['taskkill', '/F', '/PID', str(self.server_process.pid)],
                                     capture_output=True, check=False)
                    else:
                        os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
                except:
                    pass
    
    async def run(self):
        """运行快速启动流程"""
        self.print_banner()
        
        # 1. 启动服务器
        if not self.start_server():
            print("\n❌ 无法启动服务器")
            print("请运行: python diagnose_and_fix.py 进行诊断")
            return
        
        # 2. 创建测试游戏
        await self.create_test_game()
        
        # 3. 打开浏览器（可选）
        response = input("\n是否打开API文档页面？(y/n): ")
        if response.lower() == 'y':
            self.open_browser()
        
        # 4. 打印说明
        self.print_instructions()
        
        # 5. 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
            print("\n👋 感谢使用RuleK!")


def main():
    """主函数"""
    quick_start = RuleKQuickStart()
    
    try:
        asyncio.run(quick_start.run())
    except KeyboardInterrupt:
        quick_start.cleanup()
        print("\n👋 再见!")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        quick_start.cleanup()
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
