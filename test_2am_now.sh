#!/bin/bash

# Test 2 AM Docker Script Immediately - Ubuntu Server
# Runs Docker right now instead of waiting for 2:00 AM

echo "================================================"
echo "  Test 2 AM Docker Script - Ubuntu Server"
echo "================================================"
echo ""
echo "This will run Docker immediately (not waiting for 2 AM)"
echo "Fresh database: job_market_data (jobscraper/working)"
echo "Old database will be ignored"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create logs directory
mkdir -p data/logs

# Log file
LOG_FILE="data/logs/2am_test.log"

# Function to log with timestamp
log_message() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a "$LOG_FILE"
}

# Function to get current time
get_current_time() {
    date '+%H:%M:%S %d/%m/%Y'
}

# Function to run Docker with fresh database
run_docker_fresh() {
    log_message "🛑 Stopping existing containers..."
    docker-compose down 2>/dev/null || true
    
    log_message "🗑️ Cleaning up old containers and volumes..."
    docker system prune -f 2>/dev/null || true
    
    log_message "🐳 Starting fresh Docker containers with NEW database (job_market_data)..."
    if docker-compose up -d; then
        log_message "✅ Docker containers started successfully!"
    else
        log_message "❌ Failed to start Docker containers"
        return 1
    fi
    
    # Wait for containers to be ready
    log_message "⏳ Waiting 30 seconds for containers to initialize..."
    sleep 30
    
    # Run the scraper
    log_message "🚀 Starting job scraper pipeline..."
    if timeout 7200 docker-compose exec -T job-scraper python scripts/run_automated_pipeline.py; then
        log_message "🎉 Job scraper completed successfully!"
        return 0
    else
        log_message "❌ Job scraper failed or timed out"
        return 1
    fi
}

# Main function
main() {
    # Log startup
    log_message "=================================================="
    log_message "2 AM TEST STARTED (IMMEDIATE RUN)"
    log_message "Current time: $(get_current_time)"
    log_message "Database: job_market_data (NEW)"
    log_message "Old database: IGNORED (fresh start)"
    log_message "=================================================="
    
    # Check if Docker is available
    if ! command -v docker >/dev/null 2>&1; then
        log_message "❌ Docker not found. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        log_message "❌ Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi
    
    # Run Docker immediately
    if run_docker_fresh; then
        log_message "=================================================="
        log_message "✅ TEST COMPLETED SUCCESSFULLY!"
        log_message "Finished at: $(get_current_time)"
        log_message "=================================================="
        exit 0
    else
        log_message "=================================================="
        log_message "❌ TEST FAILED!"
        log_message "Failed at: $(get_current_time)"
        log_message "=================================================="
        exit 1
    fi
}

# Handle Ctrl+C
trap 'log_message "🛑 Test stopped by user"; exit 0' INT

# Run main function
main