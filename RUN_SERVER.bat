@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Setup has not completed. First run RUN_AND_PUSH.bat from the ZIP folder.
  pause
  exit /b 1
)
echo.
echo Django website: http://127.0.0.1:8000/
echo Django Admin:   http://127.0.0.1:8000/admin/
echo Real server log: .evidence\django_server.txt
echo Leave this window open while browsing the website.
echo.
".venv\Scripts\python.exe" -u scripts\run_and_log.py
pause
