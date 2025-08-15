#!/bin/bash

echo "🚀 RuleK 项目修复和启动脚本"
echo "=============================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查Python环境
echo "📦 检查后端环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3 已安装${NC}"

# 2. 安装后端依赖
echo ""
echo "📦 安装后端依赖..."
pip3 install -r requirements.txt --quiet 2>/dev/null
echo -e "${GREEN}✅ 后端依赖已安装${NC}"

# 3. 检查前端环境
echo ""
echo "📦 检查前端环境..."
cd web/frontend

# 安装前端依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi
echo -e "${GREEN}✅ 前端依赖已安装${NC}"

# 4. 启动服务
echo ""
echo "🎮 启动游戏服务..."
echo "=============================="
echo ""

# 启动后端
echo "🔥 启动后端服务..."
cd ../..
python3 start_web_server.py &
BACKEND_PID=$!
echo -e "${GREEN}✅ 后端已启动 (PID: $BACKEND_PID)${NC}"

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "🎨 启动前端服务..."
cd web/frontend
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ 前端已启动 (PID: $FRONTEND_PID)${NC}"

# 显示访问信息
echo ""
echo "=============================="
echo -e "${GREEN}🎉 服务已启动！${NC}"
echo ""
echo "📍 访问地址："
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "💡 提示："
echo "   1. 清除浏览器缓存 (Cmd+Shift+R)"
echo "   2. 打开浏览器控制台查看错误"
echo "   3. 按 Ctrl+C 停止所有服务"
echo ""
echo "=============================="
echo ""

# 等待用户中断
echo "按 Ctrl+C 停止服务..."
wait

# 清理
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null
echo ""
echo "👋 服务已停止"
