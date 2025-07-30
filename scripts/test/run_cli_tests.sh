#!/bin/bash
# run_cli_tests.sh - 更新版

echo "🧪 运行 CLI 测试..."
echo "=========================="

# 设置测试环境变量
export PYTEST_RUNNING=1
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 创建测试结果目录
mkdir -p test_results

# 运行测试（简化版，不依赖额外插件）
pytest tests/cli/test_cli_game.py \
    -v \
    --tb=short \
    --maxfail=5 \
    --cov=src.cli_game \
    --cov-report=html:htmlcov/cli \
    --cov-report=term

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 所有测试通过！"
    echo ""
    echo "📊 覆盖率报告: htmlcov/cli/index.html"
else
    echo ""
    echo "❌ 有测试失败，请查看上面的错误信息"
fi
