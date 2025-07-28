#!/usr/bin/env python3
"""
RuleK AI集成修复脚本
自动应用所有必要的修复和改进
"""
import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any


class RuleKFixer:
    """RuleK项目修复器"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.fixes_applied = []
        self.errors = []
        
    def fix_all(self):
        """应用所有修复"""
        print("🔧 开始修复 RuleK 项目...")
        
        # 1. 修复 GameStateManager difficulty 属性
        self.fix_game_state_difficulty()
        
        # 2. 修复事件打印问题
        self.fix_event_printing()
        
        # 3. 修复 CLI pause 递归
        self.fix_cli_pause()
        
        # 4. 修复 DeepSeek narrative 长度
        self.fix_narrative_length()
        
        # 5. 修复规则评估字段名
        self.fix_rule_eval_fields()
        
        # 6. 创建规则模板文件
        self.create_rule_templates()
        
        # 7. 更新启动脚本权限
        self.fix_startup_scripts()
        
        # 8. 总结
        self.print_summary()
    
    def fix_game_state_difficulty(self):
        """修复 GameStateManager 的 difficulty 属性"""
        file_path = self.project_root / "src" / "core" / "game_state.py"
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 查找插入位置
            insert_pos = content.find("@property\n    def is_game_over")
            if insert_pos == -1:
                insert_pos = content.find("def is_game_over")
            
            if insert_pos > 0:
                # 准备插入的代码
                difficulty_property = '''    @property
    def difficulty(self) -> str:
        """获取当前游戏难度"""
        return self.state.difficulty if self.state else "normal"
        
    '''
                
                # 检查是否已存在
                if "def difficulty(self)" not in content:
                    # 插入代码
                    content = content[:insert_pos] + difficulty_property + content[insert_pos:]
                    file_path.write_text(content, encoding='utf-8')
                    self.fixes_applied.append("✅ 修复 GameStateManager.difficulty 属性")
                else:
                    self.fixes_applied.append("⏭️  GameStateManager.difficulty 已存在")
            else:
                self.errors.append("❌ 无法定位 game_state.py 插入位置")
                
        except Exception as e:
            self.errors.append(f"❌ 修复 game_state.py 失败: {str(e)}")
    
    def fix_event_printing(self):
        """修复事件打印兼容性"""
        file_path = self.project_root / "src" / "cli_game.py"
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 查找并替换事件打印逻辑
            old_event_print = '''        for event in events:
            time_str = event.get("game_time", "??:??")
            print(f"[{time_str}] {event.get('description', '未知事件')}")'''
            
            new_event_print = '''        for event in events:
            # 处理 Event 对象和 dict 的兼容性
            if hasattr(event, 'to_dict'):
                event_dict = event.to_dict()
            else:
                event_dict = event if isinstance(event, dict) else {"description": str(event)}
            time_str = event_dict.get("game_time", "??:??")
            print(f"[{time_str}] {event_dict.get('description', '未知事件')}")'''
            
            if old_event_print in content:
                content = content.replace(old_event_print, new_event_print)
                file_path.write_text(content, encoding='utf-8')
                self.fixes_applied.append("✅ 修复事件打印兼容性")
            else:
                self.fixes_applied.append("⏭️  事件打印已修复")
                
        except Exception as e:
            self.errors.append(f"❌ 修复事件打印失败: {str(e)}")
    
    def fix_cli_pause(self):
        """修复 CLI pause 递归问题"""
        file_path = self.project_root / "src" / "cli_game.py"
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 查找并修复 _pause 方法
            old_pause = '''    def _pause(self):
        """暂停，等待用户按回车继续"""
        if self.is_testing:
            return
        self._pause()'''
            
            new_pause = '''    def _pause(self):
        """暂停，等待用户按回车继续（修复递归问题）"""
        if not self.is_testing:
            input("\\n按回车继续...")'''
            
            if "_pause()" in content and "self._pause()" in content:
                # 使用更精确的替换
                import re
                pattern = r'def _pause\(self\):.*?(?=\n    def|\n\n|\Z)'
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    content = content.replace(match.group(), new_pause.strip())
                    file_path.write_text(content, encoding='utf-8')
                    self.fixes_applied.append("✅ 修复 CLI pause 递归")
                else:
                    self.errors.append("❌ 无法定位 _pause 方法")
            else:
                self.fixes_applied.append("⏭️  CLI pause 已修复")
                
        except Exception as e:
            self.errors.append(f"❌ 修复 CLI pause 失败: {str(e)}")
    
    def fix_narrative_length(self):
        """修复叙事长度验证"""
        file_path = self.project_root / "src" / "api" / "deepseek_client.py"
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 修复 _ensure_len_text 方法
            old_method = '''    def _ensure_len_text(self, text: str) -> str:
        """确保文本长度符合要求"""
        if len(text) < 50:'''
            
            new_method = '''    def _ensure_len_text(self, text: str, min_len: int = 200) -> str:
        """确保文本长度符合要求"""
        if len(text) < min_len:'''
            
            if old_method in content:
                content = content.replace(old_method, new_method)
                file_path.write_text(content, encoding='utf-8')
                self.fixes_applied.append("✅ 修复叙事长度参数化")
            else:
                self.fixes_applied.append("⏭️  叙事长度已修复")
                
        except Exception as e:
            self.errors.append(f"❌ 修复叙事长度失败: {str(e)}")
    
    def fix_rule_eval_fields(self):
        """修复规则评估字段名不匹配"""
        file_path = self.project_root / "src" / "api" / "deepseek_client.py"
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 在解析JSON后添加字段映射
            search_text = "res = json.loads(json_str)"
            if search_text in content:
                # 找到所有出现的位置
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if search_text in line and i + 1 < len(lines):
                        # 检查下一行是否已有映射
                        if "cost_estimate" not in lines[i + 1]:
                            indent = len(line) - len(line.lstrip())
                            mapping_code = " " * indent + '''# 处理字段名不匹配问题
                        if "cost_estimate" in res and "cost" not in res:
                            res["cost"] = res["cost_estimate"]'''
                            lines.insert(i + 1, mapping_code)
                            break
                
                content = '\n'.join(lines)
                file_path.write_text(content, encoding='utf-8')
                self.fixes_applied.append("✅ 修复规则评估字段映射")
            else:
                self.fixes_applied.append("⏭️  规则评估字段已修复")
                
        except Exception as e:
            self.errors.append(f"❌ 修复规则评估字段失败: {str(e)}")
    
    def create_rule_templates(self):
        """创建规则模板文件"""
        file_path = self.project_root / "data" / "rule_templates.json"
        
        # 已在前面创建，这里只检查
        if file_path.exists():
            self.fixes_applied.append("✅ 规则模板文件已存在")
        else:
            self.errors.append("❌ 规则模板文件缺失")
    
    def fix_startup_scripts(self):
        """修复启动脚本权限"""
        scripts = [
            "start.sh",
            "start_enhanced.sh",
            "cleanup.sh",
            "game.sh"
        ]
        
        for script_name in scripts:
            script_path = self.project_root / script_name
            if script_path.exists():
                try:
                    # 设置可执行权限
                    os.chmod(script_path, 0o755)
                    self.fixes_applied.append(f"✅ 设置 {script_name} 可执行权限")
                except Exception as e:
                    self.errors.append(f"❌ 设置 {script_name} 权限失败: {str(e)}")
    
    def print_summary(self):
        """打印修复总结"""
        print("\n" + "="*50)
        print("🎯 修复总结")
        print("="*50)
        
        if self.fixes_applied:
            print("\n✅ 成功修复:")
            for fix in self.fixes_applied:
                print(f"  {fix}")
        
        if self.errors:
            print("\n❌ 修复失败:")
            for error in self.errors:
                print(f"  {error}")
        
        print(f"\n📊 统计: {len(self.fixes_applied)} 成功, {len(self.errors)} 失败")
        
        if not self.errors:
            print("\n🎉 所有修复已成功应用！")
            print("\n下一步:")
            print("1. 运行测试: pytest tests/")
            print("2. 启动CLI: python rulek.py cli")
            print("3. 启动Web: ./start_enhanced.sh")
        else:
            print("\n⚠️  部分修复失败，请手动检查")


def main():
    """主函数"""
    print("RuleK AI 集成修复工具 v1.0")
    print("-" * 50)
    
    # 检查是否在项目根目录
    if not Path("rulek.py").exists():
        print("❌ 请在 RuleK 项目根目录运行此脚本")
        sys.exit(1)
    
    # 创建修复器并执行
    fixer = RuleKFixer()
    fixer.fix_all()
    
    # 提示后续步骤
    print("\n" + "="*50)
    print("📋 后续步骤：")
    print("="*50)
    print("1. 检查 .env 文件，确保 DEEPSEEK_API_KEY 已设置")
    print("2. 运行测试验证修复: pytest tests/ -v")
    print("3. 测试CLI模式: python rulek.py cli --ai")
    print("4. 测试Web模式: ./start_enhanced.sh")
    print("\n💡 提示: 使用 --mock 参数可以在没有API Key的情况下测试")


if __name__ == "__main__":
    main()
