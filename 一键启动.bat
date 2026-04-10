@echo off
chcp 65001 > nul
title 电力交易AI平台

echo.
echo ========================================
echo   电力交易AI平台 - 一键启动
echo ========================================
echo.

cd /d "%~dp0backend"

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python！
    echo.
    echo 请先安装Python:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/4] 检查环境...
python --version

:: 创建本地配置
echo [2/4] 配置环境...
(
echo # 本地部署配置
echo APP_ENV=local
echo APP_HOST=127.0.0.1
echo APP_PORT=8000
echo APP_DATABASE_PATH=./power_trading.db
echo APP_AUTH_ENABLED=true
echo APP_AUTH_JWT_SECRET=local-dev-secret-key
echo APP_MOUNT_FRONTEND_DIST=true
) > .env.local

copy /Y .env.local .env >nul
echo 配置完成

:: 创建虚拟环境（如果不存在）
if not exist ".venv" (
    echo [3/4] 创建虚拟环境并安装依赖...
    echo 这可能需要几分钟，请稍候...
    python -m venv .venv
    call .venv\Scripts\pip.exe install -r requirements.txt
) else (
    echo [3/4] 依赖已就绪
)

echo.
echo ========================================
echo   正在启动服务，请稍候...
echo ========================================
echo.

:: 启动后端服务
start "电力交易AI平台" .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

:: 等待服务启动
echo 等待服务启动...
for /L %%i in (1,1,20) do (
    ping -n 2 127.0.0.1 >nul
    netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
    if not errorlevel 1 (
        goto service_ready
    )
)

:service_ready
timeout /t 2 /nobreak >nul
echo 服务已就绪！
echo.

:: 打开浏览器
start http://127.0.0.1:8000/console

echo ========================================
echo   服务已启动！
echo ========================================
echo.
echo   平台地址: http://127.0.0.1:8000/console
echo   API文档:   http://127.0.0.1:8000/docs
echo.
echo   关闭命令窗口可停止服务
echo.
pause
