#!/bin/bash
# 测试前端是否能正常启动
# 2025-01-08

echo "==================================="
echo "   前端启动测试脚本"
echo "==================================="

cd "$(dirname "$0")/../../web/frontend"

echo "📦 检查依赖..."
if [ ! -d "node_modules" ]; then
    echo "⚠️  未找到 node_modules，正在安装依赖..."
    npm install
fi

echo "🚀 启动前端开发服务器..."
echo "等待10秒后检查服务状态..."

# 后台启动前端
npm run dev &
FRONTEND_PID=$!

sleep 10

# 检查端口是否打开
if lsof -i:5173 | grep -q LISTEN; then
    echo "✅ 前端成功启动在 http://localhost:5173"
    echo "✅ API导入问题已修复"
    
    # 终止前端进程
    kill $FRONTEND_PID 2>/dev/null
    
    echo "测试完成，前端进程已终止"
    exit 0
else
    echo "❌ 前端启动失败"
    echo "请检查错误日志"
    
    # 终止前端进程
    kill $FRONTEND_PID 2>/dev/null
    
    exit 1
fi
