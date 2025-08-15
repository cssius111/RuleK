#!/bin/bash

echo "🚀 RuleK 快速修复和启动"
echo "================================"

# 进入项目目录
cd /Users/chenpinle/Desktop/杂/pythonProject/RuleK

# 1. 清理旧进程
echo "🧹 清理旧进程..."
pkill -f "start_web_server.py" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
sleep 2

# 2. 修复store文件冲突
echo "📁 检查并修复文件冲突..."
if [ -f "web/frontend/src/stores/game.js" ]; then
    mv web/frontend/src/stores/game.js web/frontend/src/stores/game.js.old
    echo "  ✅ 移除了冲突的game.js文件"
fi

# 3. 确保环境配置存在
echo "⚙️ 配置环境..."
if [ ! -f "web/frontend/.env" ]; then
    cat > web/frontend/.env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_WS_URL=ws://localhost:8000
VITE_USE_MOCK_DATA=false
VITE_USE_REAL_API=true
VITE_DEBUG_MODE=true
EOF
    echo "  ✅ 创建了.env配置文件"
else
    echo "  ✅ .env文件已存在"
fi

# 4. 启动后端
echo ""
echo "🔥 启动后端服务..."
python3 start_web_server.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "  后端PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✅ 后端启动成功"
else
    echo "  ❌ 后端启动失败，检查 logs/backend.log"
    cat logs/backend.log | tail -20
    exit 1
fi

# 5. 启动前端
echo ""
echo "🎨 启动前端服务..."
cd web/frontend

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "  📦 安装依赖..."
    npm install
fi

npm run dev > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "  前端PID: $FRONTEND_PID"

# 等待前端启动
echo "  等待前端启动..."
for i in {1..10}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo "  ✅ 前端启动成功"
        break
    fi
    sleep 2
done

# 6. 显示结果
echo ""
echo "================================"
echo "🎮 服务启动完成！"
echo ""
echo "📍 访问地址："
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "🧪 测试游戏创建："
echo "   1. 访问 http://localhost:5173/new-game"
echo "   2. 填写表单"
echo "   3. 点击'开启地狱之门'"
echo ""
echo "📝 查看日志："
echo "   后端: tail -f logs/backend.log"
echo "   前端: tail -f logs/frontend.log"
echo ""
echo "⛔ 停止服务："
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "================================"
echo ""

# 保存PID到文件
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# 打开浏览器
sleep 2
open http://localhost:5173/new-game

# 保持脚本运行
echo "按 Ctrl+C 停止所有服务..."
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '👋 服务已停止'; exit" INT
wait
