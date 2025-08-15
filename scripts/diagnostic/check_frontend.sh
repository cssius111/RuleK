#!/bin/bash

echo "🔍 检查前端环境..."
echo "================================"

# 进入前端目录
cd web/frontend

# 检查是否有重复的文件
echo "📁 检查重复文件..."
if [ -f "src/stores/game.js" ] && [ -f "src/stores/game.ts" ]; then
    echo "⚠️  发现重复的 game store 文件！"
    echo "   - game.js"
    echo "   - game.ts"
else
    echo "✅ 没有重复的 store 文件"
fi

# 检查依赖
echo ""
echo "📦 检查依赖安装..."
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules 不存在，需要安装依赖"
    echo "   运行: cd web/frontend && npm install"
else
    echo "✅ 依赖已安装"
fi

# 检查环境文件
echo ""
echo "⚙️  检查环境配置..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在"
    echo "   创建 .env 文件并配置 API 地址"
    if [ -f ".env.example" ]; then
        echo "   可以复制 .env.example: cp .env.example .env"
    fi
else
    echo "✅ .env 文件存在"
    echo "   API 配置:"
    grep "VITE_API" .env || echo "   未找到 API 配置"
fi

echo ""
echo "================================"
echo "📝 修复建议："
echo "1. 删除旧的 game.js 文件（已完成）"
echo "2. 重启开发服务器: npm run dev"
echo "3. 清除浏览器缓存"
echo "4. 检查浏览器控制台错误"
echo ""
echo "🚀 启动命令："
echo "   cd web/frontend && npm run dev"
echo ""
