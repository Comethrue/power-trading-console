# 一键启动电力交易平台 API（默认 http://0.0.0.0:8000）
# 启动后在浏览器打开：http://127.0.0.1:8000/console/

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontend = Join-Path $root "frontend"
$distIndex = Join-Path $frontend "dist\index.html"

function Test-DistIndexOk {
    if (-not (Test-Path $distIndex)) { return $false }
    $raw = Get-Content -LiteralPath $distIndex -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    if (-not $raw) { return $false }
    if ($raw -match '/src/main\.js') { return $false }
    return $true
}

if (-not (Test-DistIndexOk)) {
    Write-Host "[前端] 需要先构建 dist 才能访问 /console/（否则会出现 GET /src/main.js 404）" -ForegroundColor Yellow
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Host "未找到 Node.js。请在 frontend 目录执行: npm install && npm run build" -ForegroundColor Red
        exit 1
    }
    Push-Location $frontend
    try {
        if (-not (Test-Path "node_modules")) { npm install; if ($LASTEXITCODE -ne 0) { throw "npm install 失败" } }
        npm run build
        if ($LASTEXITCODE -ne 0) { throw "npm run build 失败" }
    } finally {
        Pop-Location
    }
    Write-Host "[前端] 构建完成" -ForegroundColor Green
}

Set-Location (Join-Path $root "backend")

# 优先使用标准 CPython 3.13 虚拟环境（勿用 python3.13t 创建 venv，否则 pydantic-core 无法加载）
$venvCpy313 = Join-Path $root "backend\.venv_cpy313\Scripts\python.exe"
$venvPy = Join-Path $root "backend\.venv\Scripts\python.exe"
$venv312 = Join-Path $root "backend\.venv312\Scripts\python.exe"

# 自动导入示例市场价格数据
$dbPath = Join-Path $root "backend\power_trading.db"
$csvPath = Join-Path $root "backend\data\sample_market_prices.csv"
$marketScript = Join-Path $root "backend\scripts\import_market_data.py"

if ((Test-Path $dbPath) -and (Test-Path $csvPath)) {
    $pythonExec = $null
    if (Test-Path $venvCpy313) { $pythonExec = $venvCpy313 }
    elseif (Test-Path $venvPy) { $pythonExec = $venvPy }
    elseif (Test-Path $venv312) { $pythonExec = $venv312 }
    elseif (Get-Command py -ErrorAction SilentlyContinue) { $pythonExec = "py" }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { $pythonExec = "python" }

    if ($pythonExec) {
        $prevOut = & $pythonExec $marketScript --db $dbPath --csv $csvPath --source "示例导入" 2>&1
        if ($prevOut) { Write-Host "[startup] $prevOut" -ForegroundColor Gray }
    }
}

if (Test-Path $venvCpy313) {
    & $venvCpy313 (Join-Path (Get-Location) "run_dev.py")
}
elseif (Test-Path $venvPy) {
    & $venvPy (Join-Path (Get-Location) "run_dev.py")
}
elseif (Test-Path $venv312) {
    & $venv312 (Join-Path (Get-Location) "run_dev.py")
}
else {
    Write-Host "未找到 backend\.venv，尝试使用系统 Python（py -3 或 python）。" -ForegroundColor Yellow
    Write-Host "建议先执行: cd backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt" -ForegroundColor Gray

    $runDev = Join-Path (Get-Location) "run_dev.py"
    $uvicornStarted = $false
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -3 $runDev
        $uvicornStarted = $true
    }
    if (-not $uvicornStarted) {
        if (Get-Command python -ErrorAction SilentlyContinue) {
            python $runDev
            $uvicornStarted = $true
        }
    }
    if (-not $uvicornStarted) {
        Write-Host "未找到 Python，请先安装 Python 3.11+ 并加入 PATH。" -ForegroundColor Red
        exit 1
    }
}
