@echo off
echo Starting MIT Mysore Timetable Server...
echo.
echo Make sure you have Python installed and all dependencies ready.
echo.
cd /d "%~dp0"
python flask_server.py
pause