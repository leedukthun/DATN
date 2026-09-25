[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Venv = Join-Path $Backend ".venv"
$VenvPython = Join-Path $Venv "Scripts\python.exe"
$BackendEnv = Join-Path $Backend ".env"
$FrontendEnv = Join-Path $Frontend ".env"
$ModelPath = Join-Path $Backend "models\best.pt"

function Write-Section([string]$Message) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Assert-LastExitCode([string]$Message) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Message (exit code: $LASTEXITCODE)"
    }
}

function Get-CombinedHash([string[]]$Paths) {
    $hashes = foreach ($Path in $Paths) {
        if (Test-Path $Path) {
            (Get-FileHash -Algorithm SHA256 -Path $Path).Hash
        }
    }
    return ($hashes -join "|")
}

Write-Section "CHUẨN BỊ MÔI TRƯỜNG VS CODE"

if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    throw "Không tìm thấy npm.cmd. Hãy cài Node.js LTS rồi mở lại VS Code."
}

$PythonCommand = $null
$PythonArguments = @()

if (Get-Command py.exe -ErrorAction SilentlyContinue) {
    & py.exe "-3.11" -V *> $null
    if ($LASTEXITCODE -eq 0) {
        $PythonCommand = "py.exe"
        $PythonArguments = @("-3.11")
    } else {
        & py.exe "-3" -V *> $null
        if ($LASTEXITCODE -eq 0) {
            $PythonCommand = "py.exe"
            $PythonArguments = @("-3")
        }
    }
}

if (-not $PythonCommand -and (Get-Command python.exe -ErrorAction SilentlyContinue)) {
    & python.exe -c "import sys; raise SystemExit(0 if sys.version_info.major == 3 else 1)" *> $null
    if ($LASTEXITCODE -eq 0) {
        $PythonCommand = "python.exe"
    }
}

if (-not $PythonCommand) {
    throw "Không tìm thấy Python 3. Khuyến nghị cài Python 3.11 x64 và chọn 'Add Python to PATH'."
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "[1/6] Tạo virtual environment backend\.venv ..." -ForegroundColor Yellow
    Push-Location $Backend
    try {
        & $PythonCommand @PythonArguments -m venv ".venv"
        Assert-LastExitCode "Không thể tạo Python virtual environment"
    } finally {
        Pop-Location
    }
} else {
    Write-Host "[1/6] Virtual environment đã tồn tại." -ForegroundColor Green
}

if (-not (Test-Path $BackendEnv)) {
    Copy-Item (Join-Path $Backend ".env.example") $BackendEnv
    Write-Host "[2/6] Đã tạo backend\.env từ .env.example." -ForegroundColor Green
} else {
    Write-Host "[2/6] backend\.env đã tồn tại." -ForegroundColor Green
}

if (-not (Test-Path $FrontendEnv)) {
    Copy-Item (Join-Path $Frontend ".env.example") $FrontendEnv
    Write-Host "[3/6] Đã tạo frontend\.env từ .env.example." -ForegroundColor Green
} else {
    Write-Host "[3/6] frontend\.env đã tồn tại." -ForegroundColor Green
}

$RequirementFiles = @(
    (Join-Path $Backend "requirements.txt"),
    (Join-Path $Backend "requirements-dev.txt")
)
$RequirementHash = Get-CombinedHash $RequirementFiles
$RequirementMarker = Join-Path $Venv ".requirements.sha256"
$InstalledRequirementHash = if (Test-Path $RequirementMarker) {
    (Get-Content -Raw $RequirementMarker).Trim()
} else {
    ""
}

if ($Force -or ($RequirementHash -ne $InstalledRequirementHash)) {
    Write-Host "[4/6] Cài đặt/cập nhật thư viện Python ..." -ForegroundColor Yellow
    & $VenvPython -m pip install --upgrade pip
    Assert-LastExitCode "Không thể nâng cấp pip"
    & $VenvPython -m pip install -r (Join-Path $Backend "requirements-dev.txt")
    Assert-LastExitCode "Không thể cài thư viện Python"
    [System.IO.File]::WriteAllText($RequirementMarker, $RequirementHash)
} else {
    Write-Host "[4/6] Thư viện Python đã đúng phiên bản yêu cầu." -ForegroundColor Green
}

$PackageFiles = @((Join-Path $Frontend "package.json"))
$PackageLock = Join-Path $Frontend "package-lock.json"
if (Test-Path $PackageLock) {
    $PackageFiles += $PackageLock
}
$PackageHash = Get-CombinedHash $PackageFiles
$NodeModules = Join-Path $Frontend "node_modules"
$NodeMarker = Join-Path $NodeModules ".package.sha256"
$InstalledPackageHash = if (Test-Path $NodeMarker) {
    (Get-Content -Raw $NodeMarker).Trim()
} else {
    ""
}

if ($Force -or (-not (Test-Path $NodeModules)) -or ($PackageHash -ne $InstalledPackageHash)) {
    Write-Host "[5/6] Cài đặt/cập nhật thư viện frontend ..." -ForegroundColor Yellow
    Push-Location $Frontend
    try {
        & npm.cmd install --no-audit --no-fund
        Assert-LastExitCode "Không thể chạy npm install"
    } finally {
        Pop-Location
    }

    $PackageFiles = @((Join-Path $Frontend "package.json"))
    if (Test-Path $PackageLock) {
        $PackageFiles += $PackageLock
    }
    $PackageHash = Get-CombinedHash $PackageFiles
    if (-not (Test-Path $NodeModules)) {
        throw "npm install hoàn tất nhưng không tìm thấy frontend\node_modules."
    }
    [System.IO.File]::WriteAllText($NodeMarker, $PackageHash)
} else {
    Write-Host "[5/6] Thư viện frontend đã đúng phiên bản yêu cầu." -ForegroundColor Green
}

if (-not (Test-Path $ModelPath)) {
    throw "Không tìm thấy model: $ModelPath"
}

Write-Host "[6/6] Kiểm tra import backend và model ..." -ForegroundColor Yellow
Push-Location $Backend
try {
    & $VenvPython "verify_setup.py"
    Assert-LastExitCode "Kiểm tra cấu hình backend thất bại"
} finally {
    Pop-Location
}

Write-Section "MÔI TRƯỜNG ĐÃ SẴN SÀNG"
Write-Host "Nhấn F5 và chọn: Toàn hệ thống: Backend + Frontend" -ForegroundColor Green
Write-Host "Frontend : http://localhost:5173"
Write-Host "API docs : http://localhost:8000/docs"
