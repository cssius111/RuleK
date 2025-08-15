#!/bin/bash

echo "🚀 RuleK 完整重启"
echo "================================"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
ROOT_DIR="/Users/chenpinle/Desktop/杂/pythonProject/RuleK"
cd "$ROOT_DIR"

# 1. 停止所有服务
echo -e "${YELLOW}🛑 停止所有服务...${NC}"
pkill -f "python.*start_web_server" 2>/dev/null
pkill -f "npm.*dev" 2>/dev/null
pkill -f "vite" 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
sleep 2

# 2. 清理缓存
echo -e "${YELLOW}🧹 清理缓存...${NC}"
cd "$ROOT_DIR/web/frontend"
rm -rf node_modules/.vite 2>/dev/null
rm -rf .vite 2>/dev/null
rm -rf dist 2>/dev/null

# 3. 启动后端
echo -e "${YELLOW}🔥 启动后端服务...${NC}"
cd "$ROOT_DIR"
python3 start_web_server.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"

# 等待后端启动
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ 后端启动成功${NC}"
        break
    fi
    sleep 1
done

# 4. 启动前端
echo -e "${YELLOW}🎨 启动前端服务...${NC}"
cd "$ROOT_DIR/web/frontend"

# 确保依赖安装
if [ ! -d "node_modules" ]; then
    echo "   📦 安装依赖..."
    npm install
fi

# 启动前端
npm run dev > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端 PID: $FRONTEND_PID"

# 等待前端启动
echo "   等待前端启动..."
for i in {1..15}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ 前端启动成功${NC}"
        break
    fi
    sleep 1
done

# 5. 测试API
echo -e "${YELLOW}🧪 测试API...${NC}"
sleep 2

# 测试健康检查
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ API健康检查通过${NC}"
else
    echo -e "${RED}   ❌ API健康检查失败${NC}"
fi

# 测试游戏创建
response=$(curl -s -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"difficulty":"normal","initial_fear_points":1000,"initial_npc_count":4}' \
  2>/dev/null)

if echo "$response" | grep -q "game_id"; then
    echo -e "${GREEN}   ✅ 游戏创建API正常${NC}"
else
    echo -e "${RED}   ❌ 游戏创建API异常${NC}"
fi

# 6. 显示结果
echo ""
echo "================================"
echo -e "${GREEN}✨ 服务启动完成！${NC}"
echo ""
echo "📍 访问地址："
echo "   前端: http://localhost:5173"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "🎮 开始游戏："
echo "   1. 打开: http://localhost:5173/new-game"
echo "   2. 强制刷新: Cmd+Shift+R"
echo "   3. 填写表单并点击'开启地狱之门'"
echo ""
echo "📝 查看日志："
echo "   后端: tail -f logs/backend.log"
echo "   前端: tail -f logs/frontend.log"
echo ""
echo "⛔ 停止服务："
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "================================"

# 保存PID
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# 尝试打开浏览器
sleep 2
open http://localhost:5173/new-game 2>/dev/null

# 保持运行
echo ""
echo "按 Ctrl+C 停止所有服务..."
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '👋 服务已停止'; exit" INT
wait
