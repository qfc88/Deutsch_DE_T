#!/usr/bin/env python3
"""
Automated Pipeline V2 - Clean & Complete Integration
Enhanced pipeline with comprehensive data cleaning and single database load
Scrape → Enhanced Validation → Complete Cleaning → Single DB Load
"""

import asyncio
import sys
import os
import logging
import time
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))
sys.path.append(str(project_root / "src" / "config"))
sys.path.append(str(project_root / "src" / "utils"))
sys.path.append(str(project_root / "src" / "database"))

try:
    from settings import *
except ImportError as e:
    print(f"[ERROR] Settings import failed: {e}")
    sys.exit(1)

# Enhanced logging for V2
logging.basicConfig(
    level=getattr(logging, LOGGING_SETTINGS.get('level', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(PATHS['logs_dir']) / 'automated_pipeline_v2.log')
    ]
)
logger = logging.getLogger(__name__)

class AutomatedPipelineV2:
    def __init__(self):
        self.running = True
        self.start_time = datetime.now()
        self.stats = {
            'phases_completed': 0,
            'total_jobs_processed': 0,
            'total_jobs_cleaned': 0,
            'total_jobs_loaded': 0,
            'validation_failures': 0,
            'cleaning_failures': 0,
            'database_failures': 0,
            'errors': 0,
            'last_run': None
        }
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False
    
    async def wait_for_database(self, max_attempts=30):
        """Wait for database to be ready"""
        logger.info("🔄 Waiting for database connection...")
        
        for attempt in range(max_attempts):
            try:
                from connection import DatabaseManager
                
                db = DatabaseManager()
                await db.connect()
                await db.disconnect()
                logger.info("[SUCCESS] Database connection successful")
                return True
                
            except Exception as e:
                if attempt < max_attempts - 1:
                    logger.info(f"Database not ready (attempt {attempt + 1}/{max_attempts}), retrying in 5s...")
                    await asyncio.sleep(5)
                else:
                    logger.error(f"[ERROR] Database connection failed after {max_attempts} attempts: {e}")
                    return False
        
        return False
    
    async def run_phase1_links(self):
        """Phase 1: Collect job URLs"""
        logger.info("🔗 PHASE 1: Starting job URL collection...")
        
        try:
            from scrapers.link_job import JobURLScraper
            
            # Use the arbeitsagentur.de URL from assignment
            url = "https://www.arbeitsagentur.de/jobsuche/suche?angebotsart=4&ausbildungsart=0&arbeitszeit=vz&branche=22;1;2;9;3;5;7;10;11;16;12;21;26;15;17;19;20;8;23;29&veroeffentlichtseit=7&sort=veroeffdatum"
            
            scraper = JobURLScraper(url)
            
            # Check if we should skip if recent data exists
            existing_df = scraper.load_job_urls_from_csv()
            if existing_df is not None and len(existing_df) > 0:
                logger.info(f"📋 Found {len(existing_df)} existing URLs, using them")
                df = existing_df
            else:
                logger.info("🆕 No existing data found")
                # For now, skip scraping to avoid Playwright issues
                logger.warning("[WARNING] Skipping scraping due to Playwright async conversion in progress")
                return 0
            
            if df is not None and len(df) > 0:
                logger.info(f"[SUCCESS] Phase 1 completed: {len(df)} job URLs collected")
                return len(df)
            else:
                logger.error("[ERROR] Phase 1 failed: No URLs collected")
                return 0
                
        except Exception as e:
            logger.error(f"[ERROR] Phase 1 error: {e}")
            self.stats['errors'] += 1
            return 0
    
    async def run_phase2_enhanced_scraping(self):
        """Phase 2: Enhanced scraping with comprehensive validation and cleaning"""
        logger.info("🎯 PHASE 2: Starting enhanced job scraping with clean integration...")
        
        try:
            from scrapers.job_scraper_v2 import JobScraperV2
            
            # Check if input file exists
            input_path = Path(PATHS['input_csv'])
            if not input_path.exists():
                logger.error("[ERROR] Input file not found, Phase 1 must complete first")
                return 0
            
            # Initialize V2 scraper with enhanced settings
            auto_solve = os.getenv('AUTO_SOLVE_CAPTCHA', 'true').lower() == 'true'
            enable_realtime_enhancement = os.getenv('ENABLE_REALTIME_ENHANCEMENT', 'true').lower() == 'true'
            
            scraper = JobScraperV2(
                auto_solve_captcha=auto_solve,
                enable_comprehensive_validation=True,
                enable_enhanced_cleaning=True,
                enable_single_db_load=True,
                enable_realtime_enhancement=enable_realtime_enhancement
            )
            
            # Load existing progress for resume
            existing_jobs = await scraper.load_existing_progress()
            resume = existing_jobs is not None and len(existing_jobs) > 0
            
            if resume:
                logger.info(f"🔄 Resuming from {len(existing_jobs)} existing jobs")
            
            # Run enhanced scraping
            logger.info("🚀 Starting enhanced scraping with:")
            logger.info("   ✅ Comprehensive validation")
            logger.info("   ✅ Enhanced data cleaning")
            logger.info("   ✅ Single database load")
            logger.info("   ✅ No duplicate loading")
            if enable_realtime_enhancement:
                logger.info("   🔍 Realtime contact enhancement")
            else:
                logger.info("   ⚠️ Realtime enhancement disabled")
            
            result = await scraper.run_enhanced(
                input_csv_path=str(input_path),
                resume=resume,
                auto_solve_captcha=auto_solve
            )
            
            # Update statistics
            self.stats['total_jobs_processed'] = result.get('scraped_count', 0)
            self.stats['total_jobs_cleaned'] = result.get('cleaned_count', 0)
            self.stats['total_jobs_loaded'] = result.get('loaded_count', 0)
            self.stats['validation_failures'] = result.get('validation_failures', 0)
            self.stats['cleaning_failures'] = result.get('cleaning_failures', 0)
            self.stats['database_failures'] = result.get('database_failures', 0)
            
            logger.info(f"[SUCCESS] Phase 2 completed:")
            logger.info(f"   📊 Jobs scraped: {result.get('scraped_count', 0)}")
            logger.info(f"   🧹 Jobs cleaned: {result.get('cleaned_count', 0)}")
            logger.info(f"   💾 Jobs loaded to DB: {result.get('loaded_count', 0)}")
            logger.info(f"   ❌ Validation failures: {result.get('validation_failures', 0)}")
            logger.info(f"   🔧 Cleaning failures: {result.get('cleaning_failures', 0)}")
            logger.info(f"   💥 Database failures: {result.get('database_failures', 0)}")
            
            return result.get('loaded_count', 0)
            
        except Exception as e:
            logger.error(f"[ERROR] Phase 2 error: {e}")
            self.stats['errors'] += 1
            return 0
    
    async def run_phase3_contacts(self):
        """Phase 3: Enhanced contact extraction for remaining missing contacts"""
        logger.info("📞 PHASE 3: Starting contact enhancement for remaining gaps...")
        
        try:
            # Import and run the contact enhancement
            sys.path.append(str(project_root / "scripts"))
            from process_missing_emails import load_missing_jobs, process_contact_enhancement, save_enhanced_results
            
            # Load jobs still missing contacts after enhanced cleaning
            missing_jobs = await load_missing_jobs()
            if not missing_jobs:
                logger.info("[SUCCESS] Phase 3 skipped: No remaining missing contacts after enhanced cleaning")
                return 0
            
            # Limit processing in automation mode to prevent long runs
            max_jobs = min(len(missing_jobs), 50)  # Reduced since V2 should have fewer gaps
            
            logger.info(f"🔍 Processing {max_jobs} remaining jobs for contact enhancement")
            enhanced_jobs = await process_contact_enhancement(missing_jobs, max_jobs)
            
            if enhanced_jobs:
                report = await save_enhanced_results(enhanced_jobs, missing_jobs)
                contacts_found = report['processing_summary']['emails_found'] + report['processing_summary']['phones_found']
                logger.info(f"[SUCCESS] Phase 3 completed: {contacts_found} additional contacts found")
                return contacts_found
            else:
                logger.warning("[WARNING] Phase 3 completed with no enhancements")
                return 0
                
        except Exception as e:
            logger.error(f"[ERROR] Phase 3 error: {e}")
            self.stats['errors'] += 1
            return 0
    
    async def run_full_pipeline_v2(self):
        """Run the complete V2 automated pipeline with enhanced integration"""
        logger.info("🚀 Starting V2 automated job scraper pipeline...")
        logger.info("📋 V2 Features: Enhanced validation + Comprehensive cleaning + Single DB load")
        logger.info(f"📊 Configuration: batch_size={SCRAPER_SETTINGS['batch_size']}, headless={SCRAPER_SETTINGS.get('headless', True)}")
        
        # Wait for database
        if not await self.wait_for_database():
            logger.error("[ERROR] Pipeline aborted: Database not available")
            return False
        
        pipeline_start = time.time()
        
        try:
            # Phase 1: Collect URLs
            if self.running:
                urls_collected = await self.run_phase1_links()
                if urls_collected > 0:
                    self.stats['phases_completed'] += 1
            
            # Phase 2: Enhanced scraping with integrated cleaning and DB loading
            if self.running:
                jobs_loaded = await self.run_phase2_enhanced_scraping()
                if jobs_loaded >= 0:  # 0 is valid (no jobs to process)
                    self.stats['phases_completed'] += 1
            
            # Phase 3: Contact enhancement for remaining gaps only
            if self.running:
                contacts_enhanced = await self.run_phase3_contacts()
                if contacts_enhanced >= 0:  # 0 is valid (no enhancement needed)
                    self.stats['phases_completed'] += 1
            
            # No separate Phase 4 - database loading is integrated in Phase 2
            
            pipeline_duration = time.time() - pipeline_start
            
            # Final report
            self.stats['last_run'] = datetime.now().isoformat()
            
            logger.info("🎉 V2 PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info(f"📊 Enhanced Summary:")
            logger.info(f"   ⏰ Duration: {pipeline_duration:.1f} seconds")
            logger.info(f"   ✅ Phases completed: {self.stats['phases_completed']}/3")
            logger.info(f"   📋 Jobs scraped: {self.stats['total_jobs_processed']}")
            logger.info(f"   🧹 Jobs cleaned: {self.stats['total_jobs_cleaned']}")
            logger.info(f"   💾 Jobs in database: {self.stats['total_jobs_loaded']}")
            logger.info(f"   ❌ Validation failures: {self.stats['validation_failures']}")
            logger.info(f"   🔧 Cleaning failures: {self.stats['cleaning_failures']}")
            logger.info(f"   💥 Database failures: {self.stats['database_failures']}")
            logger.info(f"   🚫 Total errors: {self.stats['errors']}")
            
            return self.stats['errors'] == 0
            
        except Exception as e:
            logger.error(f"[ERROR] V2 Pipeline failed: {e}")
            return False
    
    async def run_continuous_mode(self):
        """Run V2 pipeline in continuous mode with scheduling"""
        logger.info("🔄 Starting V2 continuous automation mode...")
        
        # Run interval from environment or default to 6 hours
        interval_hours = int(os.getenv('PIPELINE_INTERVAL_HOURS', '6'))
        interval_seconds = interval_hours * 3600
        
        while self.running:
            try:
                logger.info(f"🚀 Starting scheduled V2 pipeline run (interval: {interval_hours}h)")
                success = await self.run_full_pipeline_v2()
                
                if success:
                    logger.info(f"[SUCCESS] Scheduled V2 run completed successfully")
                else:
                    logger.warning(f"[WARNING] Scheduled V2 run completed with errors")
                
                if self.running:
                    logger.info(f"😴 Sleeping for {interval_hours} hours until next run...")
                    await asyncio.sleep(interval_seconds)
                    
            except asyncio.CancelledError:
                logger.info("🛑 V2 Continuous mode cancelled")
                break
            except Exception as e:
                logger.error(f"[ERROR] Error in V2 continuous mode: {e}")
                if self.running:
                    logger.info("🔄 Retrying in 30 minutes...")
                    await asyncio.sleep(1800)  # Wait 30 minutes before retry

async def main():
    """Main entry point for V2 pipeline"""
    pipeline = AutomatedPipelineV2()
    
    # Check if continuous mode is requested
    continuous = os.getenv('CONTINUOUS_MODE', 'false').lower() == 'true'
    
    if continuous:
        logger.info("🔄 Running V2 in continuous mode")
        await pipeline.run_continuous_mode()
    else:
        logger.info("⚡ Running single V2 pipeline execution")
        success = await pipeline.run_full_pipeline_v2()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 V2 Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"[ERROR] V2 Fatal error: {e}")
        sys.exit(1)