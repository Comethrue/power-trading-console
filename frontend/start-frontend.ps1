# ==========================================
# 电力交易平台 - 前端启动脚本
# PowerGrid Console - Frontend Launcher
# ==========================================

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  电力交易平台控制台 - 前端启动" -ForegroundColor Cyan
Write-Host "  PowerGrid Console - Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到前端目录
Set-Location "$ProjectRoot\frontend"

# 检查 Node.js
Write-Host "[1/3] 检查 Node.js 环境..." -ForegroundColor Yellow
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCmd) {
    Write-Host "  错误: 未找到 Node.js" -ForegroundColor Red
    Write-Host "  请先安装 Node.js: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host "  Node.js 版本: $(node --version)" -ForegroundColor Green

# 检查 npm
Write-Host "[2/3] 检查 npm..." -ForegroundColor Yellow
Write-Host "  npm 版本: $(npm --version)" -ForegroundColor Green

# 安装依赖
Write-Host "[3/3] 安装前端依赖..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "  node_modules 已存在，跳过安装..." -ForegroundColor Gray
} else {
    Write-Host "  运行 npm install..." -ForegroundColor White
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  错误: npm install 失败" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  依赖安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "启动方式:" -ForegroundColor White
Write-Host ""
Write-Host "  开发模式 (推荐):" -ForegroundColor Yellow
Write-Host "    npm run dev" -ForegroundColor White
Write-Host "    - 支持热更新" -ForegroundColor Gray
Write-Host "    - 访问地址: http://localhost:5173" -ForegroundColor Gray
Write-Host "    - API 代理到: http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host ""
Write-Host "  生产构建:" -ForegroundColor Yellow
Write-Host "    npm run build" -ForegroundColor White
Write-Host "    - 输出到 dist 目录" -ForegroundColor Gray
Write-Host ""
Write-Host "  完整启动 (前后端):" -ForegroundColor Yellow
Write-Host "    ..\start-backend.ps1    # 先启动后端" -ForegroundColor White
Write-Host "    npm run dev              # 再启动前端" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# 询问是否立即启动
Write-Host "是否立即启动开发服务器? [Y/n]" -ForegroundColor White -NoNewline
$response = Read-Host
if ($response -ne "n" -and $response -ne "N") {
    Write-Host ""
    Write-Host "启动开发服务器..." -ForegroundColor Green
    Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Gray
    Write-Host ""
    npm run dev
}
