#!/bin/bash

echo "🔍 开始诊断游戏创建问题..."
echo "================================"

cd /Users/chenpinle/Desktop/杂/pythonProject/RuleK/web/frontend

# 检查服务是否运行
echo "📡 检查服务状态..."
if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ 前端服务运行中"
else
    echo "❌ 前端服务未运行"
    echo "   请先运行: npm run dev"
fi

if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务运行中"
else
    echo "⚠️ 后端服务未运行"
    echo "   请先运行: python start_web_server.py"
fi

echo ""
echo "🧪 运行Playwright测试..."
echo "================================"

# 确保test-results目录存在
mkdir -p test-results

# 运行测试
if [ -f "node_modules/.bin/playwright" ]; then
    ./node_modules/.bin/playwright test tests/game-creation.spec.ts --reporter=list
else
    echo "❌ Playwright未安装"
    echo "   运行: npm install -D @playwright/test"
    echo "   然后: npx playwright install"
fi

echo ""
echo "================================"
echo "📊 测试完成！"
echo "截图保存在: web/frontend/test-results/"
echo ""
