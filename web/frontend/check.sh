#!/bin/bash

# RuleK Web Frontend 快速验证脚本
# 在 web/frontend 目录运行

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "     RuleK Web Frontend 环境验证"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $2${NC}"
        return 0
    else
        echo -e "${RED}❌ $2 未安装${NC}"
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $2 存在${NC}"
        return 0
    else
        echo -e "${RED}❌ $2 不存在${NC}"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅ $2 存在${NC}"
        return 0
    else
        echo -e "${RED}❌ $2 不存在${NC}"
        return 1
    fi
}

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✅ 端口 $1 服务运行中${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  端口 $1 服务未运行${NC}"
        return 1
    fi
}

# 开始检查
echo -e "${BLUE}1. 基础环境检查${NC}"
echo "------------------------"
check_command node "Node.js"
check_command npm "npm"
check_command python3 "Python 3"
echo ""

echo -e "${BLUE}2. 项目结构检查${NC}"
echo "------------------------"
check_file "package.json" "package.json"
check_file "vite.config.ts" "Vite配置"
check_file "tsconfig.json" "TypeScript配置"
check_dir "src" "源代码目录"
check_dir "node_modules" "依赖包"
echo ""

echo -e "${BLUE}3. 服务状态检查${NC}"
echo "------------------------"
check_port 5173 "开发服务器(5173)"
check_port 8000 "API服务器(8000)"
echo ""

echo -e "${BLUE}4. 可用脚本检查${NC}"
echo "------------------------"
if [ -f "package.json" ]; then
    echo "主要脚本："
    grep -E '"(dev|build|test:phase0|track:phase0|setup:playwright)"' package.json | sed 's/.*"\([^"]*\)".*/  • \1/'
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}下一步操作建议：${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 根据检查结果给出建议
if [ ! -d "node_modules" ]; then
    echo "1. 安装依赖："
    echo "   npm install"
    echo ""
fi

if ! lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "2. 启动开发服务器："
    echo "   npm run dev"
    echo ""
fi

if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "3. 启动API服务器（新终端）："
    echo "   cd ../.. && python start_web_server.py"
    echo ""
fi

echo "4. 安装Playwright（E2E测试）："
echo "   npm run setup:playwright"
echo ""

echo "5. 运行环境验证测试："
echo "   npm run test:phase0"
echo ""

echo "6. 查看进度报告："
echo "   npm run track:phase0"
echo ""

echo -e "${GREEN}提示：环境就绪后，访问 http://localhost:5173 查看应用${NC}"
