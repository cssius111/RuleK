#!/bin/bash
# RuleK 快速命令脚本

case "$1" in
    "play"|"")
        echo "🎮 启动规则怪谈管理者..."
        python play.py
        ;;
    "web")
        echo "🌐 启动Web服务器..."
        python play.py web
        ;;
    "test")
        echo "🧪 运行测试..."
        python test_fixes.py
        ;;
    "fix")
        echo "🔧 验证修复..."
        python fix_ai_issues.py
        ;;
    "help")
        echo "用法: ./game.sh [命令]"
        echo ""
        echo "命令:"
        echo "  play    运行CLI游戏（默认）"
        echo "  web     启动Web服务器"
        echo "  test    运行测试"
        echo "  fix     验证修复"
        echo "  help    显示此帮助"
        ;;
    *)
        echo "未知命令: $1"
        echo "使用 './game.sh help' 查看帮助"
        ;;
esac
