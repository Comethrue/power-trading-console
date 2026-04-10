# UTF-8 BOM - required for Chinese text in Windows PowerShell 5.1
# PowerGrid - start frontend + backend
# Usage: .\start-all.ps1   or   .\start-all.ps1 -SkipBuild

param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host ""
Write-Host "  PowerGrid Trading Console - Full Stack" -ForegroundColor Cyan
Write-Host ""

$runFrontend = $true
$runBackend = $true

if ($args.Count -gt 0) {
    $mode = $args[0].ToLower()
    if ($mode -eq "backend" -or $mode -eq "-b") { $runFrontend = $false }
    if ($mode -eq "frontend" -or $mode -eq "-f") { $runBackend = $false }
}

if ($runFrontend) {
    Write-Host "[Frontend] Checking Node.js..." -ForegroundColor Yellow
    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
    if (-not $nodeCmd) {
        Write-Host "  Node.js not found. Frontend skipped." -ForegroundColor Red
        $runFrontend = $false
    }
    else {
        Write-Host "  Node: $(node --version)" -ForegroundColor Green
        Write-Host "  npm: $(npm --version)" -ForegroundColor Green
    }
}

if ($runBackend) {
    Write-Host "[Backend] Checking Python..." -ForegroundColor Yellow
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pyCmd) { $pyCmd = Get-Command py -ErrorAction SilentlyContinue }
    if (-not $pyCmd) {
        Write-Host "  Python not found. Backend skipped." -ForegroundColor Red
        $runBackend = $false
    }
    else {
        Write-Host "  Python: $(python --version 2>&1)" -ForegroundColor Green
    }
}

if ($runFrontend) {
    Write-Host "[Frontend] npm dependencies..." -ForegroundColor Yellow
    if (-not (Test-Path "$ProjectRoot\frontend\node_modules")) {
        Write-Host "  Running npm install..." -ForegroundColor White
        Push-Location "$ProjectRoot\frontend"
        try {
            npm install
            if ($LASTEXITCODE -ne 0) {
                Write-Host "  npm install failed. Frontend skipped." -ForegroundColor Red
                $runFrontend = $false
            }
            else {
                Write-Host "  npm install OK" -ForegroundColor Green
            }
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Host "  node_modules exists, skip install" -ForegroundColor Gray
    }

    $distIndex = "$ProjectRoot\frontend\dist\index.html"
    $needBuild = $true
    if (Test-Path $distIndex) {
        $idx = Get-Content -LiteralPath $distIndex -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($idx -and $idx -notmatch '/src/main\.js') { $needBuild = $false }
    }
    if ($needBuild -and -not $SkipBuild) {
        Write-Host "[Frontend] npm run build..." -ForegroundColor Yellow
        Push-Location "$ProjectRoot\frontend"
        try {
            npm run build
            if ($LASTEXITCODE -ne 0) {
                Write-Host "  Build failed; /console on backend may 404" -ForegroundColor Red
            }
            else {
                Write-Host "  Build OK" -ForegroundColor Green
            }
        }
        finally {
            Pop-Location
        }
    }
    elseif ($needBuild -and $SkipBuild) {
        Write-Host "[Frontend] Skipped build (-SkipBuild). Run npm run build if you need /console on :8000" -ForegroundColor Gray
    }
}

if ($runBackend) {
    Write-Host ""
    Write-Host "[Backend] Starting FastAPI..." -ForegroundColor Cyan
    Write-Host "  http://127.0.0.1:8000" -ForegroundColor Gray
    Write-Host "  http://127.0.0.1:8000/docs" -ForegroundColor Gray
    Write-Host ""

    $backendScript = @"
`$ErrorActionPreference = "Stop"
Set-Location "$ProjectRoot\backend"
`$venvCpy313 = "$ProjectRoot\backend\.venv_cpy313\Scripts\python.exe"
`$venvPy = "$ProjectRoot\backend\.venv\Scripts\python.exe"
`$venv312 = "$ProjectRoot\backend\.venv312\Scripts\python.exe"
`$dbPath = "$ProjectRoot\backend\power_trading.db"
`$csvPath = "$ProjectRoot\backend\data\sample_market_prices.csv"
`$marketScript = "$ProjectRoot\backend\scripts\import_market_data.py"
if ((Test-Path `$dbPath) -and (Test-Path `$csvPath)) {
    `$pyExec = `$null
    if (Test-Path `$venvCpy313) { `$pyExec = `$venvCpy313 }
    elseif (Test-Path `$venvPy) { `$pyExec = `$venvPy }
    elseif (Test-Path `$venv312) { `$pyExec = `$venv312 }
    elseif (Get-Command py -ErrorAction SilentlyContinue) { `$pyExec = "py" }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { `$pyExec = "python" }
    if (`$pyExec) {
        & `$pyExec `$marketScript --db `$dbPath --csv `$csvPath --source "start-import" 2>&1 | Out-Null
    }
}
if (Test-Path `$venvCpy313) {
    & `$venvCpy313 run_dev.py
}
elseif (Test-Path `$venvPy) {
    & `$venvPy run_dev.py
}
elseif (Test-Path `$venv312) {
    & `$venv312 run_dev.py
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 run_dev.py
}
else {
    python run_dev.py
}
"@

    $null = Start-Job -ScriptBlock {
        param($s)
        Invoke-Expression $s
    } -ArgumentList $backendScript
}

if ($runBackend) {
    Write-Host "  Waiting for backend..." -ForegroundColor Gray
    Start-Sleep -Seconds 3
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($resp.StatusCode -eq 200) {
            Write-Host "  Backend OK" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  Backend may still be starting..." -ForegroundColor Gray
    }
}

if ($runFrontend) {
    Write-Host ""
    Write-Host "[Frontend] Starting Vite..." -ForegroundColor Cyan
    Write-Host "  http://localhost:5173/console/" -ForegroundColor Gray
    Write-Host ""
    Push-Location "$ProjectRoot\frontend"
    try {
        npm run dev
    }
    finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "Done." -ForegroundColor Cyan
