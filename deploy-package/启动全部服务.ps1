# ============================================
# 电力交易AI平台 - Windows一键启动脚本
# ============================================
# 功能：自动安装依赖、启动后端和前端服务
# 使用：双击运行此脚本

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ScriptDir "backend"
$FrontendDir = Join-Path $ScriptDir "frontend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 电力交易AI平台 - 本地部署启动器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python环境
Write-Host "[1/5] 检查Python环境..." -ForegroundColor Yellow
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
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
    Write-Host "  错误: 未找到Python，请先安装Python 3.10+" -ForegroundColor Red
    Write-Host "  下载地址: https://www.python.org/downloads/" -ForegroundColor Cyan
    Read-Host "按Enter键退出"
    exit 1
}

# 检查Node.js环境
Write-Host "[2/5] 检查Node.js环境..." -ForegroundColor Yellow
$nodeCmd = $null
foreach ($cmd in @("node", "nodejs")) {
    try {
        $result = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $nodeCmd = $cmd
            Write-Host "  找到: $result" -ForegroundColor Green
            break
        }
    } catch {}
}
if (-not $nodeCmd) {
    Write-Host "  警告: 未找到Node.js，将无法启动前端开发服务器" -ForegroundColor Yellow
    Write-Host "  如需前端，请先安装: https://nodejs.org/" -ForegroundColor Cyan
}

# 安装后端依赖
Write-Host "[3/5] 安装后端依赖..." -ForegroundColor Yellow
Set-Location $BackendDir
if (Test-Path ".venv") {
    Write-Host "  已检测到虚拟环境，跳过安装" -ForegroundColor Cyan
} else {
    & $pythonCmd -m venv .venv
    & .\.venv\Scripts\Activate.ps1
    & $pythonCmd -m pip install --upgrade pip
    & $pythonCmd -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  后端依赖安装失败" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
}
Write-Host "  后端依赖就绪" -ForegroundColor Green

# 启动后端服务
Write-Host "[4/5] 启动后端服务..." -ForegroundColor Yellow
$backendEnv = Join-Path $BackendDir ".env.local"
if (Test-Path $backendEnv) {
    Copy-Item $backendEnv (Join-Path $BackendDir ".env") -Force
    Write-Host "  已加载本地配置" -ForegroundColor Cyan
}

$backendJob = Start-Job -ScriptBlock {
    param($dir, $venv)
    Set-Location $dir
    & "$venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
} -ArgumentList $BackendDir, (Join-Path $BackendDir ".venv")

Start-Sleep -Seconds 3
Write-Host "  后端服务启动中 (http://127.0.0.1:8000)" -ForegroundColor Green

# 启动前端服务
if ($nodeCmd) {
    Write-Host "[5/5] 启动前端服务..." -ForegroundColor Yellow
    Set-Location $FrontendDir

    # 创建本地环境配置
    $frontendEnv = @"
# 本地开发配置
VITE_BASE_URL=/
VITE_API_BASE=http://127.0.0.1:8000
"@
    Set-Content -Path ".env.local" -Value $frontendEnv -Encoding UTF8

    # 使用vite启动
    if (Test-Path "node_modules") {
        $viteJob = Start-Job -ScriptBlock {
            param($dir)
            Set-Location $dir
            & npm run dev
        } -ArgumentList $FrontendDir
        Write-Host "  前端服务启动中 (http://localhost:5173)" -ForegroundColor Green
    } else {
        Write-Host "  未安装前端依赖，跳过前端启动" -ForegroundColor Yellow
        Write-Host "  提示: 进入frontend目录运行 npm install" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " 服务已启动！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host " 后端API: http://127.0.0.1:8000" -ForegroundColor White
if ($nodeCmd) {
    Write-Host " 前端界面: http://localhost:5173" -ForegroundColor White
} else {
    Write-Host " 前端界面: 请在浏览器打开 frontend/dist/index.html" -ForegroundColor White
}
Write-Host ""
Write-Host " 按 Ctrl+C 停止服务" -ForegroundColor Cyan
Write-Host ""

# 等待用户中断
try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    Write-Host ""
    Write-Host "正在停止服务..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job -Job $viteJob -ErrorAction SilentlyContinue
    Remove-Job -Job $backendJob, $viteJob -Force -ErrorAction SilentlyContinue
    Write-Host "服务已停止" -ForegroundColor Green
}
