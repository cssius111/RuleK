#!/usr/bin/env python3
"""
RuleK CLI 测试运行器和修复助手
自动运行测试、分析失败、提供修复建议
"""
import subprocess
import sys
import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class CLITestRunner:
    """CLI测试运行器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = []
        self.failed_tests = []
        self.error_patterns = {
            "AttributeError.*turn_count": "使用了错误的属性名 turn_count（应该是 current_turn）",
            "AttributeError.*state.rules": "使用了 state.rules（应该是 game_manager.rules）",
            "ModuleNotFoundError": "模块导入错误，检查路径设置",
            "TypeError.*missing.*argument": "函数调用缺少必要参数",
            "TypeError.*non-default argument.*follows default": "dataclass字段顺序错误，无默认值字段必须在有默认值字段之前",
            "KeyError": "字典键不存在",
            "ValueError": "值错误，检查数据验证",
            "AssertionError": "断言失败，检查测试逻辑",
        }
        
    def setup_environment(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")
        
        # 设置环境变量
        os.environ['PYTEST_RUNNING'] = '1'
        os.environ['PYTHONPATH'] = str(self.project_root)
        
        # 创建必要目录
        dirs = ['test_results', 'htmlcov', 'logs', 'data/saves']
        for dir_path in dirs:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
            
        print("  ✓ 环境设置完成")
        
    def run_tests(self, test_file: str = "tests/cli/test_cli_game.py") -> int:
        """运行测试并收集结果"""
        print(f"\n🧪 运行测试: {test_file}")
        print("=" * 60)
        
        # 基本命令
        cmd = [
            sys.executable, '-m', 'pytest',
            test_file,
            '-v',
            '--tb=short',
            '-x'  # 在第一个失败时停止
        ]
        
        # 尝试添加json报告（如果插件存在）
        try:
            import pytest_json_report
            cmd.extend([
                '--json-report',
                '--json-report-file=test_results/cli_test_report.json'
            ])
        except ImportError:
            pass
        
        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        # 解析结果
        self._parse_results(result)
        
        return result.returncode
        
    def _parse_results(self, result):
        """解析测试结果"""
        # 尝试加载JSON报告
        json_report = self.project_root / "test_results/cli_test_report.json"
        if json_report.exists():
            try:
                with open(json_report) as f:
                    report = json.load(f)
                    self.test_results = report.get('tests', [])
                    self.failed_tests = [
                        t for t in self.test_results 
                        if t.get('outcome') == 'failed'
                    ]
            except:
                pass
        
        # 从stdout和stderr解析
        if not self.failed_tests:
            output = result.stdout + "\n" + result.stderr
            
            # 解析失败信息
            failed_pattern = r"FAILED (.*?) - (.*)"
            for match in re.finditer(failed_pattern, output):
                self.failed_tests.append({
                    'nodeid': match.group(1),
                    'call': {'longrepr': match.group(2)}
                })
            
            # 解析错误信息
            error_pattern = r"ERROR (.*?) - (.*)"
            for match in re.finditer(error_pattern, output):
                self.failed_tests.append({
                    'nodeid': match.group(1),
                    'call': {'longrepr': match.group(2)}
                })
            
            # 如果有stderr但没有解析到具体失败，添加通用失败
            if result.returncode != 0 and not self.failed_tests and result.stderr:
                self.failed_tests.append({
                    'nodeid': 'collection',
                    'call': {'longrepr': result.stderr[:500]}
                })
                
    def analyze_failures(self) -> List[Dict]:
        """分析失败的测试"""
        print("\n🔍 分析测试失败...")
        
        analysis = []
        for test in self.failed_tests:
            test_name = test.get('nodeid', 'Unknown')
            error_msg = str(test.get('call', {}).get('longrepr', ''))
            
            # 匹配错误模式
            suggestions = []
            for pattern, suggestion in self.error_patterns.items():
                if re.search(pattern, error_msg):
                    suggestions.append(suggestion)
            
            analysis.append({
                'test': test_name,
                'error': error_msg[:200] + '...' if len(error_msg) > 200 else error_msg,
                'suggestions': suggestions or ['检查测试代码和实现的一致性']
            })
            
        return analysis
        
    def suggest_fixes(self, analysis: List[Dict]):
        """提供修复建议"""
        print("\n💡 修复建议：")
        print("=" * 60)
        
        for i, item in enumerate(analysis, 1):
            print(f"\n{i}. 测试: {item['test']}")
            print(f"   错误: {item['error']}")
            print("   建议:")
            for suggestion in item['suggestions']:
                print(f"   - {suggestion}")
                
    def generate_fix_script(self, analysis: List[Dict]):
        """生成修复脚本"""
        fixes = []
        
        # 收集所有需要的修复
        for item in analysis:
            error = item['error']
            if 'turn_count' in error:
                fixes.append({
                    'file': 'src/cli_game.py',
                    'pattern': r'\.turn_count\b',
                    'replacement': '.current_turn',
                    'description': '修复 turn_count -> current_turn'
                })
            if 'state.rules' in error:
                fixes.append({
                    'file': 'src/cli_game.py',
                    'pattern': r'\.state\.rules\b',
                    'replacement': '.rules',
                    'description': '修复 state.rules -> rules'
                })
                
        if fixes:
            self._write_fix_script(fixes)
            
    def _write_fix_script(self, fixes: List[Dict]):
        """写入修复脚本"""
        script_path = self.project_root / "auto_fix_cli.py"
        
        script_content = '''#!/usr/bin/env python3
"""自动修复CLI测试问题"""
import re
from pathlib import Path

fixes = %s

def apply_fixes():
    for fix in fixes:
        file_path = Path(fix['file'])
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            original = content
            content = re.sub(fix['pattern'], fix['replacement'], content)
            
            if content != original:
                file_path.write_text(content, encoding='utf-8')
                print(f"✓ {fix['description']}")
            else:
                print(f"- {fix['description']} (无需修改)")

if __name__ == "__main__":
    print("应用自动修复...")
    apply_fixes()
    print("\\n完成！请重新运行测试。")
''' % repr(fixes)
        
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        print(f"\n📝 生成了自动修复脚本: {script_path}")
        print("   运行: python auto_fix_cli.py")
        
    def run_cycle(self, max_iterations: int = 5):
        """运行测试-修复循环"""
        print("🔄 开始测试-修复循环")
        print("=" * 60)
        
        for i in range(max_iterations):
            print(f"\n📍 第 {i+1}/{max_iterations} 轮")
            
            # 运行测试
            exit_code = self.run_tests()
            
            if exit_code == 0:
                print("\n✅ 所有测试通过！")
                self._generate_report()
                return True
                
            # 分析失败
            analysis = self.analyze_failures()
            
            if not analysis:
                print("\n❌ 测试失败但无法分析原因")
                return False
                
            # 提供建议
            self.suggest_fixes(analysis)
            
            # 生成修复脚本
            self.generate_fix_script(analysis)
            
            # 等待用户确认
            if i < max_iterations - 1:
                response = input("\n是否应用自动修复并继续？(y/n): ")
                if response.lower() != 'y':
                    break
                    
                # 应用修复
                subprocess.run([sys.executable, "auto_fix_cli.py"], cwd=self.project_root)
                
        print("\n❌ 达到最大迭代次数，仍有测试失败")
        return False
        
    def _generate_report(self):
        """生成测试报告"""
        report_path = self.project_root / "test_results/cli_test_summary.txt"
        
        report = f"""
RuleK CLI 测试报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 60}

测试统计:
- 总测试数: {len(self.test_results)}
- 通过: {len([t for t in self.test_results if t.get('outcome') == 'passed'])}
- 失败: {len(self.failed_tests)}
- 跳过: {len([t for t in self.test_results if t.get('outcome') == 'skipped'])}

状态: {'✅ 全部通过' if not self.failed_tests else '❌ 有失败'}
"""
        
        report_path.write_text(report)
        print(f"\n📊 测试报告已保存: {report_path}")


def main():
    """主函数"""
    runner = CLITestRunner()
    
    # 设置环境
    runner.setup_environment()
    
    # 运行测试循环
    success = runner.run_cycle()
    
    if success:
        print("\n🎉 恭喜！CLI测试全部通过！")
        print("\n下一步：")
        print("1. 运行扩展测试: pytest tests/cli/test_cli_game_extended.py")
        print("2. 查看覆盖率报告: open htmlcov/index.html")
        print("3. 集成到CI/CD流程")
    else:
        print("\n⚠️  仍有测试需要手动修复")
        print("请查看错误详情并手动修复")
        
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
