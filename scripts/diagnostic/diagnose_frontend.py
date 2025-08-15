#!/usr/bin/env python3
"""
RuleK 前端问题诊断和修复
"""
import os
import subprocess
import sys
import json
import shutil

def run_command(cmd, cwd=None, show_output=False):
    """运行命令"""
    try:
        if show_output:
            result = subprocess.run(cmd, shell=True, cwd=cwd, text=True)
            return result.returncode == 0
        else:
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def diagnose_frontend():
    """诊断前端问题"""
    print("=" * 60)
    print("🔍 前端问题诊断")
    print("=" * 60)
    
    frontend_dir = os.path.join(os.path.dirname(__file__), 'web', 'frontend')
    issues = []
    
    # 1. 检查前端目录
    print("\n1. 检查前端目录...")
    if os.path.exists(frontend_dir):
        print(f"✅ 前端目录存在: {frontend_dir}")
    else:
        print(f"❌ 前端目录不存在: {frontend_dir}")
        issues.append("前端目录不存在")
        return issues
    
    # 2. 检查 package.json
    print("\n2. 检查 package.json...")
    package_json_path = os.path.join(frontend_dir, 'package.json')
    if os.path.exists(package_json_path):
        print("✅ package.json 存在")
        with open(package_json_path, 'r') as f:
            try:
                package = json.load(f)
                print(f"   项目名称: {package.get('name', 'unknown')}")
                print(f"   版本: {package.get('version', 'unknown')}")
            except json.JSONDecodeError:
                print("❌ package.json 格式错误")
                issues.append("package.json 格式错误")
    else:
        print("❌ package.json 不存在")
        issues.append("package.json 不存在")
    
    # 3. 检查 Node.js 和 npm
    print("\n3. 检查 Node.js 和 npm...")
    success, stdout, stderr = run_command("node --version")
    if success:
        print(f"✅ Node.js 已安装: {stdout.strip()}")
    else:
        print("❌ Node.js 未安装")
        issues.append("Node.js 未安装")
    
    success, stdout, stderr = run_command("npm --version")
    if success:
        print(f"✅ npm 已安装: {stdout.strip()}")
    else:
        print("❌ npm 未安装")
        issues.append("npm 未安装")
    
    # 4. 检查 node_modules
    print("\n4. 检查依赖安装...")
    node_modules = os.path.join(frontend_dir, 'node_modules')
    if os.path.exists(node_modules):
        # 计算 node_modules 中的包数量
        try:
            packages = len([d for d in os.listdir(node_modules) if os.path.isdir(os.path.join(node_modules, d))])
            print(f"✅ node_modules 存在 ({packages} 个包)")
        except:
            print("✅ node_modules 存在")
    else:
        print("❌ node_modules 不存在（需要安装依赖）")
        issues.append("依赖未安装")
    
    # 5. 检查 Vite 配置
    print("\n5. 检查 Vite 配置...")
    vite_config = os.path.join(frontend_dir, 'vite.config.js')
    vite_config_ts = os.path.join(frontend_dir, 'vite.config.ts')
    if os.path.exists(vite_config) or os.path.exists(vite_config_ts):
        print("✅ Vite 配置文件存在")
    else:
        print("❌ Vite 配置文件不存在")
        issues.append("Vite 配置文件缺失")
    
    # 6. 检查端口占用
    print("\n6. 检查端口占用...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5173))
    sock.close()
    if result == 0:
        print("⚠️ 端口 5173 已被占用")
        issues.append("端口 5173 已被占用")
    else:
        print("✅ 端口 5173 可用")
    
    return issues

def fix_frontend():
    """修复前端问题"""
    print("\n" + "=" * 60)
    print("🔧 开始修复前端")
    print("=" * 60)
    
    frontend_dir = os.path.join(os.path.dirname(__file__), 'web', 'frontend')
    
    # 1. 清理旧的 node_modules 和缓存
    print("\n1. 清理缓存...")
    node_modules = os.path.join(frontend_dir, 'node_modules')
    if os.path.exists(node_modules):
        print("   删除 node_modules...")
        shutil.rmtree(node_modules, ignore_errors=True)
    
    package_lock = os.path.join(frontend_dir, 'package-lock.json')
    if os.path.exists(package_lock):
        print("   删除 package-lock.json...")
        os.remove(package_lock)
    
    vite_cache = os.path.join(frontend_dir, '.vite')
    if os.path.exists(vite_cache):
        print("   删除 .vite 缓存...")
        shutil.rmtree(vite_cache, ignore_errors=True)
    
    print("✅ 清理完成")
    
    # 2. 安装依赖
    print("\n2. 安装依赖...")
    print("   运行 npm install（可能需要几分钟）...")
    success = run_command("npm install", cwd=frontend_dir, show_output=True)
    if success:
        print("✅ 依赖安装成功")
    else:
        print("❌ 依赖安装失败")
        print("\n尝试以下方法:")
        print("1. 使用淘宝镜像:")
        print("   npm config set registry https://registry.npmmirror.com")
        print("   npm install")
        print("2. 使用 cnpm:")
        print("   npm install -g cnpm")
        print("   cnpm install")
        print("3. 使用 yarn:")
        print("   npm install -g yarn")
        print("   yarn install")
        return False
    
    # 3. 杀死占用端口的进程
    print("\n3. 清理端口...")
    os.system("lsof -ti:5173 | xargs kill -9 2>/dev/null")
    print("✅ 端口清理完成")
    
    return True

def start_frontend():
    """启动前端"""
    print("\n" + "=" * 60)
    print("🚀 启动前端服务器")
    print("=" * 60)
    
    frontend_dir = os.path.join(os.path.dirname(__file__), 'web', 'frontend')
    
    print("\n运行: npm run dev")
    print("前端将在 http://localhost:5173 启动")
    print("\n按 Ctrl+C 停止服务器")
    
    # 启动前端
    subprocess.run("npm run dev", shell=True, cwd=frontend_dir)

def main():
    # 诊断问题
    issues = diagnose_frontend()
    
    if issues:
        print("\n" + "=" * 60)
        print("⚠️ 发现以下问题:")
        print("=" * 60)
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        
        # 询问是否修复
        print("\n是否尝试自动修复? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice == 'y':
            if fix_frontend():
                print("\n✅ 修复完成")
                print("\n是否启动前端? (y/n): ", end="")
                if input().strip().lower() == 'y':
                    start_frontend()
            else:
                print("\n❌ 修复失败，请手动处理")
    else:
        print("\n" + "=" * 60)
        print("✅ 前端配置正常")
        print("=" * 60)
        print("\n是否启动前端? (y/n): ", end="")
        if input().strip().lower() == 'y':
            start_frontend()

if __name__ == "__main__":
    main()
