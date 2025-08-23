#!/usr/bin/env python3
"""
Docker Entrypoint Script
Dynamically selects pipeline version based on environment variables
Supports both V1 and V2 pipelines with graceful fallback
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ENTRYPOINT - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entrypoint - select and run appropriate pipeline"""
    
    # Get pipeline version from environment
    pipeline_version = os.getenv('PIPELINE_VERSION', 'v2').lower()
    
    logger.info("🐳 Docker Container Starting...")
    logger.info(f"📋 Pipeline Version: {pipeline_version}")
    
    # Environment configuration summary
    logger.info("📊 Configuration Summary:")
    logger.info(f"   🔧 Automation Mode: {os.getenv('AUTOMATION_MODE', 'false')}")
    logger.info(f"   🤖 Auto Solve CAPTCHA: {os.getenv('AUTO_SOLVE_CAPTCHA', 'false')}")
    logger.info(f"   👁️  Headless Mode: {os.getenv('SCRAPER_HEADLESS', 'true')}")
    logger.info(f"   📦 Batch Size: {os.getenv('SCRAPER_BATCH_SIZE', '50')}")
    logger.info(f"   💾 Database: {os.getenv('DB_NAME', 'scrape')}")
    
    if pipeline_version == 'v2':
        logger.info("✨ V2 Features:")
        logger.info(f"   ✅ Comprehensive Validation: {os.getenv('ENABLE_COMPREHENSIVE_VALIDATION', 'true')}")
        logger.info(f"   🧹 Enhanced Cleaning: {os.getenv('ENABLE_ENHANCED_CLEANING', 'true')}")
        logger.info(f"   💾 Single DB Load: {os.getenv('ENABLE_SINGLE_DB_LOAD', 'true')}")
    
    # Determine which pipeline to run
    if pipeline_version == 'v2':
        script_path = "scripts/run_automated_pipeline_v2.py"
        if not Path(script_path).exists():
            logger.warning("⚠️ V2 pipeline not found, falling back to V1")
            script_path = "scripts/run_automated_pipeline.py"
    elif pipeline_version == 'v1' or pipeline_version == '1':
        script_path = "scripts/run_automated_pipeline.py"
    else:
        logger.warning(f"⚠️ Unknown pipeline version '{pipeline_version}', defaulting to V2")
        script_path = "scripts/run_automated_pipeline_v2.py"
        if not Path(script_path).exists():
            script_path = "scripts/run_automated_pipeline.py"
    
    # Final confirmation
    logger.info(f"🚀 Starting: {script_path}")
    
    try:
        # Import and run the selected pipeline
        if 'v2' in script_path:
            from run_automated_pipeline_v2 import main as pipeline_main
        else:
            from run_automated_pipeline import main as pipeline_main
        
        # Run the pipeline
        import asyncio
        asyncio.run(pipeline_main())
        
    except ImportError as e:
        logger.error(f"❌ Failed to import pipeline: {e}")
        logger.info("🔄 Falling back to direct execution")
        
        # Fallback to direct execution
        import subprocess
        try:
            result = subprocess.run([sys.executable, script_path], check=True)
            sys.exit(result.returncode)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Pipeline execution failed: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Pipeline error: {e}")
        sys.exit(1)
    
    logger.info("✅ Pipeline completed successfully")

if __name__ == "__main__":
    main()