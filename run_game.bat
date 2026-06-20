@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist venv (
    echo [提示] 虛擬環境不存在，正在自動安裝...
    call setup_venv.bat
)

echo 啟動 Blox Fruits 2D...
venv\Scripts\python main.py
if %errorlevel% neq 0 (
    echo.
    echo [錯誤] 遊戲啟動失敗！錯誤碼: %errorlevel%
    pause
)
