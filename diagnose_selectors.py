"""
Google Maps Selector Diagnostic Tool
Use this to find the correct selectors for your region/language
"""
import asyncio
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def diagnose_selectors():
    """
    Open Google Maps and help identify the correct selectors
    """
    print("\n" + "="*70)
    print("Google Maps Selector Diagnostic Tool")
    print("="*70)
    print("\nThis tool will:")
    print("1. Open Google Maps in your browser")
    print("2. Try to find the search box using common selectors")
    print("3. Save screenshots for debugging")
    print("4. Show you the page structure")
    print("="*70 + "\n")
    
    keyword = input("Enter keyword to search (e.g., 'restaurants'): ").strip()
    location = input("Enter location (e.g., 'Chennai'): ").strip()
    
    async with async_playwright() as p:
        # Launch browser in NON-headless mode so you can see what's happening
        browser = await p.chromium.launch(headless=False, args=['--start-maximized'])
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # Navigate to Google Maps
        logger.info("Loading Google Maps...")
        await page.goto('https://www.google.com/maps', wait_until='domcontentloaded')
        await asyncio.sleep(5)
        
        # Save initial screenshot
        await page.screenshot(path='screenshot_1_loaded.png', full_page=True)
        logger.info("✓ Screenshot saved: screenshot_1_loaded.png")
        
        # Try different search box selectors
        selectors_to_try = [
            'input#searchboxinput',
            'input[aria-label*="Search"]',
            'input[name="q"]',
            'input[placeholder*="Search"]',
            '#searchbox input',
            'input[type="text"]',
            'form input',
        ]
        
        search_box = None
        working_selector = None
        
        logger.info("\nTrying to find search box with different selectors...")
        for selector in selectors_to_try:
            try:
                element = await page.wait_for_selector(selector, timeout=2000)
                if element:
                    # Check if it's visible
                    is_visible = await element.is_visible()
                    if is_visible:
                        logger.info(f"✓ FOUND working selector: {selector}")
                        search_box = element
                        working_selector = selector
                        break
                    else:
                        logger.info(f"  Found but not visible: {selector}")
            except Exception as e:
                logger.debug(f"  Not found: {selector}")
        
        if search_box:
            logger.info(f"\n✓ Successfully found search box with: {working_selector}")
            
            # Try to search
            search_query = f"{keyword} {location}"
            logger.info(f"Searching for: {search_query}")
            
            await search_box.click()
            await asyncio.sleep(1)
            await search_box.fill(search_query)
            await asyncio.sleep(2)
            await search_box.press('Enter')
            
            logger.info("Waiting for results...")
            await asyncio.sleep(8)
            
            # Save results screenshot
            await page.screenshot(path='screenshot_2_results.png', full_page=True)
            logger.info("✓ Screenshot saved: screenshot_2_results.png")
            
            # Try to find results panel
            results_selectors = [
                'div[role="feed"]',
                'div[aria-label*="Results"]',
                '.m6QErb',
                '[role="main"]'
            ]
            
            logger.info("\nLooking for results panel...")
            for selector in results_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        logger.info(f"✓ Found results panel: {selector}")
                except:
                    pass
            
            # Get page content for manual inspection
            logger.info("\nSaving page HTML for manual inspection...")
            content = await page.content()
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("✓ Page HTML saved: page_source.html")
            
            print("\n" + "="*70)
            print("SUCCESS!")
            print("="*70)
            print(f"Working search box selector: {working_selector}")
            print("\nFiles created:")
            print("  - screenshot_1_loaded.png (Google Maps loaded)")
            print("  - screenshot_2_results.png (Search results)")
            print("  - page_source.html (Page HTML for inspection)")
            print("\nYou can now:")
            print("1. Check the screenshots to see if search worked")
            print("2. Inspect page_source.html to find correct selectors")
            print("3. Update the selectors in scraper.py")
            print("="*70 + "\n")
            
        else:
            logger.error("\n✗ Could not find search box with any selector!")
            logger.info("Saving page HTML for manual inspection...")
            content = await page.content()
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("\n" + "="*70)
            print("SEARCH BOX NOT FOUND")
            print("="*70)
            print("Please check:")
            print("  - screenshot_1_loaded.png")
            print("  - page_source.html")
            print("\nManually inspect these files to find the correct selector")
            print("Look for: <input> tags near the search area")
            print("="*70 + "\n")
        
        # Keep browser open for manual inspection
        input("\nPress Enter to close the browser...")
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(diagnose_selectors())
