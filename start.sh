#!/bin/bash
# 快速启动脚本 - 同时启动后端和前端

echo "🎮 启动规则怪谈管理者..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    exit 1
fi

# 检查Node环境
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js"
    exit 1
fi

# 安装Python依赖
echo "📦 检查 Python 依赖..."
pip install -q -r requirements.txt

# 启动后端
echo "🚀 启动后端服务器..."
python rulek.py web &
BACKEND_PID=$!
echo "✅ 后端 PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 检查前端依赖
echo "📦 检查前端依赖..."
cd web/frontend
if [ ! -d "node_modules" ]; then
    echo "📥 安装前端依赖..."
    npm install
fi

# 启动前端
echo "🚀 启动前端开发服务器..."
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端 PID: $FRONTEND_PID"

# 等待前端启动
sleep 3

echo ""
echo "✨ 规则怪谈管理者已启动！"
echo "🌐 前端地址: http://localhost:5173"
echo "🔧 后端地址: http://localhost:8000"
echo "📚 API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务..."

# 捕获退出信号
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# 等待进程
wait
