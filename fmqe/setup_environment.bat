@echo off
REM FMQE Environment Setup Script (Batch version)
REM Double-click this file to run setup

echo ============================================
echo FMQE - FileMaker to PostgreSQL Setup
echo ============================================
echo.

set PROJECT_ROOT=C:\projects\duft
set FMQE_DIR=%PROJECT_ROOT%\fmqe
set JAVA_DIR=%PROJECT_ROOT%\java

echo [1/5] Checking Python...
py -3.12 --version
if errorlevel 1 (
    echo ERROR: Python 3.12 not found. Please install from python.org
    pause
    exit /b 1
)

echo [2/5] Installing pip if needed...
py -3.12 -m ensurepip --upgrade 2>nul

echo [3/5] Installing Python packages...
py -3.12 -m pip install pandas jaydebeapi sqlalchemy psycopg2-binary jupyter ipykernel jpype1 --quiet
echo   Packages installed.

echo [4/5] Checking Java...
if exist "%JAVA_DIR%\jdk-21.0.4+7\bin\java.exe" (
    echo   Java already installed.
) else (
    echo   Java not found. Please run setup_environment.ps1 in PowerShell to download Java.
    echo   Or manually download OpenJDK 21 from https://adoptium.net/
)

echo [5/5] Checking JDBC driver...
if exist "%FMQE_DIR%\fmjdbc.jar" (
    echo   JDBC driver found.
) else (
    echo   WARNING: fmjdbc.jar not found in %FMQE_DIR%
    echo   Copy from FileMaker Server installation.
)

echo.
echo ============================================
echo Running Verification...
echo ============================================
py -3.12 "%FMQE_DIR%\test_setup.py"

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Ensure FileMaker Server is running with JDBC enabled
echo 2. Run: cd %FMQE_DIR%
echo 3. Run: py -3.12 -m jupyter notebook fmqe_import.ipynb
echo.
pause
