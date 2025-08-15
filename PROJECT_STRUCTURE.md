# RuleK 项目结构说明

## 📁 目录结构

```
RuleK/
├── 📂 config/           # 配置文件
├── 📂 data/             # 游戏数据
├── 📂 deploy/           # 部署相关文件
├── 📂 docs/             # 项目文档
│   ├── architecture/   # 架构设计文档
│   ├── dev/            # 开发文档
│   ├── examples/       # 示例文件
│   ├── guides/         # 使用指南
│   ├── legacy/         # 旧版文档
│   └── plans/          # 计划文档
├── 📂 logs/             # 日志文件
├── 📂 scripts/          # 所有脚本
│   ├── deploy/         # 部署脚本
│   ├── dev/            # 开发工具
│   ├── diagnostic/     # 诊断工具
│   ├── fix/            # 修复脚本
│   ├── setup/          # 设置脚本
│   ├── startup/        # 启动脚本
│   ├── test/           # 测试脚本
│   └── utils/          # 工具脚本
├── 📂 src/              # 源代码
├── 📂 tests/            # 测试用例
├── 📂 tools/            # 项目管理工具
├── 📂 web/              # Web界面
│   ├── backend/        # 后端代码
│   └── frontend/       # 前端代码
└── 📄 核心文件          # 根目录核心文件

```

## 🚀 快速开始

### 主要入口
- `rulek.py` - 统一入口程序
- `start_web_server.py` - Web服务器启动
- `manage.py` - 项目管理工具
- `start.sh` / `start.bat` - 快速启动脚本

### 常用命令

```bash
# 启动Web服务器
python start_web_server.py
# 或
python rulek.py web

# 启动CLI游戏
python rulek.py cli

# 运行测试
python rulek.py test

# 项目管理
python manage.py
```

## 📂 脚本分类说明

### scripts/startup/ - 启动脚本
- `start_all.py` - 启动所有服务
- `start_backend_direct.py` - 直接启动后端
- `start_servers_simple.py` - 简单服务器启动
- `restart_all.sh` - 重启所有服务

### scripts/fix/ - 修复脚本
- `fix_and_start.sh` - 修复并启动
- `fix_axios.sh` - 修复Axios问题
- `fix_frontend.sh` - 修复前端问题
- `quick_fix.sh` - 快速修复

### scripts/diagnostic/ - 诊断工具
- `diagnose_frontend.py` - 前端诊断
- `diagnose_game.py` - 游戏诊断
- `check_health.py` - 健康检查
- `check_frontend.sh` - 前端检查

### scripts/test/ - 测试脚本
- `final_test.py` - 最终测试
- `test_ai_integration.py` - AI集成测试
- `test_ai_simple.py` - 简单AI测试
- `validate_rule_system.py` - 规则系统验证

### scripts/dev/ - 开发工具
- `improve_rules.py` - 规则改进工具
- `integrate_rule_api.py` - API集成工具
- `create_frontend_components.py` - 前端组件创建
- `play.py` - 游戏测试工具
- `play_cli.py` - CLI游戏测试

### scripts/setup/ - 设置脚本
- `setup_rulek_project.py` - 项目设置
- `clean_rulek_temp.py` - 临时文件清理

### scripts/utils/ - 工具脚本
- `cleanup.sh` - 清理脚本
- `make_executable.sh` - 设置可执行权限
- `restructure.py` - 项目重构工具

## 📚 文档结构

### docs/architecture/ - 架构文档
- AI核心实现相关文档
- Web端优化计划

### docs/dev/ - 开发文档
- `AGENT.md` - AI协作规范
- `PROJECT_PLAN.md` - 项目计划
- `PROFESSIONAL_START.md` - 专业化启动指南

### docs/guides/ - 使用指南
- `Quick_Start_Guide.md` - 快速开始
- `CLI_Testing_and_Development.md` - CLI开发指南
- `GAME_DEMO_GUIDE.md` - 游戏演示指南

### docs/plans/ - 计划文档
- `MCP_Development_Plan.md` - MCP开发计划
- `PROJECT_RESTRUCTURE_PLAN.md` - 重构计划
- `REMAINING_TASKS.md` - 待完成任务

## 🔧 项目管理

使用 `python manage.py` 访问项目管理工具，可以：
- 查看项目状态
- 运行测试
- 清理临时文件
- 启动服务器

## 📝 重要文件

### 配置文件
- `.env` - 环境变量（不提交到Git）
- `.env.example` - 环境变量示例
- `requirements.txt` - Python依赖
- `package.json` - Node.js依赖
- `pyproject.toml` - Python项目配置

### 构建文件
- `Makefile` - Make构建配置
- `.pre-commit-config.yaml` - Git提交前检查

### 文档
- `README.md` - 项目说明
- `LICENSE` - 许可证

---

*更新日期：2024-12-22*
