@echo off
REM ============================================
REM ClassSphere - Auto Fix Port Conflicts
REM ============================================
echo ============================================
echo ClassSphere Port Configuration Fix
echo ============================================
echo.
echo This script will update port configurations to avoid conflicts:
echo   - summarize_quiz_generator/app.py: 5001 -^> 5002
echo   - backend/api.py: 5001 -^> 5003
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

REM ============================================
REM Fix summarize_quiz_generator/app.py
REM ============================================
echo [1/2] Fixing summarize_quiz_generator/app.py...

set "FILE1=summarize_quiz_generator\app.py"
if exist "%FILE1%" (
    powershell -Command "(Get-Content '%FILE1%') -replace 'app\.run\(host=\"0\.0\.0\.0\", port=5001, debug=True\)', 'app.run(host=\"0.0.0.0\", port=5002, debug=True)' | Set-Content '%FILE1%'"
    echo    ✓ Updated summarize_quiz_generator/app.py to use port 5002
) else (
    echo    ✗ File not found: %FILE1%
)

REM ============================================
REM Fix backend/api.py
REM ============================================
echo [2/2] Fixing backend/api.py...

set "FILE2=backend\api.py"
if exist "%FILE2%" (
    powershell -Command "(Get-Content '%FILE2%') -replace 'app\.run\(debug=True, port=5001\)', 'app.run(debug=True, port=5003)' | Set-Content '%FILE2%'"
    echo    ✓ Updated backend/api.py to use port 5003
) else (
    echo    ✗ File not found: %FILE2%
)

echo.
echo ============================================
echo Port configuration fix completed!
echo ============================================
echo.
echo New port assignments:
echo   - AI Attendance:         Port 5000 ✓
echo   - AI Violence Detection: Port 5001 ✓
echo   - Quiz Generator:        Port 5002 ✓ (updated)
echo   - Main Backend API:      Port 5003 ✓ (updated)
echo   - Frontend:              Port 3000 ✓
echo.
echo You can now run: run.bat
echo.
pause
