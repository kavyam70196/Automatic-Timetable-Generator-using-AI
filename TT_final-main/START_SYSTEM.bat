@echo off
title MIT Mysore Timetable System
echo.
echo ========================================
echo   MIT Mysore Timetable System v2.0
echo ========================================
echo.
echo Testing system connection...
python test_supabase_connection.py
echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] System test passed!
    echo.
    echo Starting Flask server...
    echo Server will be available at: http://127.0.0.1:5000
    echo.
    echo Available pages:
    echo - Login: index.htm
    echo - Create Timetable: timetable-new.htm  
    echo - View Timetables: timetable_display.htm
    echo.
    python flask_server.py
) else (
    echo [ERROR] System test failed!
    echo Please check your internet connection and try again.
    pause
)