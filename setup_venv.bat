@echo off
setlocal enabledelayedexpansion

echo =========================================
echo  Blox Fruits 2D - Setup
echo =========================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found.
    echo         Please install Python 3.8+ from https://www.python.org/downloads/
    echo         Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/3] Creating virtual environment ...
if exist "venv" (
    echo       Removing old venv ...
    rmdir /s /q venv
)
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)
echo       Done.
echo.

echo [2/3] Installing packages (pygame, numpy) ...
venv\Scripts\python -m pip install --upgrade pip --quiet
venv\Scripts\python -m pip install "pygame>=2.0.0" "numpy>=1.20.0"
if %errorlevel% neq 0 (
    echo [ERROR] Package installation failed. Check your network connection.
    pause
    exit /b 1
)
echo.

echo [3/3] Verifying installation ...
venv\Scripts\python -c "import pygame; print('  pygame', pygame.__version__, 'OK')"
venv\Scripts\python -c "import numpy;  print('  numpy ', numpy.__version__,  'OK')"

echo.
echo =========================================
echo  Setup complete!
echo  Run run_game.bat to start the game.
echo =========================================
pause
