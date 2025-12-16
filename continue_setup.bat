@echo off
echo ========================================
echo DUFT Project - Automated Setup Script
echo ========================================
echo.
echo This script will:
echo 1. Create Python 3.12 virtual environment
echo 2. Install Python dependencies
echo 3. Set up PostgreSQL database
echo 4. Run Django migrations
echo 5. Install frontend dependencies
echo.
echo Press Ctrl+C to cancel, or
pause
echo.

echo Step 1: Removing old Python 3.13 virtual environment...
if exist .venv rmdir /s /q .venv
echo.

echo Step 2: Creating new virtual environment with Python 3.12...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Make sure Python 3.12 is installed and in PATH
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

echo Step 3: Activating virtual environment...
call .venv\Scripts\activate.bat
echo.

echo Step 4: Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Step 5: Installing Python dependencies (this may take 5-10 minutes)...
python -m pip install -r duft-server\requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Python dependencies installed
echo.

echo Step 6: Creating PostgreSQL database...
psql -U postgres -c "CREATE DATABASE qe_data;"
if %errorlevel% neq 0 (
    echo Note: Database might already exist or connection failed
    echo You may need to enter the postgres password
)
echo.

echo Step 7: Running Django migrations...
python duft-server\manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Migrations failed
    echo Check your PostgreSQL connection settings
    pause
    exit /b 1
)
echo [OK] Migrations completed
echo.

echo Step 8: Installing frontend dependencies...
cd duft-ui
call yarn install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] Frontend dependencies installed
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create a superuser account:
echo    .venv\Scripts\python.exe duft-server\manage.py createsuperuser
echo.
echo 2. Start the backend server:
echo    .venv\Scripts\python.exe duft-server\manage.py runserver
echo.
echo 3. In a new terminal, start the frontend:
echo    cd duft-ui
echo    yarn dev
echo.
echo 4. Open browser: http://localhost:3031
echo ========================================
pause
