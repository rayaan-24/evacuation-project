    @echo off
title Smart Evacuation System - Digital Working Model
color 0A

echo.
echo ==============================================================
echo   SMART EVACUATION SYSTEM - DIGITAL WORKING MODEL
echo   IoT Integration Testing Without Hardware
echo ==============================================================
echo.

:: Check if Flask is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.7+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if requests library is installed
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing required Python packages...
    pip install flask flask-cors pyserial requests
    echo.
)

:: Check if backend is already running
netstat -ano | findstr :5000 >nul
if not errorlevel 1 (
    echo WARNING: Port 5000 appears to be in use.
    echo Backend may already be running.
    echo.
)

echo ==============================================================
echo   STARTUP CHECKLIST
echo ==============================================================
echo.
echo [1] Backend Server    : Press 1 to START
echo [2] IoT Simulator     : Press 2 to START (after backend)
echo [3] Frontend URL      : http://localhost:5000/
echo [4] API Docs          : http://localhost:5000/api
echo [5] Run Demo          : Press 5 to trigger demo
echo [6] Clear All         : Press 6 to reset emergencies
echo [7] Exit              : Press 7 to quit
echo.
echo ==============================================================
echo.

:menu
set /p choice="Enter choice (1-7): "

if "%choice%"=="1" goto start_backend
if "%choice%"=="2" goto start_simulator
if "%choice%"=="3" goto open_frontend
if "%choice%"=="5" goto run_demo
if "%choice%"=="6" goto clear_all
if "%choice%"=="7" goto end

echo Invalid choice. Please try again.
goto menu

:start_backend
echo.
echo Starting Backend Server...
echo ================================
start "Backend Server" cmd /k "cd /d %~dp0backend && python app.py"
echo Backend started in new window.
echo Wait 3 seconds for server to initialize...
timeout /t 3 /nobreak >nul
echo.
echo Testing API connection...
curl -s http://localhost:5000/api >nul
if errorlevel 1 (
    echo ERROR: Could not connect to backend.
    echo Please check the backend server window for errors.
) else (
    echo SUCCESS: Backend is running!
    echo API: http://localhost:5000/api
    echo Frontend: http://localhost:5000/
)
echo.
goto menu

:start_simulator
echo.
echo Starting IoT Simulator...
echo ============================
start "IoT Simulator" cmd /k "cd /d %~dp0backend && python iot_simulator.py"
echo Simulator started in new window.
echo.
goto menu

:open_frontend
echo.
echo Opening Frontend in default browser...
start http://localhost:5000/
echo.
goto menu

:run_demo
echo.
echo Running Demo Scenario...
echo ========================
python -c "import requests; requests.post('http://localhost:5000/sensor-update', json={'sensor_id': 'sensor_0', 'type': 'FIRE'})"
echo Triggered sensor_0 (FIRE)
python -c "import requests; requests.post('http://localhost:5000/sensor-update', json={'sensor_id': 'sensor_4', 'type': 'SMOKE'})"
echo Triggered sensor_4 (SMOKE)
python -c "import requests; requests.post('http://localhost:5000/sensor-update', json={'sensor_id': 'sensor_8', 'type': 'GAS'})"
echo Triggered sensor_8 (GAS)
echo.
echo Demo sensors triggered! Check frontend at http://localhost:5000/
echo.
goto menu

:clear_all
echo.
echo Clearing All Emergencies...
echo ===========================
curl -s -X POST http://localhost:5000/reset-emergencies
echo.
echo All emergencies cleared!
echo.
goto menu

:end
echo.
echo ==============================================================
echo   Goodbye!
echo ==============================================================
echo.
pause
