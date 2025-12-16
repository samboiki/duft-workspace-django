# DUFT Project - Install Prerequisites via Chocolatey
# Run this in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DUFT Project - Installing Prerequisites" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Installing Python 3.12..." -ForegroundColor Green
choco install python312 --version=3.12.10 -y --force

Write-Host ""
Write-Host "Installing PostgreSQL 15..." -ForegroundColor Green
choco install postgresql15 --params '/Password:postgres' --version=15.14 -y --force

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Close this PowerShell window" -ForegroundColor White
Write-Host "2. Open a NEW Command Prompt (to refresh PATH)" -ForegroundColor White
Write-Host "3. Run: cd C:\projects\duft" -ForegroundColor White
Write-Host "4. Run: verify_installation.bat" -ForegroundColor White
Write-Host ""
pause
