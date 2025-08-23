@echo off
echo ====================================
echo   2 AM Vietnam Time Docker Scheduler
echo ====================================
echo.
echo This will start Docker automatically at 2:00 AM Vietnam time
echo Fresh database: job_market_data (jobscraper/working)
echo Old database will be ignored
echo.
echo Press Ctrl+C to cancel
echo.

cd /d "%~dp0"

REM Activate conda environment
if exist "C:\ProgramData\anaconda3\condabin\activate.bat" (
    echo Activating conda environment py11...
    call C:\ProgramData\anaconda3\condabin\activate.bat py11
)

REM Create logs directory
if not exist "data\logs" mkdir data\logs

REM Start the 2AM scheduler
echo Starting 2 AM scheduler...
python run_2am_tonight.py

echo.
echo Scheduler finished. Check data/logs/2am_runner.log for details.
pause