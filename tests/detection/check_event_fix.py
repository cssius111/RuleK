#!/usr/bin/env python3
"""检查并验证Event类修复"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔍 检查Event类...")
print("=" * 60)

# 1. 显示文件内容
event_file = project_root / "src/models/event.py"
if event_file.exists():
    print("\n📄 Event类定义（前50行）：")
    print("-" * 60)
    lines = event_file.read_text().splitlines()[:50]
    for i, line in enumerate(lines, 1):
        if '@dataclass' in line or 'class Event' in line:
            print(f">>> {i:3d}: {line}")  # 高亮重要行
        else:
            print(f"    {i:3d}: {line}")
    print("-" * 60)

# 2. 尝试导入
print("\n🧪 测试导入...")
try:
    # 清除缓存
    modules_to_clear = [
        'src.models.event',
        'src.models',
        'src.core.rule_executor',
        'src.cli_game'
    ]
    for mod in modules_to_clear:
        if mod in sys.modules:
            del sys.modules[mod]
    
    from src.models.event import Event, EventType
    print("  ✅ 导入成功")
    
    # 3. 创建实例
    print("\n🧪 创建Event实例...")
    event = Event(
        type=EventType.SYSTEM,
        description="测试事件",
        turn=1
    )
    print("  ✅ 创建成功")
    print(f"     - ID: {event.id}")
    print(f"     - Type: {event.type}")
    print(f"     - Created: {event.created_at}")
    
    # 4. 测试序列化
    print("\n🧪 测试序列化...")
    event_dict = event.to_dict()
    print("  ✅ 序列化成功")
    print(f"     - Keys: {list(event_dict.keys())}")
    
except Exception as e:
    print(f"  ❌ 错误: {e}")
    import traceback
    print("\n详细错误信息：")
    traceback.print_exc()
    
    print("\n💡 修复建议：")
    if "non-default argument" in str(e):
        print("  Event类字段顺序问题已在文件中修复，但可能有缓存")
        print("  请运行: python ultimate_cli_fix.py")
    else:
        print("  请检查错误信息并手动修复")

print("\n" + "=" * 60)
print("检查完成！")
