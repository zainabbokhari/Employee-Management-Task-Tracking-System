@echo off
REM Employee Management System - Setup Script for Windows

echo ==========================================
echo   Employee Management System Setup
echo ==========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env file if not exists
if not exist .env (
    echo.
    echo Creating .env file...
    copy .env.example .env
)

REM Initialize database
echo.
echo Initializing database...
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

echo.
echo ==========================================
echo   Setup Complete!
echo ==========================================
echo.
echo To start the application:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate
echo.
echo   2. Run the server:
echo      python -m uvicorn app.main:app --reload
echo.
echo   3. Open in browser:
echo      http://localhost:8000
echo.
echo Default Login Credentials:
echo   Admin:    admin@company.com / admin123
echo   Manager:  manager@company.com / manager123
echo   Employee: employee@company.com / employee123
echo.
echo ==========================================
echo.

REM Ask if user wants to start now
set /p START_NOW="Start the application now? (y/n): "
if /i "%START_NOW%"=="y" (
    echo.
    echo Starting server...
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
)

pause
