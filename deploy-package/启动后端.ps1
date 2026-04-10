# ============================================
# 电力交易AI平台 - 一键启动脚本
# 功能：自动安装依赖并启动后端服务
# 使用：双击运行此脚本
# ============================================

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ScriptDir "backend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  电力交易AI平台 - 本地部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python
Write-Host "[1/4] 检查Python环境..." -ForegroundColor Yellow
$pythonCmd = $null
foreach ($cmd in @("python", "python3")) {
    try {
        $result = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "  找到: $result" -ForegroundColor Green
            break
        }
    } catch {}
}
if (-not $pythonCmd) {
    Write-Host "  错误: 未找到Python！" -ForegroundColor Red
    Write-Host "  请先安装Python: https://www.python.org/downloads/" -ForegroundColor Cyan
    Read-Host "按Enter退出"
    exit 1
}

# 设置工作目录
Set-Location $BackendDir

# 复制环境变量配置
$envFile = Join-Path $BackendDir ".env.local"
if (Test-Path $envFile) {
    Copy-Item $envFile (Join-Path $BackendDir ".env") -Force
    Write-Host "[2/4] 已加载本地配置" -ForegroundColor Green
} else {
    Write-Host "[2/4] 使用默认配置" -ForegroundColor Yellow
}

# 创建虚拟环境并安装依赖
Write-Host "[3/4] 安装依赖..." -ForegroundColor Yellow
$VenvDir = Join-Path $BackendDir ".venv"

if (-not (Test-Path $VenvDir)) {
    Write-Host "  创建虚拟环境..." -ForegroundColor Cyan
    & $pythonCmd -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  虚拟环境创建失败！" -ForegroundColor Red
        exit 1
    }
}

$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$PipExe = Join-Path $VenvDir "Scripts\pip.exe"

Write-Host "  安装Python包..." -ForegroundColor Cyan
& $PythonExe -m pip install --upgrade pip --quiet
& $PipExe install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "  依赖安装失败！" -ForegroundColor Red
    exit 1
}
Write-Host "  依赖安装完成" -ForegroundColor Green

# 启动服务
Write-Host "[4/4] 启动服务..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  服务启动中！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  平台地址: http://127.0.0.1:8000/console" -ForegroundColor White
Write-Host "  API文档:   http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  按 Ctrl+C 停止服务" -ForegroundColor Cyan
Write-Host ""

# 打开浏览器
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:8000/console"

# 启动uvicorn
& $PythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
