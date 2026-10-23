@echo off
cd /d "%~dp0microservices\dealer_api"
where npm.cmd >nul 2>nul
if errorlevel 1 (echo Node.js is required. & pause & exit /b 1)
if not exist node_modules call npm.cmd install --no-audit --no-fund
if errorlevel 1 (pause & exit /b 1)
call npm.cmd start
pause
