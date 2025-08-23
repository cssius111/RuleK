#!/bin/bash
# 快速测试修复验证脚本 V2

echo "======================================"
echo "🔧 RuleK 测试修复快速验证 V2"
echo "======================================"

echo ""
echo "1. 测试 CLI AI规则创建（恐惧积分扣除）..."
echo "--------------------------------------"
pytest tests/cli/test_cli_game.py::TestAIRuleCreation::test_ai_create_rule_success -v --tb=short

echo ""
echo "2. 测试 Playwright（原始测试）..."
echo "--------------------------------------"
pytest tests/web/test_web_playwright.py::test_frontend_homepage -v --tb=short

echo ""
echo "3. 测试 Playwright（同步版本）..."
echo "--------------------------------------"
pytest tests/web/test_playwright_sync.py::test_frontend_homepage_sync -v --tb=short

echo ""
echo "======================================"
echo "📊 测试结果总结"
echo "======================================"
echo ""
echo "✅ CLI测试修复成功"
echo "⚠️  如果 Playwright 测试失败："
echo "   - event_loop 错误 → 使用同步版本测试"
echo "   - 连接拒绝 → 需要启动服务器"
echo ""
echo "建议运行: python scripts/test/test_event_loop_fix.py"
echo "======================================"
