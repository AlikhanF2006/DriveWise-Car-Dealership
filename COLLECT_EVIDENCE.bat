@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo First run the setup script.& pause& exit /b 1)
echo You must have RUN_SERVER.bat running in another window.
".venv\Scripts\python.exe" scripts\collect_evidence.py
pause
