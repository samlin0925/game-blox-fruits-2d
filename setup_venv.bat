@echo off
chcp 65001 >nul
echo =========================================
echo  Blox Fruits 2D - 環境安裝程式
echo =========================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python！請先安裝 Python 3.8 以上版本。
    echo 下載網址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 建立虛擬環境 (venv)...
python -m venv venv
if %errorlevel% neq 0 (
    echo [錯誤] 建立虛擬環境失敗！
    pause
    exit /b 1
)

echo [2/3] 安裝依賴套件 (pygame, numpy)...
venv\Scripts\pip install --upgrade pip -q
venv\Scripts\pip install pygame>=2.0.0 numpy>=1.20.0
if %errorlevel% neq 0 (
    echo [錯誤] 安裝套件失敗！請檢查網路連線。
    pause
    exit /b 1
)

echo [3/3] 確認安裝...
venv\Scripts\python -c "import pygame; print(f'  pygame {pygame.__version__} OK')"
venv\Scripts\python -c "import numpy; print(f'  numpy {numpy.__version__} OK')"

echo.
echo =========================================
echo  安裝完成！執行 run_game.bat 開始遊戲
echo =========================================
pause
