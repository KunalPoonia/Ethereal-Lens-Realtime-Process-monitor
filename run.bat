@echo off
cd /d "%~dp0"
echo Starting Process Monitor Web Server...
echo.
cd rt_dashboard
python -m uvicorn server:app
pause
