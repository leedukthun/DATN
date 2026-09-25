@echo off
setlocal
cd /d "%~dp0frontend"
call npm run build
if errorlevel 1 (
  echo Build that bai.
  pause
  exit /b 1
)
echo Frontend da build vao frontend\dist.
echo Chay backend, sau do mo http://localhost:8000
pause
