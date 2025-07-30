#!/usr/bin/env python3
"""
import datetime
RuleK 自动化测试和修复工具
智能运行测试并自动修复常见问题
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import ast
import shutil

class AutoTestFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.test_results = {}
        self.fixes_applied = []
        self.known_issues = {
            "self.game_mgr.rules": "self.game_mgr.rules",
            "list(self.game_mgr.state.locations.keys())": "list(list(self.game_mgr.state.locations.keys()).keys())",
            "@field_validator": "@field_validator",
            "model_config = ConfigDict(": "model_config = ConfigDict(",
            "json_schema_extra": "json_json_schema_extra",
            ".model_validate(": ".model_validate(",
            ".model_dump()": ".model_dump()",
            "current_turn": "current_turn"
        }
        
    def run_smart_tests(self):
        """智能运行测试并修复"""
        print("🔧 RuleK 自动化测试和修复工具")
        print("=" * 50)
        
        # 1. 先运行诊断
        self.run_diagnosis()
        
        # 2. 尝试自动修复已知问题
        self.auto_fix_known_issues()
        
        # 3. 运行测试并收集结果
        self.run_tests_with_analysis()
        
        # 4. 分析失败并尝试修复
        self.analyze_and_fix_failures()
        
        # 5. 生成报告
        self.generate_test_report()
        
    def run_diagnosis(self):
        """运行基础诊断"""
        print("\n📊 运行基础诊断...")
        
        # 确保PYTHONPATH正确
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
            
        # 检查pytest
        try:
            import pytest
            print("✅ pytest已安装")
        except ImportError:
            print("❌ pytest未安装，正在安装...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio", "pytest-mock"])
            
    def auto_fix_known_issues(self):
        """自动修复已知问题"""
        print("\n🔨 扫描并修复已知问题...")
        
        # 扫描Python文件
        for py_file in self.project_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                original_content = content
                fixed = False
                
                # 应用已知修复
                for old_pattern, new_pattern in self.known_issues.items():
                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern)
                        fixed = True
                        
                if fixed:
                    # 备份原文件
                    backup_file = py_file.with_suffix('.py.backup')
                    shutil.copy2(py_file, backup_file)
                    
                    # 写入修复后的内容
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                    self.fixes_applied.append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "fixes": "应用了已知问题修复"
                    })
                    print(f"  ✅ 修复了: {py_file.relative_to(self.project_root)}")
                    
            except Exception as e:
                print(f"  ⚠️  处理{py_file}时出错: {e}")
                
    def run_tests_with_analysis(self):
        """运行测试并分析结果"""
        print("\n🧪 运行测试套件...")
        
        # 设置环境变量
        env = os.environ.copy()
        env['PYTEST_RUNNING'] = '1'
        env['PYTHONPATH'] = str(self.project_root)
        
        # 运行pytest并捕获输出
        cmd = [
            sys.executable, "-m", "pytest",
            "-v", "--tb=short", "--no-header",
            "-W", "ignore::DeprecationWarning",
            "--json-report", "--json-report-file=test_report.json"
        ]
        
        # 先检查是否有pytest-json-report插件
        try:
            import pytest_json_report
        except ImportError:
            print("  安装pytest-json-report插件...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pytest-json-report"])
            cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short", "--no-header", "-W", "ignore::DeprecationWarning"]
            
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        # 解析测试结果
        self.parse_test_output(result.stdout, result.stderr)
        
        # 如果有JSON报告，也解析它
        json_report = self.project_root / "test_report.json"
        if json_report.exists():
            try:
                with open(json_report, 'r') as f:
                    report_data = json.load(f)
                    self.test_results['summary'] = report_data.get('summary', {})
            except Exception:
                pass
                
    def parse_test_output(self, stdout: str, stderr: str):
        """解析测试输出"""
        # 解析失败的测试
        failures = []
        
        # 查找失败的测试
        failure_pattern = r'FAILED (.+?) - (.+)'
        for match in re.finditer(failure_pattern, stdout):
            test_name = match.group(1)
            error_msg = match.group(2)
            failures.append({
                "test": test_name,
                "error": error_msg,
                "type": self.classify_error(error_msg)
            })
            
        self.test_results['failures'] = failures
        
        # 统计信息
        summary_pattern = r'(\d+) passed.*?(\d+) failed'
        summary_match = re.search(summary_pattern, stdout)
        if summary_match:
            self.test_results['passed'] = int(summary_match.group(1))
            self.test_results['failed'] = int(summary_match.group(2))
        else:
            self.test_results['passed'] = 0
            self.test_results['failed'] = len(failures)
            
    def classify_error(self, error_msg: str) -> str:
        """分类错误类型"""
        if "ImportError" in error_msg or "ModuleNotFoundError" in error_msg:
            return "import"
        elif "AttributeError" in error_msg:
            return "attribute"
        elif "TypeError" in error_msg:
            return "type"
        elif "AssertionError" in error_msg:
            return "assertion"
        elif "FileNotFoundError" in error_msg:
            return "file"
        else:
            return "other"
            
    def analyze_and_fix_failures(self):
        """分析失败并尝试修复"""
        print("\n🔍 分析测试失败...")
        
        if not self.test_results.get('failures'):
            print("✅ 所有测试通过！")
            return
            
        # 按错误类型分组
        error_groups = {}
        for failure in self.test_results['failures']:
            error_type = failure['type']
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(failure)
            
        # 尝试修复不同类型的错误
        for error_type, failures in error_groups.items():
            print(f"\n处理{error_type}类型错误 ({len(failures)}个):")
            
            if error_type == "import":
                self.fix_import_errors(failures)
            elif error_type == "attribute":
                self.fix_attribute_errors(failures)
            elif error_type == "file":
                self.fix_file_errors(failures)
                
    def fix_import_errors(self, failures: List[Dict]):
        """修复导入错误"""
        for failure in failures:
            error_msg = failure['error']
            
            # 提取缺失的模块
            match = re.search(r"No module named '(.+?)'", error_msg)
            if match:
                module_name = match.group(1)
                print(f"  缺失模块: {module_name}")
                
                # 检查是否是拼写错误
                if "deepseek_client" in module_name and "utils" in module_name:
                    print("    → 可能是导入路径错误，应该是 src.api.deepseek_client")
                    
    def fix_attribute_errors(self, failures: List[Dict]):
        """修复属性错误"""
        for failure in failures:
            error_msg = failure['error']
            
            # 提取属性错误信息
            match = re.search(r"'(.+?)' object has no attribute '(.+?)'", error_msg)
            if match:
                obj_type = match.group(1)
                attr_name = match.group(2)
                print(f"  {obj_type} 缺少属性: {attr_name}")
                
                # 提供修复建议
                if obj_type == "GameState" and attr_name == "rules":
                    print("    → 使用 game_mgr.rules 而不是 game_mgr.state.rules")
                    
    def fix_file_errors(self, failures: List[Dict]):
        """修复文件错误"""
        for failure in failures:
            error_msg = failure['error']
            print(f"  文件相关错误: {error_msg[:100]}...")
            
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 50)
        print("📊 测试报告")
        print("=" * 50)
        
        # 显示统计
        passed = self.test_results.get('passed', 0)
        failed = self.test_results.get('failed', 0)
        total = passed + failed
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"\n测试统计:")
            print(f"  总计: {total}")
            print(f"  通过: {passed} ✅")
            print(f"  失败: {failed} ❌")
            print(f"  成功率: {success_rate:.1f}%")
            
        # 显示应用的修复
        if self.fixes_applied:
            print(f"\n应用的修复 ({len(self.fixes_applied)}个):")
            for fix in self.fixes_applied[:5]:  # 只显示前5个
                print(f"  - {fix['file']}: {fix['fixes']}")
            if len(self.fixes_applied) > 5:
                print(f"  ... 还有{len(self.fixes_applied) - 5}个修复")
                
        # 保存详细报告
        self.save_detailed_report()
        
    def save_detailed_report(self):
        """保存详细报告"""
        report_file = self.project_root / "test_fix_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# RuleK 测试修复报告\n\n")
            f.write(f"生成时间: {datetime.datetime.now()}\n\n")
            
            # 测试统计
            f.write("## 测试统计\n\n")
            passed = self.test_results.get('passed', 0)
            failed = self.test_results.get('failed', 0)
            f.write(f"- 通过: {passed}\n")
            f.write(f"- 失败: {failed}\n")
            f.write(f"- 总计: {passed + failed}\n\n")
            
            # 失败的测试
            if self.test_results.get('failures'):
                f.write("## 失败的测试\n\n")
                for i, failure in enumerate(self.test_results['failures'], 1):
                    f.write(f"### {i}. {failure['test']}\n")
                    f.write(f"**错误类型**: {failure['type']}\n")
                    f.write(f"**错误信息**: {failure['error']}\n\n")
                    
            # 应用的修复
            if self.fixes_applied:
                f.write("## 应用的修复\n\n")
                for fix in self.fixes_applied:
                    f.write(f"- **{fix['file']}**: {fix['fixes']}\n")
                    
        print(f"\n详细报告已保存到: test_fix_report.md")

if __name__ == "__main__":
    fixer = AutoTestFixer()
    fixer.run_smart_tests()
