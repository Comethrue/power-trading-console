# PowerShell 5+: UTF-8 with BOM recommended if you use Chinese comments in some editors.
# Deploy: push this repo to GitHub (triggers GitHub Pages workflow).

# ============ config ============
$githubUsername = "YOUR_GITHUB_USERNAME"
$repoName = "power-trading-console"

# ============ main ============
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " GitHub deploy script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path ".git")) {
    Write-Host "[1/4] git init..." -ForegroundColor Yellow
    git init
    git branch -M main
}
else {
    Write-Host "[1/4] .git exists, skip init" -ForegroundColor Green
}

$remoteUrl = "https://github.com/$githubUsername/$repoName.git"
Write-Host "[2/4] remote: $remoteUrl" -ForegroundColor Yellow

$currentRemote = $null
$rawOrigin = & git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($rawOrigin)) {
    $currentRemote = $rawOrigin.Trim()
}

if ([string]::IsNullOrWhiteSpace($currentRemote)) {
    git remote add origin $remoteUrl
    Write-Host "  added origin" -ForegroundColor Green
}
elseif ($currentRemote -ne $remoteUrl) {
    Write-Host "  current origin: $currentRemote" -ForegroundColor Cyan
    $change = Read-Host "  Update origin to new URL? (y/n)"
    if ($change -eq "y") {
        git remote set-url origin $remoteUrl
        Write-Host "  origin updated" -ForegroundColor Green
    }
}
else {
    Write-Host "  origin OK" -ForegroundColor Green
}

Write-Host "[3/4] git add..." -ForegroundColor Yellow
git add .

$status = @(git status --porcelain)
if ($status.Count -eq 0) {
    Write-Host "  nothing to commit" -ForegroundColor Cyan
}
else {
    Write-Host "  changes:" -ForegroundColor Cyan
    git status --short
    Write-Host ""
    $commitMsg = Read-Host "  Commit message (Enter = default)"
    if ([string]::IsNullOrWhiteSpace($commitMsg)) {
        $commitMsg = "Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    }
    Write-Host "  committing..." -ForegroundColor Yellow
    git commit -m $commitMsg
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  git commit failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "  committed" -ForegroundColor Green
}

Write-Host "[4/4] git push..." -ForegroundColor Yellow
Write-Host "  Tip: first push may need GitHub auth (PAT or credential helper)." -ForegroundColor Cyan
Write-Host ""

git push -u origin main
$pushCode = $LASTEXITCODE

if ($pushCode -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host " Push OK" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host " Check Render for API; Actions will build Pages." -ForegroundColor Cyan
    Write-Host " Frontend: https://$githubUsername.github.io/$repoName/" -ForegroundColor White
}
else {
    Write-Host ""
    Write-Host "Push failed (exit $pushCode). Check network and GitHub auth." -ForegroundColor Red
    exit $pushCode
}
