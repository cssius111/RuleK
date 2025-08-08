#!/bin/bash

# RuleK Web Frontend Setup Script

echo "🚀 RuleK Web前端初始化脚本"
echo "================================"

# 检查Node版本
echo "检查Node.js版本..."
node_version=$(node -v 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ 未检测到Node.js，请先安装Node.js 16+"
    exit 1
fi
echo "✅ Node.js版本: $node_version"

# 初始化Vue项目
echo ""
echo "📦 初始化Vue 3项目..."
npm create vite@latest . -- --template vue-ts

# 安装依赖
echo ""
echo "📦 安装核心依赖..."
npm install vue-router@4 pinia naive-ui @vicons/ionicons5
npm install socket.io-client axios dayjs
npm install -D @types/node tailwindcss postcss autoprefixer sass
npm install -D @vitejs/plugin-vue @vitejs/plugin-vue-jsx

# 配置Tailwind CSS
echo ""
echo "🎨 配置Tailwind CSS..."
npx tailwindcss init -p

cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'horror-purple': '#8b5cf6',
        'horror-dark': '#1a0033',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
EOF

# 创建目录结构
echo ""
echo "📁 创建项目结构..."
mkdir -p src/{router,stores,views,components/{game,ai,common},composables,assets/{styles,images},types,api,utils}

# 创建主样式文件
cat > src/assets/styles/main.css << 'EOF'
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

/* 全局样式 */
body {
  @apply bg-gray-900 text-white;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  @apply bg-gray-800;
}

::-webkit-scrollbar-thumb {
  @apply bg-purple-600 rounded;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-purple-500;
}

/* 动画类 */
.glow {
  animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
  from {
    box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
  }
  to {
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  }
}
EOF

echo ""
echo "✅ Web前端环境初始化完成！"
echo ""
echo "📚 接下来的步骤："
echo "1. npm run dev"
echo "2. 访问 http://localhost:3000"
echo ""
echo "祝开发愉快！🚀"