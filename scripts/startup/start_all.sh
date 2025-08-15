#!/bin/bash
# RuleK 一键启动脚本

echo "=========================================="
echo "       RuleK - 规则怪谈管理者"
echo "=========================================="

# 启动后端
echo ""
echo "1. 启动后端服务器..."
python start_web_server.py &
BACKEND_PID=$!
echo "   后端PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "2. 启动前端开发服务器..."
cd web/frontend
npm run dev &
FRONTEND_PID=$!
echo "   前端PID: $FRONTEND_PID"

echo ""
echo "=========================================="
echo "✅ 服务已启动！"
echo ""
echo "   后端: http://localhost:8000"
echo "   前端: http://localhost:5173"
echo ""
echo "   按 Ctrl+C 停止所有服务"
echo "=========================================="

# 等待中断信号
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 保持脚本运行
wait
