@echo off
REM ============================================
REM ClassSphere - Microservices Startup Script
REM ============================================
REM This script starts all microservices and the frontend
REM Each service runs in its own command window

echo ============================================
echo Starting ClassSphere Microservices Platform
echo ============================================
echo.

REM Get the directory where the batch file is located
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo Project Directory: %PROJECT_DIR%
echo.

REM ============================================
REM Configure Conda Environment
REM ============================================
set CONDAPATH=C:\Users\IT\anaconda3
set ENVNAME=AUSAM

REM Initialize Conda
call "%CONDAPATH%\Scripts\activate.bat" "%CONDAPATH%"

echo Using Conda Environment: %ENVNAME%
echo.

REM ============================================
REM 1. Start AI Backend - Attendance Service (Port 5000)
REM ============================================
echo [1/5] Starting AI Backend - Attendance Service...
start "AI-Backend-Attendance [Port 5000]" cmd /k "call "%CONDAPATH%\Scripts\activate.bat" "%CONDAPATH%" && conda activate %ENVNAME% && cd /d "%PROJECT_DIR%ai-backend-attendance" && python app.py"
timeout /t 3 /nobreak >nul

REM ============================================
REM 2. Start AI Backend - Violence Detection Service (Port 5001)
REM ============================================
echo [2/5] Starting AI Backend - Violence Detection Service...
start "AI-Backend-Violence [Port 5001]" cmd /k "call "%CONDAPATH%\Scripts\activate.bat" "%CONDAPATH%" && conda activate %ENVNAME% && cd /d "%PROJECT_DIR%ai-backend-violence" && python app.py"
timeout /t 3 /nobreak >nul

REM ============================================
REM 3. Start Summarize Quiz Generator Service (Port 5002)
REM ============================================
echo [3/5] Starting Summarize Quiz Generator Service...
start "Summarize-Quiz-Generator [Port 5002]" cmd /k "call "%CONDAPATH%\Scripts\activate.bat" "%CONDAPATH%" && conda activate %ENVNAME% && cd /d "%PROJECT_DIR%summarize_quiz_generator" && python app.py"
timeout /t 3 /nobreak >nul

REM ============================================
REM 4. Start Main Backend API Service (Port 5003)
REM ============================================
echo [4/5] Starting Main Backend API Service...
start "Main-Backend-API [Port 5003]" cmd /k "call "%CONDAPATH%\Scripts\activate.bat" "%CONDAPATH%" && conda activate %ENVNAME% && cd /d "%PROJECT_DIR%backend" && python api.py"
timeout /t 3 /nobreak >nul

REM ============================================
REM 5. Start Frontend (Next.js) (Port 3000)
REM ============================================
echo [5/5] Starting Frontend (Next.js)...
start "Frontend-Next.js [Port 3000]" cmd /k "cd /d "%PROJECT_DIR%frontend" && npm run dev"

echo.
echo ============================================
echo All services are starting...
echo ============================================
echo.
echo Services:
echo   - AI Attendance:        http://localhost:5000
echo   - AI Violence Detection: http://localhost:5001
echo   - Quiz Generator:        http://localhost:5002
echo   - Main Backend API:      http://localhost:5003
echo   - Frontend:              http://localhost:3000
echo.
echo Each service is running in its own window.
echo Close individual windows to stop specific services.
echo.
echo Press any key to exit this launcher (services will continue running)...
pause >nul
