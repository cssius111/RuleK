#!/bin/bash
# RuleK CLI 测试验证脚本

echo "🧪 RuleK CLI 测试验证"
echo "===================="

# 检查Python环境
echo "📍 检查环境..."
python --version
pytest --version

# 清理旧的测试缓存
echo "🧹 清理测试缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

# 运行CLI测试
echo "🏃 运行CLI测试..."
PYTEST_RUNNING=1 pytest tests/cli/test_cli_game.py -v --tb=short

# 检查测试结果
if [ $? -eq 0 ]; then
    echo "✅ 所有测试通过！"
    
    # 运行单个失败的测试以调试
    echo "🔍 运行之前失败的测试..."
    PYTEST_RUNNING=1 pytest tests/cli/test_cli_game.py::TestRuleManagement::test_create_rule_from_template_success -v
    PYTEST_RUNNING=1 pytest tests/cli/test_cli_game.py::TestSaveLoad::test_save_game_success -v
    
else
    echo "❌ 有测试失败"
    
    # 生成详细报告
    echo "📊 生成详细测试报告..."
    PYTEST_RUNNING=1 pytest tests/cli/test_cli_game.py -v --tb=long --capture=no > test_report.txt 2>&1
    echo "报告已保存到 test_report.txt"
fi

echo "===================="
echo "测试完成"
