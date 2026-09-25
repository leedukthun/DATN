@echo off
setlocal
cd /d "%~dp0"
where code >nul 2>nul
if errorlevel 1 (
  echo [LOI] Khong tim thay lenh "code" trong PATH.
  echo Mo VS Code, chon File ^> Open Workspace from File...
  echo Sau do chon: helmet-detection.code-workspace
  pause
  exit /b 1
)
code --reuse-window "%~dp0helmet-detection.code-workspace"
