#!/bin/bash

echo "🔧 修复 Axios 导入问题并重启服务"
echo "================================"

# 进入前端目录
cd /Users/chenpinle/Desktop/杂/pythonProject/RuleK/web/frontend

# 停止前端服务
echo "🛑 停止前端服务..."
pkill -f "npm run dev" 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
sleep 2

# 清除缓存
echo "🧹 清除缓存..."
rm -rf node_modules/.vite
rm -rf .vite
rm -rf dist

# 检查并安装 axios（如果需要）
echo "📦 检查依赖..."
if ! grep -q "axios" package.json; then
    echo "安装 axios..."
    npm install axios
fi

# 重新启动前端
echo "🚀 重新启动前端服务..."
npm run dev &
FRONTEND_PID=$!

# 等待启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ 前端服务启动成功！"
else
    echo "❌ 前端启动失败，查看日志"
fi

echo ""
echo "================================"
echo "✅ 修复完成！"
echo ""
echo "📍 请刷新浏览器页面："
echo "   http://localhost:5173/new-game"
echo ""
echo "💡 使用 Cmd+Shift+R 强制刷新"
echo ""
echo "进程ID: $FRONTEND_PID"
echo "================================"
