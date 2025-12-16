# FMQE Environment Setup Script
# Run this script in PowerShell as Administrator
# Usage: .\setup_environment.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "FMQE - FileMaker to PostgreSQL Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ROOT = "C:\projects\duft"
$FMQE_DIR = "$PROJECT_ROOT\fmqe"
$JAVA_DIR = "$PROJECT_ROOT\java"

# Step 1: Check Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = py -3.12 --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python 3.12 not found. Please install from python.org" -ForegroundColor Red
    exit 1
}

# Step 2: Install pip if needed
Write-Host "[2/5] Checking pip..." -ForegroundColor Yellow
$pipCheck = py -3.12 -m pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installing pip..." -ForegroundColor Yellow
    py -3.12 -m ensurepip --upgrade
}
Write-Host "  pip is ready" -ForegroundColor Green

# Step 3: Install Python packages
Write-Host "[3/5] Installing Python packages..." -ForegroundColor Yellow
$packages = @("pandas", "jaydebeapi", "sqlalchemy", "psycopg2-binary", "jupyter", "ipykernel", "jpype1")
foreach ($pkg in $packages) {
    Write-Host "  Installing $pkg..." -ForegroundColor Gray
    py -3.12 -m pip install $pkg --quiet
}
Write-Host "  All packages installed" -ForegroundColor Green

# Step 4: Install Java if needed
Write-Host "[4/5] Checking Java..." -ForegroundColor Yellow
$javaPath = "$JAVA_DIR\jdk-21.0.4+7\bin\java.exe"
if (Test-Path $javaPath) {
    Write-Host "  Java already installed" -ForegroundColor Green
} else {
    Write-Host "  Downloading OpenJDK 21..." -ForegroundColor Yellow
    $javaUrl = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.4%2B7/OpenJDK21U-jdk_x64_windows_hotspot_21.0.4_7.zip"
    $zipPath = "$PROJECT_ROOT\openjdk21.zip"

    Invoke-WebRequest -Uri $javaUrl -OutFile $zipPath
    Write-Host "  Extracting Java..." -ForegroundColor Yellow
    Expand-Archive -Path $zipPath -DestinationPath $JAVA_DIR -Force
    Remove-Item $zipPath
    Write-Host "  Java installed" -ForegroundColor Green
}

# Step 5: Copy JDBC driver
Write-Host "[5/5] Setting up JDBC driver..." -ForegroundColor Yellow
$jdbcSource = "$PROJECT_ROOT\duft-config\system\data_tasks\fmjdbc.jar"
$jdbcDest = "$FMQE_DIR\fmjdbc.jar"

if (Test-Path $jdbcSource) {
    Copy-Item $jdbcSource $jdbcDest -Force
    Write-Host "  JDBC driver copied" -ForegroundColor Green
} elseif (Test-Path $jdbcDest) {
    Write-Host "  JDBC driver already present" -ForegroundColor Green
} else {
    Write-Host "  WARNING: fmjdbc.jar not found. Copy manually from FileMaker Server." -ForegroundColor Yellow
}

# Verification
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Running Verification..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

py -3.12 "$FMQE_DIR\test_setup.py"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Ensure FileMaker Server is running with JDBC enabled" -ForegroundColor Gray
Write-Host "2. Run: cd $FMQE_DIR" -ForegroundColor Gray
Write-Host "3. Run: py -3.12 -m jupyter notebook fmqe_import.ipynb" -ForegroundColor Gray
Write-Host ""
