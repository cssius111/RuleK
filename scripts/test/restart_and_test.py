#!/usr/bin/env python3
"""
RuleK API 一键重启和测试
重启服务器并验证所有修复
"""
import sys
import time
import subprocess
import signal
import os
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ServerRestartTester:
    """服务器重启测试器"""
    
    def __init__(self):
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
    
    def kill_existing_server(self):
        """杀死现有服务器进程"""
        self.log("检查现有服务器进程...")
        
        try:
            # 尝试找到占用8000端口的进程
            if sys.platform == "darwin" or sys.platform == "linux":
                # Mac/Linux
                result = subprocess.run(
                    ["lsof", "-ti:8000"],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            self.log(f"终止进程 PID: {pid}")
                        except:
                            pass
                    time.sleep(2)
            elif sys.platform == "win32":
                # Windows
                subprocess.run(
                    'FOR /F "tokens=5" %P IN (\'netstat -ano ^| findstr :8000\') DO TaskKill /PID %P /F',
                    shell=True,
                    capture_output=True
                )
                time.sleep(2)
        except Exception as e:
            self.log(f"无法终止现有进程: {e}", "WARNING")
    
    def start_server(self):
        """启动新服务器"""
        self.log("启动API服务器...", "ROCKET")
        
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "rulek.py", "web"],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            self.log("等待服务器启动...")
            for i in range(10):
                time.sleep(1)
                
                # 检查服务器是否响应
                import httpx
                try:
                    response = httpx.get("http://localhost:8000/health", timeout=2)
                    if response.status_code == 200:
                        self.log("服务器启动成功！", "SUCCESS")
                        return True
                except:
                    pass
            
            self.log("服务器启动超时", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"无法启动服务器: {e}", "ERROR")
            return False
    
    def run_verification(self):
        """运行验证测试"""
        self.log("运行修复验证测试...")
        
        try:
            result = subprocess.run(
                [sys.executable, "scripts/test/verify_fixes.py"],
                cwd=project_root,
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            self.log(f"测试失败: {e}", "ERROR")
            return False
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        self.log("运行综合测试...")
        
        try:
            result = subprocess.run(
                [sys.executable, "scripts/test/test_api_comprehensive.py"],
                cwd=project_root,
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            self.log(f"综合测试失败: {e}", "ERROR")
            return False
    
    def stop_server(self):
        """停止服务器"""
        if self.server_process:
            self.log("停止服务器...")
            self.server_process.terminate()
            time.sleep(1)
            if self.server_process.poll() is None:
                self.server_process.kill()
            self.server_process = None
            self.log("服务器已停止", "SUCCESS")
    
    def run(self):
        """主流程"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║         RuleK API 一键重启和测试                           ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        try:
            # 1. 杀死现有服务器
            self.kill_existing_server()
            
            # 2. 启动新服务器
            if not self.start_server():
                self.log("无法启动服务器，请手动检查", "ERROR")
                return False
            
            # 3. 运行验证测试
            self.log("\n" + "=" * 60)
            self.log("步骤1: 验证修复")
            self.log("=" * 60)
            
            if self.run_verification():
                self.log("修复验证通过！", "SUCCESS")
                
                # 4. 询问是否运行完整测试
                print("\n是否运行完整测试套件？")
                print("1. 是 - 运行综合测试")
                print("2. 否 - 保持服务器运行")
                print("3. 退出")
                
                choice = input("\n请选择 (1-3): ").strip()
                
                if choice == "1":
                    self.log("\n" + "=" * 60)
                    self.log("步骤2: 综合测试")
                    self.log("=" * 60)
                    
                    if self.run_comprehensive_test():
                        self.log("\n🎉 所有测试通过！API完全正常", "SUCCESS")
                    else:
                        self.log("\n⚠️ 部分测试失败，请查看详情", "WARNING")
                        
                elif choice == "2":
                    self.log("\n服务器保持运行中...", "INFO")
                    self.log("访问 http://localhost:8000/docs 查看API文档", "INFO")
                    self.log("按 Ctrl+C 停止服务器", "INFO")
                    
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        pass
            else:
                self.log("修复验证失败，请检查错误", "ERROR")
                
        except KeyboardInterrupt:
            self.log("\n操作被中断", "WARNING")
        finally:
            self.stop_server()
            self.log("\n测试完成", "INFO")


def main():
    """主函数"""
    tester = ServerRestartTester()
    
    # 设置信号处理
    def signal_handler(sig, frame):
        tester.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    tester.run()


if __name__ == "__main__":
    main()
