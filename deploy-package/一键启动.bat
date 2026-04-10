@echo off
chcp 65001 > nul
title 电力交易AI平台

echo.
echo ========================================
echo   电力交易AI平台 - 一键启动
echo ========================================
echo.

cd /d "%~dp0"

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python！
    echo.
    echo 请先安装Python:
    echo https://www.python.org/downloads/
    echo.
    echo 安装后请确保勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [1/3] 检查环境...
python --version

:: 进入后端目录
cd backend

:: 复制环境配置
if exist ".env.local" (
    copy /Y ".env.local" ".env" >nul
    echo [2/3] 配置已加载
) else (
    echo [2/3] 使用默认配置
)

:: 创建虚拟环境（如果不存在）
if not exist ".venv" (
    echo [3/3] 创建虚拟环境并安装依赖...
    echo 这可能需要几分钟，请稍候...
    python -m venv .venv
    call .venv\Scripts\pip.exe install -r requirements.txt --quiet
    echo 依赖安装完成
) else (
    echo [3/3] 依赖已就绪
)

echo.
echo ========================================
echo   服务启动中...
echo ========================================
echo.
echo   平台地址: http://127.0.0.1:8000/console
echo   API文档:   http://127.0.0.1:8000/docs
echo.
echo   按 Ctrl+C 停止服务
echo.

:: 打开浏览器
start http://127.0.0.1:8000/console

:: 启动服务
call .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
