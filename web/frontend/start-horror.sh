#!/bin/bash

echo "🎮 RuleK 恐怖游戏 - 前端启动脚本"
echo "================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误：请在 web/frontend 目录下运行此脚本"
    exit 1
fi

# 检查是否安装了依赖
if [ ! -d "node_modules" ]; then
    echo "📦 正在安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

echo "🎨 恐怖主题已激活"
echo "💀 所有页面已改造为暗黑风格"
echo ""
echo "🚀 启动开发服务器..."
echo ""

# 启动开发服务器
npm run dev

# 如果需要同时启动后端，取消下面的注释
# echo "🔧 启动后端API服务器..."
# cd ../backend
# python app.py
