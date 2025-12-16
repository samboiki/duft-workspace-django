@echo off
echo ========================================
echo DUFT Project - Installation Verification
echo ========================================
echo.

echo Checking Python 3.12...
python --version 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] Python not found in PATH
) else (
    echo [OK] Python found
)
echo.

echo Checking PostgreSQL...
psql --version 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] PostgreSQL psql not found in PATH
    echo Note: You may need to add PostgreSQL bin directory to PATH
    echo Usually: C:\Program Files\PostgreSQL\15\bin
) else (
    echo [OK] PostgreSQL found
)
echo.

echo Checking Node.js...
node --version 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] Node.js not found
) else (
    echo [OK] Node.js found
)
echo.

echo Checking Yarn...
yarn --version 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] Yarn not found
) else (
    echo [OK] Yarn found
)
echo.

echo ========================================
echo.
echo If all checks pass, you're ready to continue!
echo If any fail, please install the missing software.
echo.
echo See SETUP_GUIDE.md for detailed instructions.
echo ========================================
pause
