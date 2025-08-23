@echo off
echo ========================================
echo   2 AM Simple Docker Scheduler  
echo ========================================
echo.
echo This will start Docker at 2:00 AM (system time)
echo Fresh database: job_market_data (jobscraper/working)
echo Old database will be ignored
echo.
echo Make sure your Windows time is set to Vietnam timezone!
echo Press Ctrl+C to cancel
echo.

cd /d "%~dp0"

REM Show current time
echo Current system time: %date% %time%
echo.

REM Activate conda environment
if exist "C:\ProgramData\anaconda3\condabin\activate.bat" (
    echo Activating conda environment py11...
    call C:\ProgramData\anaconda3\condabin\activate.bat py11
)

REM Create logs directory
if not exist "data\logs" mkdir data\logs

REM Start the simple 2AM scheduler
echo Starting simple 2 AM scheduler...
python run_2am_tonight_simple.py

echo.
echo Scheduler finished. Check data/logs/2am_runner.log for details.
pause