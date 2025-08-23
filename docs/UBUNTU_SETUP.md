# Ubuntu Server Setup Guide

Complete setup guide for running the Job Scraper on Ubuntu Server with automated 2 AM Vietnam time scheduling.

## Quick Start

### 1. One-Command Setup
```bash
# Download and setup everything automatically
curl -fsSL https://raw.githubusercontent.com/qfc88/Deutsch_DE_T/main/setup_ubuntu.sh | bash

# Or if you have the project already:
chmod +x setup_ubuntu.sh && ./setup_ubuntu.sh
```

### 2. Start Scheduler
```bash
# Run in foreground (see logs immediately)
./start_scheduler.sh

# Run in background (daemon mode)
./start_scheduler.sh background

# Test immediately (don't wait for 2 AM)
./test_scheduler.sh
```

### 3. Install as System Service (Optional)
```bash
# Install systemd service (auto-start on boot)
./install_systemd.sh
```

## Manual Setup Steps

### Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git python3 python3-pip
```

### Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install -y docker-compose

# Logout and login again for docker group changes
```

### Install Python Dependencies
```bash
# Install project dependencies
pip3 install --user -r requirements.txt

# Or install individually:
pip3 install --user schedule asyncpg pandas playwright requests PyYAML
```

### Setup Project Structure
```bash
# Create required directories
mkdir -p data/{input,output,logs,backup,temp}
chmod -R 755 data/

# Make scripts executable
chmod +x scripts/*.py
chmod +x *.sh
```

## Running Options

### Option 1: Interactive Mode
```bash
./start_scheduler.sh
```
- Runs in foreground
- See logs immediately
- Stop with Ctrl+C

### Option 2: Background Mode
```bash
./start_scheduler.sh background
```
- Runs in background
- Logs to `data/logs/scheduler_console.log`
- Find PID with: `ps aux | grep schedule_scraper`
- Stop with: `kill <PID>`

### Option 3: Systemd Service
```bash
# Install service
./install_systemd.sh

# Service management
sudo systemctl status job-scraper-scheduler    # Check status
sudo systemctl start job-scraper-scheduler     # Start
sudo systemctl stop job-scraper-scheduler      # Stop
sudo systemctl restart job-scraper-scheduler   # Restart

# Auto-start on boot
sudo systemctl enable job-scraper-scheduler
```

### Option 4: Manual Docker
```bash
# Start containers manually
docker-compose up -d

# Run scraping pipeline
docker-compose exec job-scraper python scripts/run_automated_pipeline.py

# Stop containers
docker-compose down
```

## Configuration

### Database Settings (docker-compose.yml)
```yaml
environment:
  POSTGRES_DB: job_market_data
  POSTGRES_USER: jobscraper  
  POSTGRES_PASSWORD: working
```

### Environment Variables (.env)
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=job_market_data
DB_USER=jobscraper
DB_PASSWORD=working
SCRAPER_HEADLESS=true
SCRAPER_BATCH_SIZE=50
```

## Monitoring

### Log Files
- **Scheduler logs:** `data/logs/scheduler.log`
- **System logs:** `data/logs/systemd.log`
- **Console logs:** `data/logs/scheduler_console.log`
- **Docker logs:** `docker-compose logs -f`

### Real-time Monitoring
```bash
# Scheduler logs
tail -f data/logs/scheduler.log

# System service logs
journalctl -u job-scraper-scheduler -f

# Docker container logs
docker-compose logs -f job-scraper

# All logs together
tail -f data/logs/*.log
```

### Database Access
- **Direct connection:** `localhost:5432` (or 5433 if configured)
- **Web interface:** http://your-server-ip:8081
- **Credentials:** jobscraper / working / job_market_data

## Timezone Configuration

### Set Vietnam Timezone (UTC+7)
```bash
# Check current timezone
timedatectl

# Set to Vietnam timezone
sudo timedatectl set-timezone Asia/Ho_Chi_Minh

# Verify
date
```

### Schedule Details
- **Target Time:** 2:00 AM Vietnam time daily
- **UTC Conversion:** 7:00 PM previous day UTC
- **Example:** Aug 24, 2025 2:00 AM Vietnam = Aug 23, 2025 7:00 PM UTC

## Troubleshooting

### Docker Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, or use newgrp:
newgrp docker
```

### Port Conflicts
```bash
# Check what's using port 5432
sudo netstat -tulpn | grep :5432

# Kill conflicting process
sudo kill <PID>

# Or change port in docker-compose.yml
```

### Service Not Starting
```bash
# Check service status
sudo systemctl status job-scraper-scheduler

# Check logs
journalctl -u job-scraper-scheduler -n 50

# Restart service
sudo systemctl restart job-scraper-scheduler
```

### Python Package Issues
```bash
# Install packages with sudo if needed
sudo pip3 install schedule

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Memory Issues
```bash
# Check memory usage
free -h
docker stats

# Reduce Docker memory if needed (docker-compose.yml)
deploy:
  resources:
    limits:
      memory: 2G
```

## Security Considerations

### Firewall Setup
```bash
# Allow only necessary ports
sudo ufw allow ssh
sudo ufw allow 8081/tcp  # Adminer (optional)
sudo ufw enable
```

### Database Security
- Change default passwords in production
- Restrict database access to localhost
- Use environment variables for secrets

### User Permissions
```bash
# Run as non-root user
# Create dedicated user if needed
sudo adduser jobscraper
sudo usermod -aG docker jobscraper
```

## Performance Optimization

### System Resources
```bash
# Check system resources
htop
df -h
docker system df

# Clean up Docker
docker system prune -f
```

### Scheduler Settings
Edit `src/config/settings.py`:
```python
SCRAPER_SETTINGS = {
    'batch_size': 50,        # Increase for faster processing
    'max_jobs_per_session': 2000,  # Set reasonable limits
    'delay_between_jobs': 0.3,     # Reduce delays
}
```

## Backup and Recovery

### Backup Database
```bash
# Create database backup
docker-compose exec postgres pg_dump -U jobscraper job_market_data > backup_$(date +%Y%m%d).sql

# Automated backup script
cat > backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="data/backup"
mkdir -p "$BACKUP_DIR"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U jobscraper job_market_data > "$BACKUP_DIR/job_market_data_$DATE.sql"
echo "Backup created: $BACKUP_DIR/job_market_data_$DATE.sql"
EOF

chmod +x backup_db.sh
```

### Restore Database
```bash
# Restore from backup
docker-compose exec -T postgres psql -U jobscraper job_market_data < backup_file.sql
```

## Success Checklist

After setup, verify:
- [ ] ✅ Docker containers start successfully
- [ ] ✅ Database accessible at localhost:8081
- [ ] ✅ Scheduler runs without errors
- [ ] ✅ Log files are created and updated
- [ ] ✅ Test run completes successfully
- [ ] ✅ Service starts on boot (if using systemd)
- [ ] ✅ Vietnam timezone configured correctly

## Support

### Common Commands
```bash
# Check everything is running
docker-compose ps
sudo systemctl status job-scraper-scheduler
ps aux | grep schedule_scraper

# Full restart
docker-compose down && docker-compose up -d
sudo systemctl restart job-scraper-scheduler

# Clean start
docker-compose down
docker system prune -f
./start_scheduler.sh
```

This Ubuntu setup provides enterprise-grade reliability with automatic scheduling, service management, and comprehensive monitoring.