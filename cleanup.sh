#!/bin/bash
# 整理项目文件脚本

echo "🧹 开始整理项目文件..."

# 移动文档到 docs/
FILES_TO_DOCS=(
    "AI_Integration_Phase3_Complete_Report.md"
    "AI_Integration_Phase3_Summary.md"
    "AI_Integration_Progress_Report_Phase3_Complete.md"
    "CLI_TEST_FIX_REPORT.md"
    "NEXT_STEPS.md"
    "QUICK_START_FIXED.md"
    "QUICK_START_GAME.md"
    "RUN_GAME_NOW.md"
    "TEST_FIX_SUMMARY.md"
)

for file in "${FILES_TO_DOCS[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "docs/" 2>/dev/null && echo "✅ 移动 $file 到 docs/"
    fi
done

# 移动测试脚本到 scripts/test/
TEST_SCRIPTS=(
    "check_missing_modules.py"
    "fix_ai_issues.py"
    "minimal_test.py"
    "quick_verify.py"
    "test_all_fixes.py"
    "test_fixes.py"
    "verify_ai_integration.py"
    "verify_final.py"
    "verify_fix.py"
    "verify_fix_v2.py"
    "verify_fixes.py"
)

for script in "${TEST_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        mv "$script" "scripts/test/" 2>/dev/null && echo "✅ 移动 $script 到 scripts/test/"
    fi
done

# 移动 shell 脚本到 scripts/
SHELL_SCRIPTS=(
    "run_cli_tests.sh"
    "verify_all_fixes.sh"
    "verify_cli_tests.sh"
)

for script in "${SHELL_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        mv "$script" "scripts/" 2>/dev/null && echo "✅ 移动 $script 到 scripts/"
    fi
done

# 删除临时文件
rm -f "start_web_server.py"

# 清理缓存
echo "🧹 清理缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
rm -rf .pytest_cache .mypy_cache .ruff_cache

echo "✅ 整理完成！"
