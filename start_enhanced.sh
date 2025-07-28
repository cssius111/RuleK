#!/bin/bash
# Enhanced start script with port detection and management

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default ports
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-5173}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to find process using port
find_process() {
    local port=$1
    lsof -i :$port | grep LISTEN | awk '{print $2}' | head -1
}

# Function to find free port
find_free_port() {
    local start_port=$1
    local port=$start_port
    
    while check_port $port; do
        port=$((port + 1))
        if [ $port -gt $((start_port + 100)) ]; then
            echo "Error: Could not find free port in range $start_port-$port" >&2
            return 1
        fi
    done
    
    echo $port
}

# ASCII Art Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║       规则怪谈管理者 (RuleK)           ║"
echo "║         Enhanced Startup               ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Check Python
echo -e "${YELLOW}🔍 检查环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    exit 1
fi

# Check ports
echo -e "${YELLOW}🔍 检查端口...${NC}"

# Backend port check
if check_port $BACKEND_PORT; then
    PID=$(find_process $BACKEND_PORT)
    echo -e "${YELLOW}⚠️  后端端口 $BACKEND_PORT 已被占用 (PID: $PID)${NC}"
    echo -e "选项："
    echo "1) 终止进程并使用端口 $BACKEND_PORT"
    echo "2) 自动查找可用端口"
    echo "3) 手动指定端口"
    echo "4) 退出"
    
    read -p "请选择 (1-4): " choice
    
    case $choice in
        1)
            echo -e "${YELLOW}终止进程 $PID...${NC}"
            kill -9 $PID 2>/dev/null
            sleep 1
            if check_port $BACKEND_PORT; then
                echo -e "${RED}❌ 无法终止进程${NC}"
                exit 1
            fi
            ;;
        2)
            NEW_PORT=$(find_free_port $BACKEND_PORT)
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ 找到可用端口: $NEW_PORT${NC}"
                BACKEND_PORT=$NEW_PORT
            else
                exit 1
            fi
            ;;
        3)
            read -p "输入后端端口号: " BACKEND_PORT
            if check_port $BACKEND_PORT; then
                echo -e "${RED}❌ 端口 $BACKEND_PORT 仍被占用${NC}"
                exit 1
            fi
            ;;
        4)
            echo -e "${YELLOW}退出...${NC}"
            exit 0
            ;;
    esac
fi

# Frontend port check
if check_port $FRONTEND_PORT; then
    PID=$(find_process $FRONTEND_PORT)
    echo -e "${YELLOW}⚠️  前端端口 $FRONTEND_PORT 已被占用 (PID: $PID)${NC}"
    FRONTEND_PORT=$(find_free_port $FRONTEND_PORT)
    echo -e "${GREEN}✅ 前端将使用端口: $FRONTEND_PORT${NC}"
fi

# Export ports for child processes
export BACKEND_PORT
export FRONTEND_PORT
export VITE_API_URL="http://localhost:$BACKEND_PORT"

# Start backend
echo -e "${GREEN}🚀 启动后端服务 (端口: $BACKEND_PORT)...${NC}"
cd web/backend
python3 run_server.py &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}⏳ 等待后端启动...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端已启动${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ 后端启动超时${NC}"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
done

# Start frontend
echo -e "${GREEN}🚀 启动前端服务 (端口: $FRONTEND_PORT)...${NC}"
cd ../frontend
npm run dev -- --port $FRONTEND_PORT &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 正在关闭服务...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ 服务已关闭${NC}"
    exit 0
}

# Register cleanup function
trap cleanup SIGINT SIGTERM

# Wait for frontend
echo -e "${YELLOW}⏳ 等待前端启动...${NC}"
sleep 5

# Display access info
echo -e "\n${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✅ RuleK 已成功启动！${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "🌐 前端地址: ${BLUE}http://localhost:$FRONTEND_PORT${NC}"
echo -e "🔧 后端API: ${BLUE}http://localhost:$BACKEND_PORT${NC}"
echo -e "📚 API文档: ${BLUE}http://localhost:$BACKEND_PORT/docs${NC}"
echo -e "\n${YELLOW}按 Ctrl+C 停止服务${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}\n"

# Keep script running
wait
