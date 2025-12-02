@echo off
setlocal

REM Detect Python
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python is not installed or not in PATH.
  echo Download: https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

REM Upgrade pip and install required packages
echo [INFO] Installing/upgrading dependencies...
python -m pip install --upgrade pip
python -m pip install customtkinter tkcalendar openpyxl
if errorlevel 1 (
  echo [ERROR] Failed to install dependencies.
  pause
  exit /b 1
)

REM Run the app
echo [INFO] Starting application...
python main.py

echo.
echo [INFO] Application exited. Press any key to close.
pause >nul
endlocal