@echo off
echo ================================================
echo   排球冒险 - AI训练系统 (Flask Web版本)
echo ================================================
echo.

REM 激活虚拟环境(如果存在)
if exist "venv\Scripts\activate.bat" (
    echo 正在激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 启动Flask服务器
echo 正在启动Web服务器...
python run_flask.py

pause

