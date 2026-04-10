@echo off
chcp 65001 > nul
title 电力交易AI平台 - 前端预览

cd /d "%~dp0frontend\dist"

echo.
echo ========================================
echo  启动前端预览服务器...
echo ========================================
echo.
echo  请确保后端服务已启动！
echo  访问地址: http://localhost:8080/console
echo  按 Ctrl+C 停止服务
echo.

powershell -Command "Start-Process http://localhost:8080/console"
python -m http.server 8080
