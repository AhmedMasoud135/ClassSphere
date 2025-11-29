@echo off
REM ============================================
REM ClassSphere - Stop All Services
REM ============================================
echo Stopping all ClassSphere services...
echo.

REM Kill processes by port
echo Stopping services on ports 3000, 5000, 5001, 5002, 5003...

REM Stop Flask services (ports 5000-5003)
for /L %%p in (5000,1,5003) do (
    echo Checking port %%p...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p ^| findstr LISTENING') do (
        echo Killing process on port %%p (PID: %%a)
        taskkill /F /PID %%a 2>nul
    )
)

REM Stop Next.js frontend (port 3000)
echo Checking port 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    echo Killing process on port 3000 (PID: %%a)
    taskkill /F /PID %%a 2>nul
)

REM Alternative: Kill by process name
echo.
echo Killing Python and Node processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul

echo.
echo All services stopped.
echo.
pause
