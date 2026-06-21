@echo off
setlocal enabledelayedexpansion

echo ============================================
echo  Blox Fruits 2D - Build Script v1.1.0
echo  Author: Sam Lin
echo ============================================
echo.

REM Move to project root (parent of release\)
cd /d "%~dp0.."
if %errorlevel% neq 0 (
    echo [ERROR] Cannot change to project root directory.
    pause
    exit /b 1
)
echo [INFO] Working directory: %CD%
echo.

REM Check virtual environment
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo         Please run setup_venv.bat first.
    pause
    exit /b 1
)

REM Step 1: Install / verify PyInstaller and Pillow
echo [1/4] Installing PyInstaller + Pillow ...
venv\Scripts\python -m pip install pyinstaller pillow --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install packages. Check your network connection.
    pause
    exit /b 1
)
echo       Done.
echo.

REM Step 2: Generate icon
echo [2/4] Generating icon.ico ...
venv\Scripts\python release\generate_icon.py
if %errorlevel% neq 0 (
    echo [WARNING] Icon generation failed. Packaging will continue without icon.
)
echo.

REM Step 3: PyInstaller packaging
echo [3/4] Packaging with PyInstaller ...
venv\Scripts\python -m PyInstaller release\bloxfruits.spec --clean --noconfirm ^
    --workpath release\build
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller failed. See output above for details.
    pause
    exit /b 1
)
echo.

REM Step 4: Show result
echo [4/4] Build complete!
echo.
set "EXE=release\dist\BloxFruits2D.exe"
if exist "%EXE%" (
    for %%F in ("%EXE%") do (
        set /a SIZE_KB=%%~zF / 1024
        echo  Output : %CD%\%EXE%
        echo  Size   : !SIZE_KB! KB
    )
) else (
    echo [WARNING] Output file not found: %EXE%
)
echo.
echo ============================================
echo  SUCCESS - BloxFruits2D.exe is ready!
echo  Double-click dist\BloxFruits2D.exe to run.
echo ============================================
pause
