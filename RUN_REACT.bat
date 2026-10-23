@echo off
cd /d "%~dp0server\frontend"
where npm.cmd >nul 2>nul
if errorlevel 1 (echo Node.js is required for React. Install it from nodejs.org & pause & exit /b 1)
echo Please run RUN_SERVER.bat first to start the Django API.
if not exist node_modules call npm.cmd install --no-audit --no-fund
if errorlevel 1 (pause & exit /b 1)
call npm.cmd run dev
pause
