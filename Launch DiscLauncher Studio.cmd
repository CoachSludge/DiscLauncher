@echo off
setlocal
cd /d "%~dp0"
where pyw >nul 2>nul
if not errorlevel 1 (
  start "" pyw -3 "%~dp0v2\gui.py"
  exit /b 0
)
where pythonw >nul 2>nul
if not errorlevel 1 (
  start "" pythonw "%~dp0v2\gui.py"
  exit /b 0
)
echo Python 3.9 or newer is required to start DiscLauncher Studio.
echo Install Python, then double-click this launcher again.
pause
exit /b 1
