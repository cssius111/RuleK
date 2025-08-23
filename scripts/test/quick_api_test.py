#!/usr/bin/env python3
"""
RuleK API 快速测试工具
一键启动服务器并运行测试
"""
import sys
import os
import time
import subprocess
import asyncio
import signal
from pathlib import Path
from typing import Optional

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class QuickAPITester:
    """快速API测试器"""
    
    def __init__(self):
        self.project_root = project_root
        self.server_process = None
        
    def log(self, message: str, level: str = "INFO"):
        """日志输出"""
        symbol = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "ROCKET": "🚀"
        }.get(level, "📝")
        print(f"{symbol} {message}")
    
    def print_banner(self):
        """打印横幅"""
        print("""
╔══════════════════════════════════════════════════╗
║         RuleK API 快速测试工具                  ║
╚══════════════════════════════════════════════════╝
        """)
    
    def check_port_available(self, port: int = 8000) -> bool:
        """检查端口是否可用"""
        import socket
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return True
            except:
                return False
    
    def start_server(self) -> bool:
        """启动API服务器"""
        self.log("启动API服务器...", "ROCKET")
        
        # 检查端口
        if not self.check_port_available(8000):
            self.log("端口8000已被占用", "WARNING")
            self.log("尝试关闭占用的进程...", "INFO")
            
            # 尝试杀死占用端口的进程
            try:
                if sys.platform == "darwin" or sys.platform == "linux":
                    subprocess.run(["lsof", "-ti:8000"], shell=True, capture_output=True)
                    subprocess.run(["kill", "-9", "$(lsof -ti:8000)"], shell=True)
                elif sys.platform == "win32":
                    subprocess.run(["netstat", "-ano", "|", "findstr", ":8000"], shell=True)
                time.sleep(2)
            except:
                pass
        
        # 启动服务器
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "rulek.py", "web"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            self.log("等待服务器启动...", "INFO")
            time.sleep(3)
            
            # 检查服务器是否运行
            import httpx
            try:
                response = httpx.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    self.log("服务器启动成功！", "SUCCESS")
                    self.log("API地址: http://localhost:8000", "INFO")
                    self.log("文档地址: http://localhost:8000/docs", "INFO")
                    return True
            except:
                pass
            
            self.log("服务器启动失败", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"无法启动服务器: {e}", "ERROR")
            return False
    
    def stop_server(self):
        """停止服务器"""
        if self.server_process:
            self.log("停止服务器...", "INFO")
            self.server_process.terminate()
            time.sleep(1)
            if self.server_process.poll() is None:
                self.server_process.kill()
            self.server_process = None
            self.log("服务器已停止", "SUCCESS")
    
    async def run_quick_tests(self) -> bool:
        """运行快速测试"""
        self.log("=" * 60)
        self.log("运行快速API测试", "INFO")
        self.log("=" * 60)
        
        import httpx
        
        try:
            async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                # 1. 测试根路径
                self.log("测试根路径...", "INFO")
                response = await client.get("/")
                if response.status_code == 200:
                    self.log("  ✓ 根路径正常", "SUCCESS")
                else:
                    self.log("  ✗ 根路径失败", "ERROR")
                    return False
                
                # 2. 测试健康检查
                self.log("测试健康检查...", "INFO")
                response = await client.get("/health")
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"  ✓ 健康检查正常 - 活跃游戏: {data.get('active_games', 0)}", "SUCCESS")
                else:
                    self.log("  ✗ 健康检查失败", "ERROR")
                    return False
                
                # 3. 测试创建游戏
                self.log("测试创建游戏...", "INFO")
                response = await client.post(
                    "/api/games",
                    json={"difficulty": "normal", "npc_count": 3}
                )
                if response.status_code == 200:
                    game_data = response.json()
                    game_id = game_data.get("game_id")
                    self.log(f"  ✓ 游戏创建成功 - ID: {game_id}", "SUCCESS")
                    
                    # 4. 测试获取游戏状态
                    self.log("测试获取游戏状态...", "INFO")
                    response = await client.get(f"/api/games/{game_id}")
                    if response.status_code == 200:
                        state = response.json()
                        self.log(f"  ✓ 游戏状态正常 - 回合: {state.get('current_turn', 0)}", "SUCCESS")
                    else:
                        self.log("  ✗ 获取游戏状态失败", "ERROR")
                        return False
                    
                    # 5. 测试规则模板
                    self.log("测试规则模板...", "INFO")
                    response = await client.get("/api/rules/templates")
                    if response.status_code == 200:
                        templates = response.json()
                        self.log(f"  ✓ 规则模板正常", "SUCCESS")
                    else:
                        self.log("  ✗ 获取规则模板失败", "ERROR")
                    
                    return True
                else:
                    self.log("  ✗ 游戏创建失败", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"测试失败: {e}", "ERROR")
            return False
    
    def run_comprehensive_tests(self) -> bool:
        """运行综合测试"""
        self.log("=" * 60)
        self.log("运行综合API测试", "INFO")
        self.log("=" * 60)
        
        test_script = self.project_root / "scripts" / "test" / "test_api_comprehensive.py"
        
        if not test_script.exists():
            self.log("综合测试脚本不存在", "WARNING")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            self.log(f"无法运行综合测试: {e}", "ERROR")
            return False
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print("\n" + "=" * 60)
            print("选择操作:")
            print("1. 运行快速测试")
            print("2. 运行综合测试")
            print("3. 打开API文档 (浏览器)")
            print("4. 查看服务器日志")
            print("5. 重启服务器")
            print("0. 退出")
            print("=" * 60)
            
            choice = input("请选择 (0-5): ").strip()
            
            if choice == "1":
                asyncio.run(self.run_quick_tests())
            elif choice == "2":
                self.run_comprehensive_tests()
            elif choice == "3":
                import webbrowser
                webbrowser.open("http://localhost:8000/docs")
                self.log("已在浏览器中打开API文档", "SUCCESS")
            elif choice == "4":
                self.log("服务器日志:", "INFO")
                if self.server_process:
                    # 读取一些输出
                    for _ in range(10):
                        line = self.server_process.stdout.readline()
                        if line:
                            print(f"  {line.strip()}")
                else:
                    self.log("服务器未运行", "WARNING")
            elif choice == "5":
                self.stop_server()
                self.start_server()
            elif choice == "0":
                break
            else:
                self.log("无效选择", "WARNING")
    
    def run(self):
        """运行测试器"""
        self.print_banner()
        
        # 先运行修复脚本
        self.log("运行API修复脚本...", "INFO")
        fix_script = self.project_root / "scripts" / "fix" / "fix_api.py"
        if fix_script.exists():
            subprocess.run([sys.executable, str(fix_script)], cwd=self.project_root)
        
        # 启动服务器
        if not self.start_server():
            self.log("无法启动服务器，请检查错误", "ERROR")
            return
        
        try:
            # 运行快速测试
            test_passed = asyncio.run(self.run_quick_tests())
            
            if test_passed:
                self.log("=" * 60)
                self.log("✨ 快速测试通过！API基本功能正常", "SUCCESS")
                self.log("=" * 60)
                
                # 询问是否运行更多测试
                print("\n选择下一步操作:")
                print("1. 运行综合测试")
                print("2. 进入交互式菜单")
                print("3. 保持服务器运行")
                print("0. 退出")
                
                choice = input("请选择 (0-3): ").strip()
                
                if choice == "1":
                    self.run_comprehensive_tests()
                elif choice == "2":
                    self.interactive_menu()
                elif choice == "3":
                    self.log("服务器保持运行中...", "INFO")
                    self.log("按 Ctrl+C 停止", "INFO")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        pass
            else:
                self.log("快速测试失败，请检查API实现", "ERROR")
                
        except KeyboardInterrupt:
            self.log("\n测试被中断", "WARNING")
        finally:
            self.stop_server()
            self.log("测试完成", "INFO")


def main():
    """主函数"""
    tester = QuickAPITester()
    
    # 设置信号处理
    def signal_handler(sig, frame):
        tester.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    tester.run()


if __name__ == "__main__":
    main()
