@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\vscode_setup.ps1"
if errorlevel 1 (
  echo.
  echo [LOI] Cai dat that bai. Xem thong bao phia tren.
  pause
  exit /b 1
)
echo.
echo Moi truong VS Code da san sang.
pause
