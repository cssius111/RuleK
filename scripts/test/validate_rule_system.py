#!/usr/bin/env python3
"""
RuleK 规则系统完整验证脚本
验证所有规则相关功能是否正常工作
"""
import os
import json
import time
from pathlib import Path

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} 缺失: {filepath}")
        return False

def validate_backend_files():
    """验证后端文件"""
    print("\n📁 验证后端文件...")
    print("-" * 50)
    
    files_to_check = [
        ("data/rule_templates.json", "规则模板数据"),
        ("web/backend/services/rule_service.py", "规则服务"),
        ("web/backend/models/rule_models.py", "规则模型"),
    ]
    
    all_exist = True
    for filepath, desc in files_to_check:
        if not check_file_exists(filepath, desc):
            all_exist = False
    
    # 检查规则模板内容
    if Path("data/rule_templates.json").exists():
        with open("data/rule_templates.json", 'r', encoding='utf-8') as f:
            templates = json.load(f)
            print(f"   📋 包含 {len(templates)} 个规则模板")
    
    return all_exist

def validate_frontend_files():
    """验证前端文件"""
    print("\n📁 验证前端文件...")
    print("-" * 50)
    
    files_to_check = [
        ("web/frontend/src/stores/rules.ts", "规则Store"),
        ("web/frontend/src/types/rule.ts", "规则类型定义"),
        ("web/frontend/src/components/game/RuleCreatorModal.vue", "规则创建模态框"),
        ("web/frontend/src/components/game/RuleTemplateSelector.vue", "模板选择器"),
        ("web/frontend/src/components/game/RuleCustomForm.vue", "自定义表单"),
        ("web/frontend/src/components/game/RuleAIParser.vue", "AI解析器"),
        ("web/frontend/src/components/game/RuleCard.vue", "规则卡片"),
    ]
    
    all_exist = True
    for filepath, desc in files_to_check:
        if not check_file_exists(filepath, desc):
            all_exist = False
    
    return all_exist

def check_api_integration():
    """检查API集成"""
    print("\n🔌 检查API集成...")
    print("-" * 50)
    
    app_path = "web/backend/app.py"
    if not Path(app_path).exists():
        print(f"❌ app.py 文件不存在")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    endpoints = [
        ("/api/rules/templates", "获取规则模板"),
        ("/api/games/{game_id}/rules/template", "从模板创建规则"),
        ("/api/games/{game_id}/rules/custom", "创建自定义规则"),
        ("/api/games/{game_id}/rules", "获取规则列表"),
        ("/api/ai/parse-rule", "AI解析规则"),
    ]
    
    all_integrated = True
    for endpoint, desc in endpoints:
        if endpoint.replace("{game_id}", "") in content:
            print(f"✅ {desc}: {endpoint}")
        else:
            print(f"❌ {desc} 未集成: {endpoint}")
            all_integrated = False
    
    return all_integrated

def generate_summary():
    """生成总结报告"""
    print("\n" + "=" * 60)
    print("📊 规则系统验证报告")
    print("=" * 60)
    
    # 验证各部分
    backend_ok = validate_backend_files()
    frontend_ok = validate_frontend_files()
    api_ok = check_api_integration()
    
    print("\n📈 验证结果总结")
    print("-" * 50)
    
    results = {
        "后端文件": backend_ok,
        "前端组件": frontend_ok,
        "API集成": api_ok
    }
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}: {'完成' if status else '未完成'}")
    
    print(f"\n完成度: {passed}/{total} ({passed*100//total}%)")
    
    if passed == total:
        print("\n🎉 恭喜！规则系统已完全就绪！")
        print("\n下一步：")
        print("1. 启动服务器: python start_servers_simple.py")
        print("2. 运行测试: python test_rule_system.py")
        print("3. 访问界面: http://localhost:5173")
    else:
        print("\n⚠️ 部分组件未完成，请运行以下脚本：")
        if not backend_ok:
            print("- python improve_rules.py")
        if not api_ok:
            print("- python integrate_rule_api.py")
        if not frontend_ok:
            print("- python create_frontend_components.py")

def show_quick_commands():
    """显示快速命令"""
    print("\n" + "=" * 60)
    print("⚡ 快速命令参考")
    print("=" * 60)
    
    commands = [
        ("启动服务器", "python start_servers_simple.py"),
        ("测试规则系统", "python test_rule_system.py"),
        ("改进规则", "python improve_rules.py"),
        ("集成API", "python integrate_rule_api.py"),
        ("创建组件", "python create_frontend_components.py"),
    ]
    
    for desc, cmd in commands:
        print(f"{desc:15} : {cmd}")

def create_test_game_script():
    """创建测试游戏脚本"""
    test_script = '''#!/usr/bin/env python3
"""快速测试规则创建"""
import requests
import json

# 创建游戏
game_resp = requests.post("http://localhost:8000/api/games", json={
    "config": {
        "initial_fear_points": 2000,
        "initial_npc_count": 4,
        "difficulty": "normal",
        "ai_enabled": True
    }
})

if game_resp.status_code == 200:
    game_id = game_resp.json()["game_id"]
    print(f"✅ 游戏创建成功: {game_id}")
    
    # 创建规则
    rule_resp = requests.post(
        f"http://localhost:8000/api/games/{game_id}/rules/template",
        json={"template_id": "midnight_mirror"}
    )
    
    if rule_resp.status_code == 200:
        print(f"✅ 规则创建成功: {rule_resp.json()['rule']['name']}")
    else:
        print(f"❌ 规则创建失败: {rule_resp.status_code}")
else:
    print(f"❌ 游戏创建失败: {game_resp.status_code}")
'''
    
    with open("quick_test_rule.py", 'w') as f:
        f.write(test_script)
    
    print("\n✅ 创建快速测试脚本: quick_test_rule.py")

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 RuleK 规则系统完整性验证")
    print("=" * 60)
    print(f"验证时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 生成验证报告
    generate_summary()
    
    # 显示快速命令
    show_quick_commands()
    
    # 创建测试脚本
    create_test_game_script()
    
    print("\n" + "=" * 60)
    print("验证完成！")

if __name__ == "__main__":
    main()
