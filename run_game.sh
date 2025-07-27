#!/bin/bash
# 规则怪谈游戏启动脚本

echo "🎭 规则怪谈管理者 - 启动中..."

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "Python版本: $python_version"

# 检查并安装依赖
if ! python3 -c "import pydantic" 2>/dev/null; then
    echo "正在安装必要的依赖..."
    pip3 install -r requirements_mvp.txt
fi

# 运行游戏
echo "启动游戏..."
python3 main_game.py

# 如果是Windows系统，使用python而不是python3
# python main_game.py
