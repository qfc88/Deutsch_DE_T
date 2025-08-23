
## Root Directory
```
job-scraper/
├── README.md              # Main project documentation
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker orchestration with new database
├── Dockerfile*            # Container definitions
├── pytest.ini            # Test configuration
├── PROJECT_STRUCTURE.md   # This file
├── start_scheduler.bat    # Windows scheduler launcher
├── test_scheduler.bat     # Windows test runner
├── start_scheduler.sh     # Ubuntu scheduler launcher
├── test_scheduler.sh      # Ubuntu test runner
├── setup_ubuntu.sh        # Ubuntu auto-setup script
└── install_systemd.sh     # Ubuntu systemd service installer
```

## Source Code (`src/`)
Core application source code organized by functionality:
```
src/
├── config/                # Configuration files
│   ├── settings.py        # Application settings
│   └── selectors.py       # Web selectors
├── database/              # Database layer
│   ├── connection.py      # Database connections
│   ├── data_loader.py     # Data loading utilities
│   └── schema.sql         # Database schema
├── models/                # Data models
│   └── job_model.py       # Job data structures
├── scrapers/              # Scraping components
│   ├── job_scraper.py     # Main job scraper
│   ├── link_job.py        # URL collection
│   ├── contact_scraper.py # Contact extraction
│   ├── captcha_solver.py  # CAPTCHA handling
│   └── external_link_handler.py # External link processing
└── utils/                 # Utility functions
    ├── data_validator.py  # Data validation
    ├── file_manager.py    # File operations
    ├── logger.py          # Logging utilities
    └── session_manager.py # Session handling
```

## Scripts (`scripts/`)
Executable scripts for different operations:
```
scripts/
├── run_full_pipeline.py        # Complete pipeline execution
├── run_automated_pipeline.py   # Docker automation pipeline
├── run_job_scraper.py          # Job scraping only
├── run_link_scraper.py         # URL collection only
├── schedule_scraper.py         # Vietnam timezone scheduler (NEW)
├── process_missing_emails.py   # Email processing
├── setup_database.py          # Database initialization
└── test_integration.py        # Integration testing
```

## Tools (`tools/`)
Standalone utility tools and scripts:
```
tools/
├── simple_load.py         # Manual database loader
└── update_start_dates.py  # Date field updater
```

## Debug (`debug/`)
Development and debugging utilities:
```
debug/
├── debug_browser.py           # Browser debugging
├── debug_contact_extraction.py # Contact scraper debugging
└── run_debug.bat             # Windows debug launcher
```

## Tests (`tests/`)
Test files organized by category:
```
tests/
├── manual/                # Manual testing scripts
│   ├── test_core_components.py
│   ├── test_date_parsing.py
│   ├── test_email_cleaning.py
│   ├── test_external_detection.py
│   └── test_fix.py
├── test_scrapers/         # Scraper unit tests
└── test_utils/            # Utility unit tests
```

## Data (`data/`)
Data storage and processing:
```
data/
├── input/                 # Input data files
├── output/               # Scraped data output
│   └── YYYYMMDD_HHMMSS/  # Session-based organization
├── backup/               # Data backups
├── logs/                 # Application logs
└── temp/                 # Temporary files
```

## Configuration Files
- `.env` / `.env.docker`: Environment variables
- `.gitignore`: Git ignore rules
- `docker-compose.yml`: Docker services configuration

## Usage

### For End-to-End Scraping:
```bash
python scripts/run_full_pipeline.py
```

### For Scheduled Scraping (2 AM Vietnam Time):
**Windows:**
```bash
start_scheduler.bat
```

**Ubuntu Server:**
```bash
./start_scheduler.sh           # Foreground
./start_scheduler.sh background # Background
./install_systemd.sh           # System service
```

### For Manual Database Loading:
```bash
python tools/simple_load.py
```

### For Development/Debugging:
```bash
python debug/debug_browser.py
```

### For Ubuntu Server Setup:
```bash
./setup_ubuntu.sh              # Complete auto-setup
```
