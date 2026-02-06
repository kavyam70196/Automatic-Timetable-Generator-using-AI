@echo off
echo ========================================
echo MIT Mysore Timetable System Startup
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo Python found

echo.
echo Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install packages
    pause
    exit /b 1
)
echo Packages installed

echo.
echo Running system tests...
python test_complete_system.py
if errorlevel 1 (
    echo Some tests failed, but continuing...
    timeout /t 3 >nul
)

echo.
echo Running integration tests...
python test_integration.py
if errorlevel 1 (
    echo Integration tests failed, but continuing...
    timeout /t 3 >nul
)

echo.
echo Starting Flask server...
echo.
echo Open your browser and go to:
echo    http://localhost:5000
echo    or
echo    Open index.htm in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

python flask_server.py

pause