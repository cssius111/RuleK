#!/usr/bin/env python
"""
快速测试修复结果
"""
import sys
import os
import subprocess

# 切换到项目目录
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

print("🧪 测试修复结果...\n")

# 1. 测试导入
print("1. 测试导入修复...")
try:
    result = subprocess.run([sys.executable, "-c", "from src.utils.config import config; print('✅ 导入成功')"], 
                          capture_output=True, text=True)
    print(result.stdout.strip() if result.returncode == 0 else f"❌ 导入失败: {result.stderr}")
except Exception as e:
    print(f"❌ 导入测试失败: {e}")

# 2. 测试 GameStateManager
print("\n2. 测试 GameStateManager...")
test_code = """
import sys
sys.path.insert(0, '.')
from src.core.game_state import GameStateManager

gsm = GameStateManager()
state = gsm.new_game()

# 检查是否有NPC
if len(gsm.npcs) > 0:
    print(f'✅ 默认NPC创建成功: {len(gsm.npcs)} 个NPC')
else:
    print('❌ 默认NPC创建失败')

# 测试 save_game 签名
try:
    gsm.save_game("test.json")
    print('✅ save_game 方法签名修复成功')
except Exception as e:
    print(f'❌ save_game 方法失败: {e}')
"""

try:
    result = subprocess.run([sys.executable, "-c", test_code], capture_output=True, text=True)
    print(result.stdout.strip() if result.returncode == 0 else f"错误: {result.stderr}")
except Exception as e:
    print(f"❌ GameStateManager 测试失败: {e}")

# 3. 测试时间范围检查
print("\n3. 测试时间范围检查...")
test_time_code = """
import sys
sys.path.insert(0, '.')
from src.core.rule_executor import RuleExecutor
from src.core.game_state import GameStateManager

gsm = GameStateManager()
executor = RuleExecutor(gsm)

# 测试宽松格式
result = executor._check_time_range("10:30", {"from": "9:00", "to": "12:00"})
if result:
    print('✅ 宽松时间格式支持成功')
else:
    print('❌ 宽松时间格式支持失败')
"""

try:
    result = subprocess.run([sys.executable, "-c", test_time_code], capture_output=True, text=True)
    print(result.stdout.strip() if result.returncode == 0 else f"错误: {result.stderr}")
except Exception as e:
    print(f"❌ 时间范围测试失败: {e}")

# 4. 运行单元测试
print("\n4. 运行单元测试...")
try:
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/unit/test_game.py", "-v", "--tb=short"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ 单元测试通过")
    else:
        # 提取失败的测试
        lines = result.stdout.split('\n')
        failed_tests = [line for line in lines if 'FAILED' in line or 'ERROR' in line]
        if failed_tests:
            print("❌ 部分测试失败:")
            for test in failed_tests[:3]:  # 只显示前3个失败
                print(f"  - {test}")
except Exception as e:
    print(f"❌ 测试运行失败: {e}")

print("\n✨ 测试完成！")
