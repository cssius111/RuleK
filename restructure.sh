#!/bin/bash
# RuleK 项目重构执行脚本

echo "RuleK 项目重构工具"
echo "=================="
echo ""

# 检查是否在项目根目录
if [ ! -f "rulek.py" ]; then
    echo "错误: 请在 RuleK 项目根目录运行此脚本"
    exit 1
fi

# 显示选项
echo "请选择操作："
echo "1) 预览重构计划（推荐先执行）"
echo "2) 执行完整重构"
echo "3) 仅清理缓存和备份文件"
echo "4) 查看重构计划文档"
echo "5) 退出"
echo ""

read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "--- 预览模式 ---"
        python scripts/utils/restructure.py --dry-run
        ;;
    2)
        echo ""
        echo "⚠️  警告: 这将移动大量文件，建议先备份项目"
        read -p "是否继续? (y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            python scripts/utils/restructure.py
        else
            echo "已取消"
        fi
        ;;
    3)
        echo ""
        echo "--- 清理模式 ---"
        python scripts/utils/restructure.py --clean-only
        ;;
    4)
        echo ""
        echo "--- 查看重构计划 ---"
        if [ -f "docs/PROJECT_RESTRUCTURE_PLAN.md" ]; then
            less docs/PROJECT_RESTRUCTURE_PLAN.md
        else
            echo "错误: 找不到重构计划文档"
        fi
        ;;
    5)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo ""
echo "完成!"
