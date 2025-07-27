#!/usr/bin/env python
"""
修复所有已知问题的脚本
"""
import os
import sys
import subprocess
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

def fix_permissions():
    """修复脚本执行权限"""
    print("🔧 修复脚本执行权限...")
    scripts = ["start.sh", "quick_start.sh", "run_game.sh"]
    
    for script in scripts:
        script_path = PROJECT_ROOT / script
        if script_path.exists():
            os.chmod(script_path, 0o755)
            print(f"✅ 已添加执行权限: {script}")
    
    # 同时修复Python脚本
    py_scripts = ["rulek.py", "scripts/dev_tools.py"]
    for script in py_scripts:
        script_path = PROJECT_ROOT / script
        if script_path.exists():
            os.chmod(script_path, 0o755)
            print(f"✅ 已添加执行权限: {script}")

def fix_imports():
    """修复导入问题"""
    print("\n🔧 修复导入问题...")
    
    # 修复 rulek.py 中的 load_config 导入
    rulek_path = PROJECT_ROOT / "rulek.py"
    with open(rulek_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换错误的导入
    content = content.replace(
        'from src.utils.config import load_config',
        'from src.utils.config import config'
    )
    
    with open(rulek_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已修复 rulek.py 的导入")

def fix_game_state_manager():
    """修复 GameStateManager 的问题"""
    print("\n🔧 修复 GameStateManager...")
    
    # 修复 save_game 方法签名
    game_state_path = PROJECT_ROOT / "src/core/game_state.py"
    with open(game_state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修改 save_game 方法签名以接受可选的文件名参数
    content = content.replace(
        'def save_game(self) -> bool:',
        'def save_game(self, filename: Optional[str] = None) -> bool:'
    )
    
    # 使用提供的文件名或默认文件名
    content = content.replace(
        'save_file = self.save_dir / f"{self.state.game_id}.json"',
        '''if filename:
            save_file = self.save_dir / filename
        else:
            save_file = self.save_dir / f"{self.state.game_id}.json"'''
    )
    
    with open(game_state_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已修复 save_game 方法签名")
    
    # 修复 new_game 方法以创建默认NPC
    fix_new_game_npcs()

def fix_new_game_npcs():
    """修复 new_game 方法以创建默认NPC"""
    print("\n🔧 修复默认NPC创建...")
    
    # 创建一个补丁文件来修改 GameStateManager
    patch_content = '''
# 在 new_game 方法的末尾添加默认NPC创建
def create_default_npcs(self):
    """创建默认NPC"""
    from src.models.npc import generate_random_npc
    
    default_npc_names = ["张三", "李四", "王五"]
    for name in default_npc_names:
        npc = generate_random_npc(name)
        self.add_npc(npc.__dict__ if hasattr(npc, '__dict__') else npc)
'''
    
    # 修改 GameStateManager 的 new_game 方法
    game_state_path = PROJECT_ROOT / "src/core/game_state.py"
    with open(game_state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在 new_game 方法的返回语句前添加创建默认NPC的调用
    if 'def create_default_npcs' not in content:
        # 添加方法定义
        content = content.replace(
            'class GameStateManager:',
            'class GameStateManager:'
        )
        
        # 在 new_game 方法返回前添加创建NPC的调用
        content = content.replace(
            'return self.state',
            '''# 创建默认NPC
        self._create_default_npcs()
        
        return self.state'''
        )
        
        # 在类的末尾添加创建默认NPC的方法
        class_end = content.rfind('# 单元测试')
        if class_end == -1:
            class_end = content.rfind('if __name__')
        
        method_def = '''
    def _create_default_npcs(self):
        """创建默认NPC"""
        try:
            from ..models.npc import generate_random_npc
            
            default_npc_names = ["张三", "李四", "王五"]
            for name in default_npc_names:
                npc = generate_random_npc(name)
                npc_dict = npc.__dict__ if hasattr(npc, '__dict__') else npc
                self.add_npc(npc_dict)
        except ImportError:
            # 如果无法导入NPC模块，创建简单的NPC
            for i, name in enumerate(["张三", "李四", "王五"]):
                simple_npc = {
                    "id": f"npc_{i+1}",
                    "name": name,
                    "hp": 100,
                    "sanity": 100,
                    "fear": 0,
                    "location": "living_room"
                }
                self.add_npc(simple_npc)

'''
        
        content = content[:class_end] + method_def + content[class_end:]
    
    with open(game_state_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已修复默认NPC创建")

def fix_time_range_check():
    """修复时间范围检查，严格验证时间格式"""
    print("\n🔧 修复时间范围检查...")
    
    rule_executor_path = PROJECT_ROOT / "src/core/rule_executor.py"
    with open(rule_executor_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修改 _check_time_range 方法，使用正则检查格式
    new_method = '''    def _check_time_range(self, current_time: str, time_range: Dict[str, str]) -> bool:
        """检查时间是否在范围内

        Args:
            current_time: 当前时间字符串，格式为 "HH:MM"
            time_range: 时间范围字典，包含 "from" 和 "to" 键

        Returns:
            bool: 时间是否在范围内
        """
        try:
            import re

            start_time = time_range.get("from", "")
            end_time = time_range.get("to", "")

            pattern = re.compile(r"^\d{2}:\d{2}$")
            for label, t in {"current_time": current_time, "start_time": start_time, "end_time": end_time}.items():
                if not pattern.match(t):
                    logger.error(f"时间格式错误: '{t}' 不符合 HH:MM 格式")
                    return False
            
            # 使用 datetime 解析时间以确保格式正确
            current = datetime.strptime(current_time, "%H:%M")
            start = datetime.strptime(start_time, "%H:%M")
            end = datetime.strptime(end_time, "%H:%M")
            
            # 将所有时间转换为当天的时间
            today = datetime.now().date()
            current = current.replace(year=today.year, month=today.month, day=today.day)
            start = start.replace(year=today.year, month=today.month, day=today.day)
            end = end.replace(year=today.year, month=today.month, day=today.day)
            
            # 处理跨午夜的情况
            if start > end:
                # 如果开始时间大于结束时间，说明跨越了午夜
                # 例如: 23:00 到 02:00
                if current >= start:  # 当前时间在今天的范围内
                    return True
                # 将结束时间调整到第二天
                from datetime import timedelta
                end = end + timedelta(days=1)
                # 也需要检查当前时间是否在第二天的范围内
                current_tomorrow = current + timedelta(days=1)
                return current_tomorrow <= end
            else:
                # 正常情况：开始时间小于等于结束时间
                return start <= current <= end
                
        except ValueError as e:
            logger.error(f"时间格式错误: {e}. 期望格式: HH:MM")
            return False
        except Exception as e:
            logger.error(f"时间范围检查失败: {e}")
            return False'''
    
    # 查找并替换原方法
    import re
    pattern = r'def _check_time_range\(self.*?\n(?:.*?\n)*?.*?return False'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content.replace(match.group(0), new_method.strip())
    
    with open(rule_executor_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已修复时间范围检查")

def fix_missing_attributes():
    """修复缺失的属性和类型注解"""
    print("\n🔧 修复缺失的属性...")
    
    # 修复 GameState 缺失的属性
    game_state_path = PROJECT_ROOT / "src/core/game_state.py"
    with open(game_state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在 GameState 类中添加缺失的属性
    if 'active_rules:' not in content:
        content = content.replace(
            '# 角色\n    npcs:',
            '''# 规则
    active_rules: List[str] = field(default_factory=list)
    turn: int = 0  # 当前回合（与current_turn同步）
    
    # 角色
    npcs:'''
        )
    
    with open(game_state_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已修复 GameState 缺失的属性")

def install_frontend_deps():
    """安装前端依赖"""
    print("\n🔧 安装前端依赖...")
    
    frontend_dir = PROJECT_ROOT / "web/frontend"
    if frontend_dir.exists():
        os.chdir(frontend_dir)
        try:
            subprocess.run(["npm", "install"], check=True)
            print("✅ 前端依赖安装成功")
        except subprocess.CalledProcessError:
            print("❌ 前端依赖安装失败")
        except FileNotFoundError:
            print("❌ 未找到 npm，请先安装 Node.js")
        finally:
            os.chdir(PROJECT_ROOT)
    else:
        print("⚠️  前端目录不存在")

def run_code_quality_fixes():
    """运行代码质量修复"""
    print("\n🔧 运行代码质量修复...")
    
    try:
        # 使用 ruff 自动修复
        subprocess.run(["ruff", "check", "src/", "--fix"], capture_output=True)
        print("✅ ruff 自动修复完成")
    except FileNotFoundError:
        print("⚠️  未安装 ruff")
    
    # 修复常见的 mypy 问题
    fix_type_annotations()

def fix_type_annotations():
    """修复类型注解问题"""
    print("\n🔧 修复类型注解...")
    
    # 在文件顶部添加必要的导入
    files_to_fix = [
        "src/core/game_state.py",
        "src/core/rule_executor.py",
        "src/managers/rule_manager.py"
    ]
    
    for file_path in files_to_fix:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 确保有必要的类型导入
            if 'from typing import' in content and 'Optional' not in content:
                content = content.replace(
                    'from typing import',
                    'from typing import Optional,'
                )
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    print("✅ 类型注解修复完成")

def main():
    """主函数"""
    print("🚀 开始修复所有问题...\n")
    
    # 1. 修复权限
    fix_permissions()
    
    # 2. 修复导入
    fix_imports()
    
    # 3. 修复 GameStateManager
    fix_game_state_manager()
    
    # 4. 修复时间范围检查
    fix_time_range_check()
    
    # 5. 修复缺失的属性
    fix_missing_attributes()
    
    # 6. 安装前端依赖
    install_frontend_deps()
    
    # 7. 代码质量修复
    run_code_quality_fixes()
    
    print("\n✨ 所有修复完成！")
    print("\n建议的后续步骤：")
    print("1. 运行测试: python rulek.py test")
    print("2. 检查代码: python scripts/dev_tools.py check")
    print("3. 启动游戏: ./start.sh 或 python rulek.py web")

if __name__ == "__main__":
    main()
