#!/bin/bash
# RuleK API 快速修复和测试脚本

echo "🔧 RuleK API 快速修复和测试"
echo "============================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 1. 检查Python环境
echo -e "${CYAN}📦 检查Python环境...${NC}"
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python3 已安装${NC}"
    python3 --version
else
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

# 2. 安装依赖
echo -e "\n${CYAN}📦 检查并安装依赖...${NC}"
pip3 install -q -r requirements.txt 2>/dev/null
echo -e "${GREEN}✅ 依赖已就绪${NC}"

# 3. 停止已运行的服务
echo -e "\n${CYAN}🛑 停止已运行的服务...${NC}"
pkill -f "rulek.py web" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
sleep 2
echo -e "${GREEN}✅ 旧服务已停止${NC}"

# 4. 启动服务器
echo -e "\n${CYAN}🚀 启动API服务器...${NC}"
python3 rulek.py web &
SERVER_PID=$!
echo -e "${GREEN}✅ 服务器已启动 (PID: $SERVER_PID)${NC}"

# 等待服务器启动
echo -e "${YELLOW}⏳ 等待服务器就绪...${NC}"
sleep 5

# 5. 运行测试
echo -e "\n${CYAN}🧪 运行测试...${NC}"
python3 scripts/test/test_final_fixes.py

# 6. 询问是否保持服务器运行
echo -e "\n${CYAN}❓ 是否保持服务器运行? (y/n)${NC}"
read -r keep_running

if [[ "$keep_running" != "y" ]]; then
    echo -e "${YELLOW}🛑 停止服务器...${NC}"
    kill $SERVER_PID 2>/dev/null
    echo -e "${GREEN}✅ 服务器已停止${NC}"
else
    echo -e "${GREEN}✅ 服务器继续运行中${NC}"
    echo -e "${CYAN}访问: http://localhost:8000${NC}"
    echo -e "${CYAN}文档: http://localhost:8000/docs${NC}"
    echo -e "${YELLOW}使用 'kill $SERVER_PID' 停止服务器${NC}"
fi

echo -e "\n${GREEN}✨ 完成!${NC}"
