# RuleK Project Makefile

.PHONY: help serve test clean install web cli manage

help:
	@echo "╔══════════════════════════════════════════╗"
	@echo "║         RuleK 项目任务管理                ║"
	@echo "╚══════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 运行命令:"
	@echo "  make serve   - 启动Web服务器"
	@echo "  make web     - 启动Web服务器(同serve)"
	@echo "  make cli     - 启动CLI游戏"
	@echo "  make manage  - 项目管理工具"
	@echo ""
	@echo "🧪 开发命令:"
	@echo "  make test    - 运行测试"
	@echo "  make clean   - 清理缓存文件"
	@echo "  make install - 安装依赖"
	@echo ""
	@echo "💡 提示: 也可以使用 python rulek.py [命令]"

serve:
	@echo "🚀 启动Web服务器..."
	@python scripts/startup/start_web_server.py

web:
	@python rulek.py web

cli:
	@python rulek.py cli

test:
	@echo "🧪 运行测试..."
	@python rulek.py test

manage:
	@echo "🔧 打开项目管理..."
	@python rulek.py manage

clean:
	@echo "🧹 清理缓存文件..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@find . -type f -name "*~" -delete 2>/dev/null || true
	@echo "✅ 清理完成！"

install:
	@echo "📦 安装依赖..."
	@pip install -r requirements.txt
	@echo "✅ 安装完成！"

# 快捷命令
s: serve
w: web
c: cli
t: test
m: manage
