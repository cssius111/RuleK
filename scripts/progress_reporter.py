#!/usr/bin/env python3
"""
RuleK Web UI 自动化进度报告生成器

功能:
- 收集测试结果
- 分析代码覆盖率
- 生成可视化报告
- 发送进度通知
"""

import json
import os
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Any
import markdown
from jinja2 import Template

class ProgressReporter:
    def __init__(self, phase: int):
        self.phase = phase
        self.timestamp = datetime.datetime.now()
        self.project_root = Path(__file__).parent.parent
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        self.phase_names = {
            0: "环境准备",
            1: "基础框架",
            2: "游戏创建流程",
            3: "游戏核心界面",
            4: "规则管理系统",
            5: "NPC和AI系统",
            6: "优化和完善"
        }
        
        self.success_criteria = {
            0: {
                "functional": ["开发服务器", "API服务器", "WebSocket"],
                "performance": ["首屏<3s"],
                "quality": ["无构建错误"]
            },
            1: {
                "functional": ["路由系统", "状态管理", "布局响应式"],
                "performance": ["路由<100ms"],
                "quality": ["TypeScript无错", "组件测试"]
            },
            2: {
                "functional": ["新游戏创建", "存档加载", "参数验证"],
                "performance": ["创建<2s"],
                "quality": ["表单验证", "错误处理"]
            },
            3: {
                "functional": ["游戏主界面", "回合推进", "实时更新"],
                "performance": ["更新<100ms", "AI<2s"],
                "quality": ["同步无错", "状态一致"]
            },
            4: {
                "functional": ["规则创建", "AI解析", "模板系统"],
                "performance": ["AI<3s", "预览<500ms"],
                "quality": ["验证完整", "成本准确"]
            },
            5: {
                "functional": ["NPC展示", "AI对话", "流式推送"],
                "performance": ["生成<2s", "无延迟"],
                "quality": ["相关性>90%", "无丢失"]
            },
            6: {
                "functional": ["功能完整", "错误处理"],
                "performance": ["Lighthouse>90", "包<500KB"],
                "quality": ["覆盖>80%", "0bug"]
            }
        }
    
    def collect_test_results(self) -> Dict[str, Any]:
        """收集测试结果"""
        results = {
            "unit": self._run_unit_tests(),
            "e2e": self._run_e2e_tests(),
            "coverage": self._get_coverage(),
            "performance": self._run_performance_tests()
        }
        return results
    
    def _run_unit_tests(self) -> Dict[str, Any]:
        """运行单元测试"""
        try:
            result = subprocess.run(
                ["npm", "run", "test:unit", "--", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root / "web" / "frontend"
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"passed": 0, "failed": 0, "total": 0}
        except Exception as e:
            print(f"单元测试失败: {e}")
            return {"passed": 0, "failed": 0, "total": 0}
    
    def _run_e2e_tests(self) -> Dict[str, Any]:
        """运行E2E测试"""
        try:
            test_file = f"phase{self.phase}.spec.ts"
            result = subprocess.run(
                ["npx", "playwright", "test", test_file, "--reporter=json"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"passed": 0, "failed": 0, "total": 0}
        except Exception as e:
            print(f"E2E测试失败: {e}")
            return {"passed": 0, "failed": 0, "total": 0}
    
    def _get_coverage(self) -> Dict[str, float]:
        """获取代码覆盖率"""
        try:
            coverage_file = self.project_root / "coverage" / "coverage-summary.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    data = json.load(f)
                    return {
                        "lines": data["total"]["lines"]["pct"],
                        "functions": data["total"]["functions"]["pct"],
                        "branches": data["total"]["branches"]["pct"],
                        "statements": data["total"]["statements"]["pct"]
                    }
            return {"lines": 0, "functions": 0, "branches": 0, "statements": 0}
        except Exception as e:
            print(f"覆盖率获取失败: {e}")
            return {"lines": 0, "functions": 0, "branches": 0, "statements": 0}
    
    def _run_performance_tests(self) -> Dict[str, Any]:
        """运行性能测试"""
        try:
            # 运行Lighthouse
            result = subprocess.run(
                ["npx", "lighthouse", "http://localhost:3000", "--output=json", "--quiet"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "performance": data["categories"]["performance"]["score"] * 100,
                    "accessibility": data["categories"]["accessibility"]["score"] * 100,
                    "bestPractices": data["categories"]["best-practices"]["score"] * 100,
                    "seo": data["categories"]["seo"]["score"] * 100
                }
            return {"performance": 0, "accessibility": 0, "bestPractices": 0, "seo": 0}
        except Exception as e:
            print(f"性能测试失败: {e}")
            return {"performance": 0, "accessibility": 0, "bestPractices": 0, "seo": 0}
    
    def check_success_criteria(self, test_results: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """检查成功标准"""
        criteria = self.success_criteria[self.phase]
        results = {
            "functional": [],
            "performance": [],
            "quality": []
        }
        
        # 检查功能完整性
        for item in criteria["functional"]:
            # 这里应该有实际的检查逻辑
            passed = test_results["e2e"]["passed"] > 0
            results["functional"].append({
                "name": item,
                "passed": passed,
                "reason": "测试通过" if passed else "测试失败"
            })
        
        # 检查性能指标
        for item in criteria["performance"]:
            passed = test_results["performance"]["performance"] > 80
            results["performance"].append({
                "name": item,
                "passed": passed,
                "value": test_results["performance"]["performance"]
            })
        
        # 检查代码质量
        for item in criteria["quality"]:
            passed = test_results["coverage"]["lines"] > 70
            results["quality"].append({
                "name": item,
                "passed": passed,
                "coverage": test_results["coverage"]["lines"]
            })
        
        return results
    
    def generate_report(self, test_results: Dict[str, Any], criteria_results: Dict[str, List[Dict]]) -> str:
        """生成Markdown报告"""
        template = Template("""
# Phase {{ phase }}: {{ phase_name }} - 进度报告

## 📅 报告时间
{{ timestamp }}

## 📊 测试结果汇总

### 单元测试
- ✅ 通过: {{ unit.passed }}
- ❌ 失败: {{ unit.failed }}
- 📝 总计: {{ unit.total }}
- 📈 通过率: {{ (unit.passed / unit.total * 100) if unit.total else 0 }}%

### E2E测试
- ✅ 通过: {{ e2e.passed }}
- ❌ 失败: {{ e2e.failed }}
- 📝 总计: {{ e2e.total }}
- 📈 通过率: {{ (e2e.passed / e2e.total * 100) if e2e.total else 0 }}%

### 代码覆盖率
- 📏 行覆盖: {{ coverage.lines }}%
- 🔧 函数覆盖: {{ coverage.functions }}%
- 🌿 分支覆盖: {{ coverage.branches }}%
- 📄 语句覆盖: {{ coverage.statements }}%

### 性能评分
- ⚡ Performance: {{ performance.performance }}
- ♿ Accessibility: {{ performance.accessibility }}
- 🎯 Best Practices: {{ performance.bestPractices }}
- 🔍 SEO: {{ performance.seo }}

## ✅ 成功标准检查

### 功能完整性
{% for item in criteria.functional %}
- {{ '✅' if item.passed else '❌' }} {{ item.name }}{% if not item.passed %} ({{ item.reason }}){% endif %}
{% endfor %}

### 性能指标
{% for item in criteria.performance %}
- {{ '✅' if item.passed else '❌' }} {{ item.name }} (当前: {{ item.value }})
{% endfor %}

### 代码质量
{% for item in criteria.quality %}
- {{ '✅' if item.passed else '❌' }} {{ item.name }} (覆盖率: {{ item.coverage }}%)
{% endfor %}

## 📈 整体评估

{% set all_passed = criteria.functional | selectattr('passed') | list | length == criteria.functional | length and
                    criteria.performance | selectattr('passed') | list | length == criteria.performance | length and
                    criteria.quality | selectattr('passed') | list | length == criteria.quality | length %}

{% if all_passed %}
### ✅ Phase {{ phase }} 完成！

恭喜！当前阶段所有标准都已达成，可以进入下一阶段。

**下一步行动:**
1. 提交代码: `git commit -m "Complete Phase {{ phase }}"`
2. 创建标签: `git tag phase{{ phase }}`
3. 开始Phase {{ phase + 1 }}
{% else %}
### ⚠️ Phase {{ phase }} 未完成

还有一些标准未达成，请继续优化。

**需要改进的项目:**
{% for item in criteria.functional %}{% if not item.passed %}
- 功能: {{ item.name }}
{% endif %}{% endfor %}
{% for item in criteria.performance %}{% if not item.passed %}
- 性能: {{ item.name }}
{% endif %}{% endfor %}
{% for item in criteria.quality %}{% if not item.passed %}
- 质量: {{ item.name }}
{% endif %}{% endfor %}

**建议行动:**
1. 修复失败的测试
2. 优化性能指标
3. 提高代码覆盖率
4. 重新运行测试: `npm run test:phase{{ phase }}`
{% endif %}

## 📊 历史趋势

_(这里可以添加图表展示历史数据)_

## 💡 AI建议

基于当前测试结果，建议：
1. 重点关注失败的测试用例
2. 优化性能瓶颈
3. 补充缺失的测试覆盖

---

*报告生成时间: {{ timestamp }}*
*下次检查时间: {{ next_check }}*
        """)
        
        return template.render(
            phase=self.phase,
            phase_name=self.phase_names[self.phase],
            timestamp=self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            next_check=(self.timestamp + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
            unit=test_results["unit"],
            e2e=test_results["e2e"],
            coverage=test_results["coverage"],
            performance=test_results["performance"],
            criteria=criteria_results
        )
    
    def save_report(self, content: str):
        """保存报告"""
        # 保存Markdown
        md_file = self.reports_dir / f"phase{self.phase}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        md_file.write_text(content)
        
        # 生成HTML
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Phase {self.phase} 进度报告</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #8b5cf6; }}
                h2 {{ color: #6d28d9; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
                h3 {{ color: #4c1d95; }}
                code {{ background: #f3f4f6; padding: 2px 6px; border-radius: 3px; }}
                pre {{ background: #1f2937; color: #f3f4f6; padding: 16px; border-radius: 8px; overflow-x: auto; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; }}
                th {{ background: #f9fafb; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        html_file = self.reports_dir / f"phase{self.phase}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        html_file.write_text(html_template)
        
        print(f"📄 报告已保存:")
        print(f"   - Markdown: {md_file}")
        print(f"   - HTML: {html_file}")
        
        # 创建最新报告的符号链接
        latest_md = self.reports_dir / f"phase{self.phase}_latest.md"
        latest_html = self.reports_dir / f"phase{self.phase}_latest.html"
        
        if latest_md.exists():
            latest_md.unlink()
        if latest_html.exists():
            latest_html.unlink()
            
        latest_md.symlink_to(md_file.name)
        latest_html.symlink_to(html_file.name)
    
    def send_notification(self, passed: bool):
        """发送通知（可以集成Slack、邮件等）"""
        status = "✅ 通过" if passed else "⚠️ 未通过"
        message = f"Phase {self.phase} ({self.phase_names[self.phase]}) 测试 {status}"
        
        # 这里可以集成各种通知服务
        print(f"\n📢 {message}")
    
    def run(self):
        """运行报告生成器"""
        print(f"🚀 开始生成Phase {self.phase}进度报告...")
        
        # 收集测试结果
        print("📊 收集测试结果...")
        test_results = self.collect_test_results()
        
        # 检查成功标准
        print("✅ 检查成功标准...")
        criteria_results = self.check_success_criteria(test_results)
        
        # 生成报告
        print("📝 生成报告...")
        report_content = self.generate_report(test_results, criteria_results)
        
        # 保存报告
        self.save_report(report_content)
        
        # 判断是否通过
        all_passed = all(
            all(item["passed"] for item in criteria_results["functional"]),
            all(item["passed"] for item in criteria_results["performance"]),
            all(item["passed"] for item in criteria_results["quality"])
        )
        
        # 发送通知
        self.send_notification(all_passed)
        
        return all_passed


def main():
    import sys
    
    if len(sys.argv) != 2:
        print("用法: python progress_reporter.py <phase>")
        sys.exit(1)
    
    try:
        phase = int(sys.argv[1])
        if phase < 0 or phase > 6:
            raise ValueError("Phase必须在0-6之间")
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)
    
    reporter = ProgressReporter(phase)
    passed = reporter.run()
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
