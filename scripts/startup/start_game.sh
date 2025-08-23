#!/bin/bash
# RuleK Web UI 快速启动脚本

echo "╔══════════════════════════════════════════════════╗"
echo "║        🎮 RuleK - 规则怪谈管理者 🎮            ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 检查Node.js
echo -e "${CYAN}📋 检查环境...${NC}"
if command -v node &> /dev/null; then
    echo -e "${GREEN}✅ Node.js $(node --version)${NC}"
else
    echo -e "${RED}❌ 未找到Node.js，请先安装${NC}"
    echo "访问: https://nodejs.org/"
    exit 1
fi

# 停止旧进程
echo -e "\n${CYAN}🛑 停止旧进程...${NC}"
pkill -f "start_web_server.py" 2>/dev/null
pkill -f "rulek.py web" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
sleep 2

# 启动后端
echo -e "\n${CYAN}🚀 启动后端服务器...${NC}"
python3 start_web_server.py &
BACKEND_PID=$!
echo -e "${GREEN}✅ 后端已启动 (PID: $BACKEND_PID)${NC}"
echo "   地址: http://localhost:8000"

# 等待后端启动
sleep 3

# 检查前端依赖
echo -e "\n${CYAN}🚀 启动前端界面...${NC}"
cd web/frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 首次运行，安装依赖...${NC}"
    npm install
fi

# 启动前端
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ 前端已启动 (PID: $FRONTEND_PID)${NC}"
echo "   地址: http://localhost:5173"

# 等待前端启动
sleep 5

# 尝试打开浏览器
echo -e "\n${CYAN}🌐 打开浏览器...${NC}"
if command -v open &> /dev/null; then
    # macOS
    open http://localhost:5173
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:5173
elif command -v start &> /dev/null; then
    # Windows
    start http://localhost:5173
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║              ✨ 启动成功！✨                    ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║  🎮 游戏界面: http://localhost:5173            ║"
echo "║  🔧 API文档:  http://localhost:8000/docs       ║"
echo "║  📊 API端点:  http://localhost:8000            ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║          按 Ctrl+C 停止所有服务                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# 捕获Ctrl+C
trap cleanup INT

cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 正在停止所有服务...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    pkill -f "npm run dev" 2>/dev/null
    echo -e "${GREEN}✅ 所有服务已停止${NC}"
    echo -e "${CYAN}👋 感谢使用RuleK！${NC}"
    exit 0
}

# 等待用户中断
wait
