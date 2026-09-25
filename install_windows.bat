@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  CAI DAT - PHAT HIEN KHONG DOI MU
echo ============================================================

where py >nul 2>nul
if errorlevel 1 (
  echo [LOI] Khong tim thay Python Launcher ^(py^). Hay cai Python truoc.
  pause
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [LOI] Khong tim thay npm. Hay cai Node.js truoc.
  pause
  exit /b 1
)

cd backend
set "PYLAUNCH=py"
py -3.11 -V >nul 2>nul
if not errorlevel 1 set "PYLAUNCH=py -3.11"
if exist .venv\pyvenv.cfg (
  echo [1/5] Virtual environment da ton tai.
) else (
  echo [1/5] Tao Python virtual environment...
  %PYLAUNCH% -m venv .venv
)

call .venv\Scripts\activate.bat
if errorlevel 1 exit /b 1

echo [2/5] Nang cap pip...
python -m pip install --upgrade pip
if errorlevel 1 goto :error

echo [3/5] Cai thu vien backend...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

if not exist .env copy /Y .env.example .env >nul
cd ..\frontend
if not exist .env copy /Y .env.example .env >nul

echo [4/5] Cai thu vien frontend...
call npm install
if errorlevel 1 goto :error

cd ..\backend
echo [5/5] Kiem tra cau hinh...
python verify_setup.py
if errorlevel 1 goto :error

cd ..
echo.
echo ============================================================
echo  CAI DAT HOAN TAT. CHAY: run_windows.bat
echo ============================================================
pause
exit /b 0

:error
echo.
echo [LOI] Cai dat that bai. Xem thong bao phia tren.
pause
exit /b 1
