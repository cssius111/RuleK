#!/bin/bash

# RuleK 环境修复脚本
# 解决所有依赖和路径问题

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "     RuleK 环境修复脚本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 停止占用5173端口的进程
echo -e "${BLUE}1. 清理端口占用...${NC}"
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "发现5173端口被占用，正在清理..."
    kill -9 $(lsof -Pi :5173 -sTCP:LISTEN -t)
    echo -e "${GREEN}✅ 端口已清理${NC}"
else
    echo -e "${GREEN}✅ 端口5173未被占用${NC}"
fi

if lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null ; then
    echo "清理5174端口..."
    kill -9 $(lsof -Pi :5174 -sTCP:LISTEN -t)
fi
echo ""

# 2. 安装项目根目录的依赖
echo -e "${BLUE}2. 安装项目根目录依赖...${NC}"
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ 未找到package.json，请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 安装Playwright和其他依赖
npm install --save-dev @playwright/test playwright chalk
echo -e "${GREEN}✅ 根目录依赖安装完成${NC}"
echo ""

# 3. 安装Playwright浏览器
echo -e "${BLUE}3. 安装Playwright浏览器...${NC}"
npx playwright install chromium
echo -e "${GREEN}✅ Playwright浏览器安装完成${NC}"
echo ""

# 4. 检查并安装前端依赖
echo -e "${BLUE}4. 检查前端依赖...${NC}"
if [ -d "web/frontend" ]; then
    cd web/frontend
    if [ ! -d "node_modules" ]; then
        echo "安装前端依赖..."
        npm install
    fi
    
    # 同样安装Playwright
    npm install --save-dev @playwright/test playwright
    
    cd ../..
    echo -e "${GREEN}✅ 前端依赖就绪${NC}"
else
    echo -e "${YELLOW}⚠️ 前端目录不存在${NC}"
fi
echo ""

# 5. 创建必要的目录结构
echo -e "${BLUE}5. 创建目录结构...${NC}"
mkdir -p src/router src/stores src/views src/components
mkdir -p web/frontend/src/{router,stores,views,components}
mkdir -p tests/e2e
mkdir -p web/frontend/tests
mkdir -p reports
echo -e "${GREEN}✅ 目录结构创建完成${NC}"
echo ""

# 6. 启动服务检查
echo -e "${BLUE}6. 服务状态检查...${NC}"

# 检查后端
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${GREEN}✅ 后端服务运行中 (端口8000)${NC}"
else
    echo -e "${YELLOW}⚠️ 后端服务未运行${NC}"
    echo "   启动命令: python start_web_server.py"
fi

# 检查前端
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${GREEN}✅ 前端服务运行中 (端口5173)${NC}"
else
    echo -e "${YELLOW}⚠️ 前端服务未运行${NC}"
    echo "   启动命令: cd web/frontend && npm run dev"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}修复完成！${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "下一步操作："
echo "1. 启动前端: cd web/frontend && npm run dev"
echo "2. 运行测试: cd web/frontend && npm run test:phase0"
echo "3. 或在根目录: npm run test:phase0"
echo ""
echo -e "${GREEN}提示: 所有依赖已安装，可以开始开发了！${NC}"
