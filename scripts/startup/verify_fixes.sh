#!/bin/bash
# RuleK API 最终修复验证脚本

echo "🔧 RuleK API 最终修复验证"
echo "============================================"

# 停止旧服务
echo "🛑 停止旧服务..."
pkill -f "rulek.py web" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
sleep 2

# 启动新服务
echo "🚀 启动服务器..."
python3 rulek.py web &
SERVER_PID=$!
echo "✅ 服务器已启动 (PID: $SERVER_PID)"

# 等待服务器启动
echo "⏳ 等待服务器就绪..."
sleep 5

# 运行验证测试
echo ""
echo "🧪 运行验证测试..."
python3 scripts/test/verify_all_fixes.py
TEST_RESULT=$?

# 检查测试结果
if [ $TEST_RESULT -eq 0 ]; then
    echo ""
    echo "✨ 所有测试通过！API已完全修复！"
    echo "📝 修复内容："
    echo "  1. 规则创建的location字段类型问题"
    echo "  2. 推进回合的NPC.get属性问题"
    echo "  3. 保存游戏的JSON序列化问题"
else
    echo ""
    echo "⚠️ 测试未完全通过，请检查日志"
fi

# 询问是否保持服务器运行
echo ""
echo "❓ 是否保持服务器运行? (y/n)"
read -r keep_running

if [[ "$keep_running" != "y" ]]; then
    echo "🛑 停止服务器..."
    kill $SERVER_PID 2>/dev/null
    echo "✅ 服务器已停止"
else
    echo "✅ 服务器继续运行"
    echo "📍 访问: http://localhost:8000"
    echo "📍 文档: http://localhost:8000/docs"
fi

echo ""
echo "🎉 验证完成！"
