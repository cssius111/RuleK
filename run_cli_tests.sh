#!/bin/bash

echo "🧪 RuleK CLI 测试运行器"
echo "===================="

# 设置环境变量
export PYTEST_RUNNING=1

# 确保脚本在项目根目录运行
cd "$(dirname "$0")"

# 首先运行验证脚本
echo "📍 运行修复验证..."
python verify_fixes.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🏃 运行CLI测试..."
    pytest tests/cli/test_cli_game.py -v --tb=short
    
    # 检查测试结果
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 所有测试通过！"
    else
        echo ""
        echo "❌ 有测试失败，请查看上面的错误信息"
    fi
else
    echo ""
    echo "❌ 修复验证失败，请先解决验证脚本中的问题"
fi

echo ""
echo "测试完成"
