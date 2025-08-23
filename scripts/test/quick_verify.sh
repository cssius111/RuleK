#!/bin/bash
# 快速测试修复验证脚本

echo "======================================"
echo "🔧 RuleK 测试修复快速验证"
echo "======================================"

echo ""
echo "1. 测试 CLI AI规则创建（恐惧积分扣除）..."
echo "--------------------------------------"
pytest tests/cli/test_cli_game.py::TestAIRuleCreation::test_ai_create_rule_success -v --tb=short

echo ""
echo "2. 测试 Playwright（event_loop 修复）..."
echo "--------------------------------------"
pytest tests/web/test_web_playwright.py::test_frontend_homepage -v --tb=short

echo ""
echo "======================================"
echo "✅ 测试验证完成"
echo "======================================"
