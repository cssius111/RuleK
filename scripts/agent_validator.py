#!/usr/bin/env python3
"""
Agent规则验证器
确保AI操作遵循所有Agent规则
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

class AgentValidator:
    """Agent规则验证器"""
    
    def __init__(self, project_root: Path = None):
        self.root = Path(project_root or os.getcwd())
        self.agents = self._load_agents()
        self.violations = []
        
    def _load_agents(self) -> Dict[str, Path]:
        """加载所有Agent文件"""
        agents = {
            'main': self.root / 'MAIN_AGENT.md',
            'docs': self.root / 'docs' / '.DOCS_AGENT.md',
            'scripts': self.root / 'scripts' / '.SCRIPTS_AGENT.md',
            'backend': self.root / 'web' / 'backend' / '.BACKEND_AGENT.md',
            'frontend': self.root / 'web' / 'frontend' / '.FRONTEND_AGENT.md',
            'tests': self.root / 'tests' / '.TEST_AGENT.md',
            'src': self.root / 'src' / '.SRC_AGENT.md',
        }
        return {k: v for k, v in agents.items() if v.exists()}
    
    def validate_file_operation(self, operation: str, file_path: str) -> Tuple[bool, str]:
        """
        验证文件操作是否符合规则
        
        Args:
            operation: 'create', 'modify', 'delete'
            file_path: 文件路径
            
        Returns:
            (是否合规, 原因说明)
        """
        path = Path(file_path)
        
        # 规则1: 不在根目录创建代码文件
        if operation == 'create' and path.parent == self.root:
            if path.suffix in ['.py', '.js', '.ts', '.vue']:
                if path.name not in ['rulek.py', 'setup.py', 'manage.py']:
                    return False, f"❌ 不要在根目录创建 {path.name}，应该放在对应子目录"
        
        # 规则2: 不创建enhanced/new/fixed版本
        if operation == 'create':
            bad_suffixes = ['_enhanced', '_new', '_fixed', '_v2', '_updated', '_modified']
            name_without_ext = path.stem
            for suffix in bad_suffixes:
                if name_without_ext.endswith(suffix):
                    original = name_without_ext.replace(suffix, '') + path.suffix
                    return False, f"❌ 不要创建 {path.name}，应该直接修改 {original}"
        
        # 规则3: 文件应该在正确的目录
        if operation == 'create':
            rules = {
                'test_': 'tests/',
                'fix_': 'scripts/fix/',
                'diagnose_': 'scripts/diagnostic/',
            }
            for prefix, correct_dir in rules.items():
                if path.name.startswith(prefix) and not str(path).startswith(str(self.root / correct_dir)):
                    return False, f"❌ {path.name} 应该放在 {correct_dir} 目录"
        
        # 规则4: 优先修改而不是创建
        if operation == 'create' and path.exists():
            return False, f"❌ {path.name} 已存在，应该使用 edit_file 修改而不是覆盖"
            
        return True, "✅ 操作符合规则"
    
    def suggest_correct_path(self, file_name: str) -> str:
        """建议正确的文件路径"""
        suggestions = {
            'test_': 'tests/unit/',
            'fix_': 'scripts/fix/',
            'diagnose_': 'scripts/diagnostic/',
            'integrate_': 'scripts/dev/',
            '.vue': 'web/frontend/src/components/',
            '_service.py': 'web/backend/services/',
            '_routes.py': 'web/backend/api/',
        }
        
        for pattern, directory in suggestions.items():
            if pattern in file_name:
                return str(self.root / directory / file_name)
                
        # 默认建议
        if file_name.endswith('.py'):
            return str(self.root / 'src' / 'utils' / file_name)
        elif file_name.endswith('.md'):
            return str(self.root / 'docs' / file_name)
        else:
            return str(self.root / 'scripts' / 'temp' / file_name)
    
    def get_agent_for_path(self, file_path: str) -> Optional[str]:
        """获取路径对应的Agent"""
        path = Path(file_path)
        
        if 'docs' in path.parts:
            return 'docs'
        elif 'scripts' in path.parts:
            return 'scripts'
        elif 'web/backend' in str(path):
            return 'backend'
        elif 'web/frontend' in str(path):
            return 'frontend'
        elif 'tests' in path.parts:
            return 'tests'
        elif 'src' in path.parts:
            return 'src'
        else:
            return 'main'
    
    def check_naming_convention(self, file_path: str) -> Tuple[bool, str]:
        """检查命名规范"""
        path = Path(file_path)
        name = path.stem
        
        # Python文件命名
        if path.suffix == '.py':
            if name != name.lower():
                return False, f"❌ Python文件应该使用小写: {name.lower()}.py"
            if '-' in name:
                return False, f"❌ 使用下划线而不是连字符: {name.replace('-', '_')}.py"
                
        # Vue组件命名
        if path.suffix == '.vue' and 'components' in str(path):
            if name[0].islower():
                return False, f"❌ Vue组件应该使用PascalCase: {name[0].upper() + name[1:]}.vue"
                
        return True, "✅ 命名符合规范"
    
    def generate_agent_context(self, task_type: str) -> str:
        """生成AI需要的Agent上下文"""
        context = []
        
        # 加载主Agent
        if 'main' in self.agents:
            context.append(f"=== 主Agent规则 ===\n{self.agents['main'].read_text()}\n")
        
        # 加载相关子Agent
        if task_type in self.agents:
            context.append(f"=== {task_type.upper()} Agent规则 ===\n{self.agents[task_type].read_text()}\n")
            
        return "\n".join(context)
    
    def validate_ai_plan(self, plan: List[Dict]) -> List[Dict]:
        """
        验证AI的操作计划
        
        Args:
            plan: AI的操作计划列表
            [
                {"action": "read_file", "path": "xxx"},
                {"action": "edit_file", "path": "xxx", "changes": []},
                {"action": "write_file", "path": "xxx", "content": "xxx"}
            ]
        """
        results = []
        
        for step in plan:
            action = step.get('action')
            path = step.get('path')
            
            if action == 'write_file':
                # 检查是否应该用edit_file
                if Path(path).exists():
                    results.append({
                        'step': step,
                        'valid': False,
                        'reason': f'文件已存在，应该使用 edit_file 而不是 write_file',
                        'suggestion': {'action': 'edit_file', 'path': path}
                    })
                else:
                    # 验证创建操作
                    valid, reason = self.validate_file_operation('create', path)
                    results.append({
                        'step': step,
                        'valid': valid,
                        'reason': reason,
                        'suggestion': {'path': self.suggest_correct_path(Path(path).name)} if not valid else None
                    })
                    
            elif action == 'edit_file':
                valid, reason = self.validate_file_operation('modify', path)
                results.append({
                    'step': step,
                    'valid': valid,
                    'reason': reason
                })
                
        return results


def main():
    """主函数 - 用于测试验证器"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent规则验证器")
    parser.add_argument('--check', help="检查文件操作 (create/modify/delete)")
    parser.add_argument('--path', help="文件路径")
    parser.add_argument('--context', help="生成Agent上下文 (docs/scripts/backend/frontend/tests/src)")
    parser.add_argument('--validate-plan', help="验证操作计划JSON文件")
    
    args = parser.parse_args()
    
    validator = AgentValidator()
    
    if args.check and args.path:
        # 验证单个操作
        valid, reason = validator.validate_file_operation(args.check, args.path)
        print(reason)
        
        if not valid:
            # 建议正确路径
            suggested = validator.suggest_correct_path(Path(args.path).name)
            print(f"💡 建议路径: {suggested}")
            
            # 检查命名
            name_valid, name_reason = validator.check_naming_convention(args.path)
            if not name_valid:
                print(name_reason)
                
    elif args.context:
        # 生成Agent上下文
        context = validator.generate_agent_context(args.context)
        print(context)
        
    elif args.validate_plan:
        # 验证操作计划
        with open(args.validate_plan) as f:
            plan = json.load(f)
        
        results = validator.validate_ai_plan(plan)
        
        print("=== AI操作计划验证 ===\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['step']['action']} -> {result['step']['path']}")
            print(f"   {result['reason']}")
            if result.get('suggestion'):
                print(f"   💡 建议: {result['suggestion']}")
            print()
    else:
        # 显示所有已加载的Agent
        print("=== 已加载的Agent规则 ===\n")
        for name, path in validator.agents.items():
            print(f"✅ {name:10} -> {path.relative_to(validator.root)}")
        
        print("\n使用方法:")
        print("  检查操作: python agent_validator.py --check create --path /test.py")
        print("  生成上下文: python agent_validator.py --context backend")
        print("  验证计划: python agent_validator.py --validate-plan plan.json")


if __name__ == "__main__":
    main()
