"""
检查并修复缺失的组件
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("检查缺失的组件...")

# 检查必要的模块
missing_modules = []

# 1. 检查DialogueSystem
try:
    from src.core.dialogue_system import DialogueSystem
    print("✅ DialogueSystem 存在")
except ImportError:
    print("❌ DialogueSystem 缺失")
    missing_modules.append("DialogueSystem")

# 2. 检查Narrator
try:
    from src.core.narrator import Narrator
    print("✅ Narrator 存在")
except ImportError:
    print("❌ Narrator 缺失")
    missing_modules.append("Narrator")

# 3. 检查事件模型
try:
    from src.models.event import Event
    print("✅ Event 模型存在")
except ImportError:
    print("❌ Event 模型缺失")
    missing_modules.append("Event")

# 4. 检查MapManager
try:
    from src.models.map import MapManager
    print("✅ MapManager 存在")
except ImportError:
    print("❌ MapManager 缺失")
    missing_modules.append("MapManager")

# 5. 检查NPCManager
try:
    from src.models.npc_manager import NPCManager
    print("✅ NPCManager 存在")
except ImportError:
    try:
        from src.models import NPCManager
        print("✅ NPCManager 存在 (从 src.models)")
    except ImportError:
        print("❌ NPCManager 缺失")
        missing_modules.append("NPCManager")

# 6. 检查RuleManager
try:
    from src.models.rule_manager import RuleManager
    print("✅ RuleManager 存在")
except ImportError:
    print("❌ RuleManager 缺失")
    missing_modules.append("RuleManager")

print("\n" + "="*50)
if missing_modules:
    print(f"❌ 缺失 {len(missing_modules)} 个模块: {', '.join(missing_modules)}")
    print("\n这些模块可能需要创建占位实现或从其他位置导入")
else:
    print("✅ 所有必要模块都存在！")
