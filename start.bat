@echo off
REM 快速启动脚本 - Windows版本

echo 🎮 启动规则怪谈管理者...

REM 检查Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python
    exit /b 1
)

REM 检查Node
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Node.js
    exit /b 1
)

REM 安装Python依赖
echo 📦 检查 Python 依赖...
pip install -q -r requirements.txt

REM 启动后端
echo 🚀 启动后端服务器...
start /B python rulek.py web

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 检查前端依赖
echo 📦 检查前端依赖...
cd web\frontend
if not exist node_modules (
    echo 📥 安装前端依赖...
    call npm install
)

REM 启动前端
echo 🚀 启动前端开发服务器...
start /B npm run dev

REM 等待前端启动
timeout /t 3 /nobreak >nul

echo.
echo ✨ 规则怪谈管理者已启动！
echo 🌐 前端地址: http://localhost:5173
echo 🔧 后端地址: http://localhost:8000
echo 📚 API 文档: http://localhost:8000/docs
echo.
echo 按任意键停止所有服务...
pause >nul

REM 停止所有Python和Node进程
taskkill /F /IM python.exe >nul 2>nul
taskkill /F /IM node.exe >nul 2>nul
