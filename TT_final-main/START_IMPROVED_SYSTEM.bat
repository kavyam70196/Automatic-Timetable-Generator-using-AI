@echo off
title MIT Mysore Timetable System - Improved Version
echo.
echo ========================================
echo   MIT Mysore Timetable System v3.0
echo   IMPROVED VERSION WITH FIXES
echo ========================================
echo.
echo [INFO] Testing system connection...
python test_server.py
echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] System test passed!
    echo.
    echo [INFO] Starting Flask server...
    echo Server will be available at: http://127.0.0.1:5000
    echo.
    echo Available pages:
    echo - Main Interface: http://127.0.0.1:5000/timetable-new.htm
    echo - Dashboard: http://127.0.0.1:5000/dashboard.htm
    echo - Enhanced View: http://127.0.0.1:5000/enhanced.htm
    echo.
    echo IMPROVEMENTS IN THIS VERSION:
    echo - Only ONE lab per day (strict constraint)
    echo - FREE periods always at last period (slot 6)
    echo - Fixed button overlapping issues
    echo - Enhanced subject details with faculty initials
    echo.
    echo Starting server now...
    python flask_server.py
) else (
    echo [ERROR] System test failed!
    echo Please check your internet connection and dependencies.
    echo.
    echo To install dependencies, run:
    echo pip install flask==3.0.0 flask-cors==4.0.0 supabase==2.3.0 requests==2.31.0 python-dotenv==1.0.0
    echo.
    pause
)