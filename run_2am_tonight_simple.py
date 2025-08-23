#!/usr/bin/env python3
"""
Simple scheduler to run Docker at exactly 2 AM 
Uses system time - assumes Windows is set to Vietnam timezone
"""

import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path('data/logs/2am_runner.log'), mode='a')
    ]
)
logger = logging.getLogger(__name__)

def get_current_time():
    """Get current system time"""
    return datetime.now()

def wait_until_2am():
    """Wait until 2:00 AM system time"""
    while True:
        now = get_current_time()
        current_hour = now.hour
        current_minute = now.minute
        
        # Check if it's 2:00 AM (between 2:00 and 2:01 AM)
        if current_hour == 2 and current_minute == 0:
            logger.info(f"Target 2:00 AM reached! Starting Docker...")
            return True
            
        # Log status every 10 minutes
        if current_minute % 10 == 0:
            logger.info(f"Current time: {now.strftime('%H:%M:%S %d/%m/%Y')} - Waiting for 2:00 AM...")
        
        # Sleep for 30 seconds
        time.sleep(30)

def run_docker_fresh():
    """Start Docker with fresh database"""
    try:
        logger.info("Stopping existing containers...")
        subprocess.run(["docker-compose", "down"], check=False, capture_output=True)
        
        logger.info("Cleaning up old containers and volumes...")
        subprocess.run(["docker", "system", "prune", "-f"], check=False, capture_output=True)
        
        logger.info("Starting fresh Docker containers with NEW database (job_market_data)...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"], 
            check=True, 
            capture_output=True, 
            text=True
        )
        logger.info("Docker containers started successfully!")
        logger.info(f"Docker output: {result.stdout}")
        
        # Wait for containers to be ready
        logger.info("Waiting 30 seconds for containers to initialize...")
        time.sleep(30)
        
        # Run the scraper
        logger.info("Starting job scraper pipeline...")
        scraper_result = subprocess.run(
            ["docker-compose", "exec", "-T", "job-scraper", "python", "scripts/run_automated_pipeline.py"],
            check=True,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hours max
        )
        
        logger.info("Job scraper completed successfully!")
        logger.info(f"Scraper output: {scraper_result.stdout}")
        
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Scraper timed out after 2 hours")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Docker/Scraper failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def main():
    """Main function"""
    current_time = get_current_time()
    logger.info("=" * 50)
    logger.info(f"2 AM SCHEDULER STARTED")
    logger.info(f"Current time: {current_time.strftime('%H:%M:%S %d/%m/%Y')}")
    logger.info(f"Target: 2:00 AM (system time)")
    logger.info(f"Database: job_market_data (NEW)")
    logger.info(f"Old database: IGNORED (fresh start)")
    logger.info("=" * 50)
    logger.info("")
    
    # Create logs directory
    Path('data/logs').mkdir(parents=True, exist_ok=True)
    
    try:
        # Wait until 2 AM
        wait_until_2am()
        
        # Run Docker
        success = run_docker_fresh()
        
        # Final status
        end_time = get_current_time()
        if success:
            logger.info("=" * 50)
            logger.info(f"2 AM JOB COMPLETED SUCCESSFULLY!")
            logger.info(f"Finished at: {end_time.strftime('%H:%M:%S %d/%m/%Y')}")
            logger.info("=" * 50)
        else:
            logger.error("=" * 50)
            logger.error(f"2 AM JOB FAILED!")
            logger.error(f"Failed at: {end_time.strftime('%H:%M:%S %d/%m/%Y')}")
            logger.error("=" * 50)
            
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()