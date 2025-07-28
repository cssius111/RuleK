#!/bin/bash

echo "🔧 RuleK 修复验证和测试脚本"
echo "============================"
echo ""

# 设置环境变量
export PYTEST_RUNNING=1

# 运行综合测试脚本
echo "📍 运行修复验证..."
python test_all_fixes.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 所有修复验证通过！"
    echo ""
    echo "现在可以运行完整测试套件："
    echo "python rulek.py test"
else
    echo ""
    echo "❌ 修复验证失败，请查看上面的错误信息"
fi
