@echo off
cd /d "%~dp0"
title Installing Dependencies...

echo ======================================================
echo          Installing/Updating Dependencies...
echo ======================================================
echo.

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

echo.
echo [SUCCESS] Dependencies installed successfully!
echo.
pause
