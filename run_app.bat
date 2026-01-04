@echo off
cd /d "%~dp0"
title 5xGames Data Hub Launcher

echo ======================================================
echo          Starting 5xGames Data Hub...
echo ======================================================
echo.

:: Use python module to run streamlit to ensure we use the correct environment
python -m streamlit run main.py

:: If the above failed
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application failed to start.
    pause
)
