# 启动后端；若未构建前端则自动执行 npm run build（避免 /console 返回开发版 index 导致 GET /src/main.js 404）
$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$projectRoot = Split-Path $here -Parent
$frontend = Join-Path $projectRoot "frontend"
$distIndex = Join-Path $frontend "dist\index.html"

function Test-DistIndexOk {
    if (-not (Test-Path $distIndex)) { return $false }
    $raw = Get-Content -LiteralPath $distIndex -Raw -Encoding UTF8
    if ($raw -match '/src/main\.js') { return $false }
    return $true
}

if (-not (Test-DistIndexOk)) {
    Write-Host "[前端] dist 缺失或为开发版 index，正在构建（npm run build）..." -ForegroundColor Yellow
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Host "未找到 Node.js，无法构建。请安装 Node 后在 frontend 目录执行: npm install && npm run build" -ForegroundColor Red
        exit 1
    }
    Push-Location $frontend
    try {
        if (-not (Test-Path "node_modules")) {
            npm install
            if ($LASTEXITCODE -ne 0) { throw "npm install 失败" }
        }
        npm run build
        if ($LASTEXITCODE -ne 0) { throw "npm run build 失败" }
    } finally {
        Pop-Location
    }
    Write-Host "[前端] 构建完成" -ForegroundColor Green
}

Set-Location $here

$venvCpy313 = Join-Path $here ".venv_cpy313\Scripts\python.exe"
$venvPy = Join-Path $here ".venv\Scripts\python.exe"
$venv312 = Join-Path $here ".venv312\Scripts\python.exe"
$runDev = Join-Path $here "run_dev.py"

if (Test-Path $venvCpy313) {
    & $venvCpy313 $runDev
}
elseif (Test-Path $venvPy) {
    & $venvPy $runDev
}
elseif (Test-Path $venv312) {
    & $venv312 $runDev
}
else {
    python $runDev
}
