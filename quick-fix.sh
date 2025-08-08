#!/bin/bash

# 快速修复并启动RuleK Web

echo "🚀 RuleK Web 快速启动脚本"
echo "=========================="
echo ""

# 1. 杀死占用端口的进程
echo "1️⃣ 清理端口..."
pkill -f "npm run dev" 2>/dev/null
pkill -f "vite" 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
lsof -ti:5174 | xargs kill -9 2>/dev/null
echo "   ✅ 端口已清理"
echo ""

# 2. 安装依赖
echo "2️⃣ 安装依赖..."
echo "   安装根目录依赖..."
npm install --save-dev @playwright/test playwright chalk 2>/dev/null
echo "   ✅ 根目录依赖安装完成"

echo "   安装前端依赖..."
cd web/frontend
npm install --save-dev @playwright/test playwright 2>/dev/null
cd ../..
echo "   ✅ 前端依赖安装完成"
echo ""

# 3. 安装Playwright浏览器
echo "3️⃣ 安装Playwright浏览器..."
npx playwright install chromium --with-deps
echo "   ✅ Playwright准备就绪"
echo ""

# 4. 启动服务
echo "4️⃣ 启动服务..."

# 启动后端（如果未运行）
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "   启动后端服务..."
    python start_web_server.py &
    sleep 3
    echo "   ✅ 后端运行在 http://localhost:8000"
else
    echo "   ✅ 后端已在运行"
fi

# 启动前端
echo "   启动前端服务..."
cd web/frontend
npm run dev &
cd ../..
sleep 5
echo "   ✅ 前端运行在 http://localhost:5173"
echo ""

# 5. 运行测试
echo "5️⃣ 运行环境验证测试..."
cd web/frontend
npm run test:phase0

echo ""
echo "=========================="
echo "✅ 环境准备完成！"
echo ""
echo "访问以下地址："
echo "  前端: http://localhost:5173"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "可用命令："
echo "  cd web/frontend && npm run dev     # 启动前端"
echo "  cd web/frontend && npm run test:phase0  # 运行测试"
echo "  npm run track:phase0                # 查看进度（根目录）"
