@echo off
REM ============================================================
REM  Process Monitor Web Server — startup script
REM  Usage: Double-click or run from command prompt
REM ============================================================

cd /d "%~dp0"

if not exist "rt_dashboard" (
    echo ERROR: rt_dashboard directory not found.
    exit /b 1
)

cd rt_dashboard

echo Starting Process Monitor Web Server...
echo.

python -m uvicorn server:app --reload

exit /b %ERRORLEVEL%
