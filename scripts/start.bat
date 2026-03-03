@echo off
title Zetevnia AI Server
cd /d "%~dp0\.."

echo.
echo  ========================================
echo   ZETEVNIA AI SUNUCUSU
echo  ========================================
echo.
echo   Kapatmak icin: Ctrl + C
echo.
echo  ========================================
echo.

call venv\Scripts\activate.bat 2>nul

python -m app.main

pause
