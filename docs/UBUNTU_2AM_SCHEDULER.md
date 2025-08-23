# Ubuntu 2 AM Scheduler Guide

Simple guide for running Docker automatically at 2 AM on Ubuntu Server with fresh database.

## Quick Start

### Option 1: Wait for 2 AM Tonight
```bash
# Make executable and run
chmod +x run_2am_tonight.sh
./run_2am_tonight.sh
```

### Option 2: Test Immediately
```bash
# Test right now (don't wait for 2 AM)
chmod +x test_2am_now.sh
./test_2am_now.sh
```

### Option 3: Background Mode
```bash
# Run in background
nohup ./run_2am_tonight.sh > scheduler_output.log 2>&1 &

# Check if running
ps aux | grep run_2am_tonight

# Monitor logs
tail -f data/logs/2am_runner.log
```

## What the Scripts Do

### `run_2am_tonight.sh`
- ✅ **Waits until 2:00 AM** system time
- ✅ **Stops existing Docker** containers
- ✅ **Cleans up** old containers/volumes
- ✅ **Starts fresh Docker** with new database
- ✅ **Runs scraper pipeline** automatically
- ✅ **Logs everything** to `data/logs/2am_runner.log`

### `test_2am_now.sh`
- ✅ **Same as above** but runs immediately
- ✅ **Perfect for testing** before real run
- ✅ **Logs to** `data/logs/2am_test.log`

## Database Configuration

### New Database (Fresh Start)
- **Name:** `job_market_data`
- **User:** `jobscraper`  
- **Password:** `working`
- **Access:** localhost:5432 (internal) / localhost:8081 (Adminer)

### Old Database
- **Status:** IGNORED completely
- **No migration** needed - fresh start

## System Requirements

### Prerequisites
```bash
# Docker and Docker Compose must be installed
docker --version
docker-compose --version

# User should be in docker group
groups $USER | grep docker
```

### If Docker not installed:
```bash
# Quick Docker install
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Logout and login again

# Install Docker Compose
sudo apt install -y docker-compose
```

## Monitoring

### Real-time Logs
```bash
# Monitor scheduler logs
tail -f data/logs/2am_runner.log

# Monitor Docker logs
docker-compose logs -f

# Monitor all logs
tail -f data/logs/*.log
```

### Check Status
```bash
# Check if containers are running
docker-compose ps

# Check specific container logs
docker-compose logs job-scraper
docker-compose logs postgres
```

### Database Access
```bash
# Direct database access
docker-compose exec postgres psql -U jobscraper -d job_market_data

# Web interface
# http://your-server-ip:8081
# Server: postgres  Database: job_market_data  User: jobscraper  Password: working
```

## Timezone Setup

### Check Current Timezone
```bash
timedatectl
date
```

### Set Vietnam Timezone (Optional)
```bash
sudo timedatectl set-timezone Asia/Ho_Chi_Minh
```

## Troubleshooting

### Permission Issues
```bash
# Make scripts executable
chmod +x *.sh

# Add user to docker group
sudo usermod -aG docker $USER
# Then logout and login
```

### Docker Issues
```bash
# Clean up Docker completely
docker-compose down
docker system prune -af
docker volume prune -f

# Restart Docker service
sudo systemctl restart docker
```

### Script Not Running
```bash
# Check logs for errors
cat data/logs/2am_runner.log

# Run with debug
bash -x ./run_2am_tonight.sh
```

### Container Startup Issues
```bash
# Check what's using port 5432
sudo netstat -tulpn | grep :5432

# Kill conflicting processes
sudo pkill -f postgres
```

## Log Files

### Scheduler Logs
- **2 AM runs:** `data/logs/2am_runner.log`
- **Test runs:** `data/logs/2am_test.log`

### Docker Logs
```bash
# View container logs
docker-compose logs job-scraper
docker-compose logs postgres

# Follow logs live
docker-compose logs -f
```

## Success Verification

After successful run, verify:
- [ ] ✅ New database `job_market_data` exists
- [ ] ✅ Jobs table has fresh scraped data
- [ ] ✅ No old data from previous database
- [ ] ✅ Scraper completed without errors
- [ ] ✅ Log files show success messages

### Check Database Data
```bash
# Connect to database
docker-compose exec postgres psql -U jobscraper -d job_market_data

# Count jobs
SELECT COUNT(*) FROM jobs;

# Check latest jobs
SELECT profession, company_name, scraped_at FROM jobs ORDER BY scraped_at DESC LIMIT 5;

# Exit
\q
```

## Stop/Cancel

### Stop Waiting Script
```bash
# If running in foreground
Ctrl+C

# If running in background
ps aux | grep run_2am_tonight
kill <PID>
```

### Emergency Stop Docker
```bash
# Stop all containers
docker-compose down

# Force stop if needed
docker kill $(docker ps -q)
```

## Example Usage

### Complete Workflow
```bash
# 1. Make sure Docker is running
sudo systemctl status docker

# 2. Go to project directory
cd /path/to/job-scraper

# 3. Test first (optional)
./test_2am_now.sh

# 4. Run 2 AM scheduler
./run_2am_tonight.sh

# 5. Monitor in another terminal
tail -f data/logs/2am_runner.log
```

This simple approach ensures reliable Docker execution at exactly 2 AM with fresh database setup.