#!/bin/bash
# RuleK 前端快速修复脚本

echo "================================================"
echo "🔧 RuleK 前端修复和启动脚本"
echo "================================================"

# 进入前端目录
cd web/frontend

echo ""
echo "📋 步骤 1: 清理缓存"
rm -rf node_modules package-lock.json
rm -rf .vite

echo ""
echo "📋 步骤 2: 安装依赖"
echo "使用 npm 安装（可能需要几分钟）..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ npm install 失败"
    echo "尝试使用 cnpm 或 yarn:"
    echo "  cnpm install"
    echo "  或"
    echo "  yarn install"
    exit 1
fi

echo ""
echo "✅ 依赖安装成功"

echo ""
echo "📋 步骤 3: 启动前端开发服务器"
npm run dev
