#!/bin/bash
# RuleK 快速启动脚本

echo "🎮 规则怪谈管理者 - 快速启动"
echo "=============================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python 3，请先安装Python 3.10+"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "⚠️  警告: 未找到Node.js，Web前端将无法运行"
    echo "   请访问 https://nodejs.org 安装Node.js"
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# 安装Python依赖
echo "📥 安装Python依赖..."
pip install -r requirements.txt

# 检查是否有.env文件
if [ ! -f ".env" ]; then
    echo "📝 创建.env配置文件..."
    cp .env.example .env
    echo "   请编辑 .env 文件添加你的 DEEPSEEK_API_KEY"
fi

# 选择运行模式
echo ""
echo "请选择运行模式:"
echo "1) CLI游戏 (命令行版本)"
echo "2) Web游戏 (浏览器版本)"
echo "3) 功能演示"
echo "4) 运行测试"
echo "5) 验证环境"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo "🎮 启动CLI游戏..."
        python rulek.py cli
        ;;
    2)
        echo "🌐 启动Web服务..."
        # 启动后端
        echo "启动后端服务器..."
        python rulek.py web &
        BACKEND_PID=$!
        
        # 等待后端启动
        sleep 3
        
        # 检查前端依赖
        if [ -d "web/frontend/node_modules" ]; then
            echo "前端依赖已安装"
        else
            echo "📥 安装前端依赖..."
            cd web/frontend
            npm install
            cd ../..
        fi
        
        # 启动前端
        echo "启动前端开发服务器..."
        cd web/frontend
        npm run dev &
        FRONTEND_PID=$!
        cd ../..
        
        echo ""
        echo "✅ 服务已启动!"
        echo "   前端: http://localhost:5173"
        echo "   后端API文档: http://localhost:8000/docs"
        echo ""
        echo "按 Ctrl+C 停止所有服务"
        
        # 等待用户中断
        trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
        wait
        ;;
    3)
        echo "🎭 运行功能演示..."
        python rulek.py demo
        ;;
    4)
        echo "🧪 运行测试套件..."
        python rulek.py test
        ;;
    5)
        echo "✅ 验证环境配置..."
        python rulek.py verify
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac
