@echo off
setlocal
cd /d "%~dp0"

if not exist backend\.venv\Scripts\python.exe (
  echo Chua cai dat moi truong. Hay chay install_windows.bat truoc.
  pause
  exit /b 1
)
if not exist frontend\node_modules (
  echo Chua cai frontend. Hay chay install_windows.bat truoc.
  pause
  exit /b 1
)

start "Helmet Detection - Backend" cmd /k "cd /d ""%~dp0backend"" && call .venv\Scripts\activate.bat && python run.py"
start "Helmet Detection - Frontend" cmd /k "cd /d ""%~dp0frontend"" && npm run dev"

timeout /t 3 /nobreak >nul
start "" http://localhost:5173

echo Da khoi dong Backend va Frontend trong hai cua so terminal.
echo Dong hai cua so do de dung chuong trinh.
