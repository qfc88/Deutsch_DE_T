# Scheduled Job Scraping Setup

This document explains how to set up automated job scraping at 2 AM Vietnam time (UTC+7).

## Overview

The scheduler is designed to run when German job websites open back up at 2 AM Vietnam time on 24/08/2025, using a fresh database with professional credentials.

## New Database Configuration

### Database Details:
- **Database Name:** `job_market_data` (professional naming)
- **Username:** `jobscraper` 
- **Password:** `working`
- **Port:** 5432 (Docker internal) / 5433 (external access)

### Changes Made:
- Updated `docker-compose.yml` with new credentials
- Updated `src/config/settings.py` with new defaults
- Added `schedule==1.2.2` to requirements.txt

## Scheduling Options

### Option 1: Automatic Scheduler (Recommended)

Run the scheduler that waits for 2 AM Vietnam time:

**Windows:**
```bash
start_scheduler.bat
```

**Linux/Mac:**
```bash
python scripts/schedule_scraper.py
```

### Option 2: Test Run (Immediate)

Test the scraper immediately without waiting:

**Windows:**
```bash
test_scheduler.bat
```

**Linux/Mac:**
```bash
python scripts/schedule_scraper.py test
```

### Option 3: Manual Docker Run

Run Docker containers manually:

```bash
# Stop existing containers
docker-compose down

# Start with new database
docker-compose up -d

# Run automated pipeline
docker-compose exec job-scraper python scripts/run_automated_pipeline.py
```

## Features

### Scheduler Features:
- ✅ **Vietnam Timezone (UTC+7)** - Accurate time conversion
- ✅ **Daily Scheduling** - Runs every day at 2:00 AM
- ✅ **Fresh Database** - New database for each run
- ✅ **Professional Naming** - Clean database and user names
- ✅ **Error Handling** - Robust error recovery
- ✅ **Logging** - Comprehensive logs in `data/logs/scheduler.log`
- ✅ **Docker Integration** - Full container lifecycle management
- ✅ **Timeout Protection** - 2-hour maximum runtime

### Database Features:
- ✅ **Separate Database** - `job_market_data` instead of `scrape`
- ✅ **New User** - `jobscraper` user with `working` password
- ✅ **Port Isolation** - Uses port 5433 to avoid conflicts
- ✅ **Fresh Schema** - Clean tables for new data
- ✅ **Admin Interface** - Adminer available on port 8081

## Monitoring

### Log Files:
- **Scheduler logs:** `data/logs/scheduler.log`
- **Application logs:** Docker container logs
- **Pipeline logs:** `data/logs/automated_pipeline.log`

### Database Access:
- **Direct connection:** `localhost:5433`
- **Web interface:** http://localhost:8081 (Adminer)

### Commands for Monitoring:
```bash
# View scheduler logs
tail -f data/logs/scheduler.log

# View container logs
docker-compose logs -f job-scraper

# Check database
docker-compose exec postgres psql -U jobscraper -d job_market_data
```

## Vietnam Time Schedule

The scheduler automatically converts to Vietnam time (UTC+7):

- **Target Time:** 2:00 AM Vietnam time daily
- **UTC Equivalent:** 7:00 PM previous day (UTC)
- **Example:** 2 AM August 24, 2025 Vietnam = 7 PM August 23, 2025 UTC

## Troubleshooting

### Common Issues:

**1. Container Conflicts:**
```bash
docker-compose down
docker system prune -f
```

**2. Database Connection:**
- Check port 5433 is available
- Verify credentials in docker-compose.yml

**3. Scheduler Not Running:**
- Install schedule: `pip install schedule`
- Check logs: `data/logs/scheduler.log`

**4. Time Zone Issues:**
- Scheduler automatically handles Vietnam time
- No manual timezone configuration needed

## Success Criteria

After successful run, you should see:
- ✅ Fresh database `job_market_data` with job data
- ✅ Logs showing successful completion
- ✅ JSON batch files in `data/output/YYYYMMDD_HHMMSS/`
- ✅ Database populated with scraped jobs
- ✅ Contact information extracted and stored

## Next Steps

1. **Start Scheduler:** Run `start_scheduler.bat` 
2. **Monitor Logs:** Watch `data/logs/scheduler.log`
3. **Verify Database:** Check data at http://localhost:8081
4. **Review Results:** Analyze scraped data quality
5. **Schedule Maintenance:** Plan for daily operations