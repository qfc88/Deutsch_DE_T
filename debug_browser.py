"""
Debug script to test browser behavior and identify why pages/context are being closed
Run this locally outside Docker to see browser behavior with headless=False
"""

import asyncio
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.append(str(project_root / "src"))
sys.path.append(str(project_root / "src" / "config"))

from playwright.async_api import async_playwright
from config.settings import SCRAPER_SETTINGS, BROWSER_SETTINGS

# Test URLs that are failing
test_urls = [
    "https://www.arbeitsagentur.de/jobsuche/jobdetail/10000-1203467177-S",
    "https://www.arbeitsagentur.de/jobsuche/jobdetail/12608-1305697-14848-1-S", 
    "https://www.arbeitsagentur.de/jobsuche/jobdetail/12608-1305848-15838-1-S"
]

async def debug_browser_issues():
    """Debug browser page closing issues"""
    
    print("🔍 Starting browser debugging...")
    print(f"Headless mode: {SCRAPER_SETTINGS['headless']}")
    print(f"Test URLs: {len(test_urls)}")
    
    async with async_playwright() as p:
        # Launch browser with debug settings
        browser = await p.chromium.launch(
            headless=SCRAPER_SETTINGS['headless'],
            args=BROWSER_SETTINGS['args'],
            slow_mo=1000 if not SCRAPER_SETTINGS['headless'] else 0  # Slow down for debugging
        )
        
        print(f"✅ Browser launched successfully")
        
        try:
            for i, url in enumerate(test_urls):
                print(f"\n--- Testing URL {i+1}: {url} ---")
                
                try:
                    # Create new page
                    page = await browser.new_page()
                    print(f"✅ Page created")
                    
                    # Set viewport  
                    await page.set_viewport_size(BROWSER_SETTINGS['viewport'])
                    print(f"✅ Viewport set")
                    
                    # Try to navigate
                    print(f"🌐 Navigating to: {url}")
                    response = await page.goto(url, wait_until="load", timeout=30000)
                    print(f"✅ Navigation response: {response.status}")
                    
                    # Wait a bit to see what happens
                    await asyncio.sleep(3)
                    
                    # Check if page is still open
                    try:
                        title = await page.title()
                        print(f"✅ Page title: {title[:50]}...")
                    except Exception as title_error:
                        print(f"❌ Could not get page title: {title_error}")
                    
                    # Check for modals or CAPTCHAs
                    try:
                        captcha = await page.locator("img[alt*='captcha'], img[src*='captcha']").count()
                        if captcha > 0:
                            print(f"🔒 CAPTCHA detected: {captcha} elements")
                        else:
                            print("✅ No CAPTCHA detected")
                    except Exception as captcha_error:
                        print(f"❌ Error checking CAPTCHA: {captcha_error}")
                        
                    # Close page properly
                    await page.close()
                    print(f"✅ Page closed properly")
                    
                except Exception as page_error:
                    print(f"❌ Page error: {page_error}")
                    try:
                        await page.close()
                    except:
                        pass
                
                # Wait between tests
                if i < len(test_urls) - 1:
                    print("⏳ Waiting 5 seconds before next test...")
                    await asyncio.sleep(5)
                    
        finally:
            await browser.close()
            print(f"✅ Browser closed")

if __name__ == "__main__":
    print("🚀 Browser Debug Tool")
    print("=" * 50)
    asyncio.run(debug_browser_issues())