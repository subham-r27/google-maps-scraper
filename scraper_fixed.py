"""
Google Maps Business Lead Scraper - UPDATED VERSION
Core scraping functionality with improved selector handling
"""
import asyncio
import logging
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page
from utils import (
    wait_with_delay,
    scroll_results_panel,
    safe_get_text,
    safe_get_attribute,
    retry_operation,
    wait_for_element,
    clean_phone_number,
    clean_website,
    is_valid_business_data
)

logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    """
    Scraper for collecting business leads from Google Maps
    """
    
    def __init__(self, headless: bool = False, max_results: int = 100):
        """
        Initialize the scraper
        
        Args:
            headless: Run browser in headless mode
            max_results: Maximum number of results to scrape
        """
        self.headless = headless
        self.max_results = max_results
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # Multiple selector options for Google Maps elements (they change frequently)
        self.selectors = {
            'search_box': [
                'input#searchboxinput',
                'input[aria-label*="Search"]',
                'input[name="q"]',
                'input[placeholder*="Search"]',
                '#searchbox input'
            ],
            'search_button': [
                'button#searchbox-searchbutton',
                'button[aria-label*="Search"]',
                'button[type="submit"]',
                '#searchbox button'
            ],
            'results_panel': [
                'div[role="feed"]',
                'div[aria-label*="Results"]',
                '.m6QErb',
                '[role="main"] div.m6QErb'
            ],
            'result_items': [
                'div[role="feed"] > div > div > a',
                'a[href*="/maps/place/"]',
                '.Nv2PK a',
                'div[role="article"] a'
            ],
            'business_name': [
                'h1.DUwDvf',
                'h1[class*="fontHeadline"]',
                'h1.section-hero-header-title',
                'h1.p0Hhde'
            ],
            'address': [
                'button[data-item-id="address"]',
                'button[aria-label*="Address"]',
                '[data-item-id*="address"]',
                'div[class*="address"]'
            ],
            'phone': [
                'button[data-item-id^="phone"]',
                'button[aria-label*="Phone"]',
                '[data-item-id*="phone"]',
                'a[href^="tel:"]'
            ],
            'website': [
                'a[data-item-id="authority"]',
                'a[aria-label*="Website"]',
                'a[data-tooltip*="website"]',
                'a[href*="http"]:not([href*="google"])'
            ],
        }
    
    async def start_browser(self):
        """Start Playwright browser with updated settings"""
        logger.info("Starting browser...")
        self.playwright = await async_playwright().start()
        
        # Launch with more permissive settings
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        # Create context with realistic user agent
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US'
        )
        
        self.page = await self.context.new_page()
        
        # Set extra headers
        await self.page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        logger.info("Browser started successfully")
    
    async def close_browser(self):
        """Close browser and cleanup"""
        logger.info("Closing browser...")
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")
    
    async def find_element_with_selectors(self, selectors: list, timeout: int = 5000):
        """
        Try multiple selectors until one works
        
        Args:
            selectors: List of CSS selectors to try
            timeout: Timeout for each selector in milliseconds
            
        Returns:
            Element if found, None otherwise
        """
        for selector in selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=timeout)
                if element:
                    logger.debug(f"Found element with selector: {selector}")
                    return element
            except Exception:
                continue
        return None
    
    async def search_google_maps(self, keyword: str, location: str):
        """
        Search Google Maps with keyword and location - UPDATED VERSION
        
        Args:
            keyword: Business type to search for
            location: Geographic location
        """
        search_query = f"{keyword} {location}"
        logger.info(f"Searching for: {search_query}")
        
        # Navigate to Google Maps
        logger.info("Loading Google Maps...")
        await self.page.goto('https://www.google.com/maps', wait_until='domcontentloaded')
        await wait_with_delay(3, 5)
        
        # Take screenshot for debugging
        try:
            await self.page.screenshot(path='/tmp/google_maps_loaded.png')
            logger.info("Screenshot saved to /tmp/google_maps_loaded.png")
        except:
            pass
        
        # Try to find and fill search box with multiple selectors
        logger.info("Looking for search box...")
        search_box = await self.find_element_with_selectors(self.selectors['search_box'], timeout=15000)
        
        if not search_box:
            # Fallback: try using the URL parameter method
            logger.warning("Search box not found with selectors, using URL method...")
            search_url = f'https://www.google.com/maps/search/{search_query.replace(" ", "+")}'
            await self.page.goto(search_url, wait_until='domcontentloaded')
            await wait_with_delay(4, 6)
        else:
            # Enter search query
            logger.info("Found search box, entering query...")
            await search_box.click()
            await wait_with_delay(0.5, 1)
            await search_box.fill(search_query)
            await wait_with_delay(1, 2)
            
            # Try to click search button
            search_button = await self.find_element_with_selectors(self.selectors['search_button'], timeout=5000)
            if search_button:
                await search_button.click()
            else:
                # Fallback: press Enter
                logger.info("Search button not found, pressing Enter...")
                await search_box.press('Enter')
        
        # Wait for results to load
        logger.info("Waiting for results to load...")
        results_panel = await self.find_element_with_selectors(self.selectors['results_panel'], timeout=20000)
        
        if not results_panel:
            # Take screenshot for debugging
            try:
                await self.page.screenshot(path='/tmp/no_results.png')
                logger.error("Results panel not found. Screenshot saved to /tmp/no_results.png")
            except:
                pass
            raise Exception("Could not find results panel. Google Maps layout may have changed.")
        
        await wait_with_delay(3, 5)
        logger.info("Search completed successfully")
    
    async def load_all_results(self) -> int:
        """
        Scroll the results panel to load all available listings
        
        Returns:
            Number of result items loaded
        """
        # Find the scrollable panel
        panel_selector = None
        for selector in self.selectors['results_panel']:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    panel_selector = selector
                    break
            except:
                continue
        
        if not panel_selector:
            logger.warning("Could not find results panel for scrolling")
            return 0
        
        # Scroll to load more results
        await scroll_results_panel(self.page, panel_selector, max_scrolls=50)
        
        # Count loaded results using multiple selectors
        result_items = []
        for selector in self.selectors['result_items']:
            try:
                items = await self.page.query_selector_all(selector)
                if len(items) > len(result_items):
                    result_items = items
                    logger.debug(f"Found {len(items)} results with selector: {selector}")
            except:
                continue
        
        count = len(result_items)
        logger.info(f"Loaded {count} result items")
        
        return count
    
    async def extract_business_details(self) -> Dict[str, str]:
        """
        Extract business details from the currently open business page
        
        Returns:
            Dictionary containing business information
        """
        business_data = {
            'name': '',
            'phone': '',
            'address': '',
            'website': ''
        }
        
        try:
            # Wait for business details to load
            await wait_with_delay(2, 3)
            
            # Extract business name with multiple selectors
            for selector in self.selectors['business_name']:
                name_element = await self.page.query_selector(selector)
                if name_element:
                    business_data['name'] = await safe_get_text(name_element)
                    if business_data['name']:
                        break
            
            # Extract address with multiple selectors
            for selector in self.selectors['address']:
                address_element = await self.page.query_selector(selector)
                if address_element:
                    address_text = await safe_get_text(address_element)
                    if address_text:
                        business_data['address'] = address_text.replace('Address:', '').strip()
                        break
            
            # Extract phone number with multiple selectors
            for selector in self.selectors['phone']:
                phone_element = await self.page.query_selector(selector)
                if phone_element:
                    # Try to get from text
                    phone_text = await safe_get_text(phone_element)
                    if phone_text:
                        business_data['phone'] = clean_phone_number(phone_text)
                        break
                    # Try to get from href for tel: links
                    phone_href = await safe_get_attribute(phone_element, 'href')
                    if phone_href and phone_href.startswith('tel:'):
                        business_data['phone'] = phone_href.replace('tel:', '')
                        break
            
            # Extract website with multiple selectors
            for selector in self.selectors['website']:
                website_element = await self.page.query_selector(selector)
                if website_element:
                    website_url = await safe_get_attribute(website_element, 'href')
                    # Filter out Google-related URLs
                    if website_url and 'google.com' not in website_url:
                        business_data['website'] = clean_website(website_url)
                        break
            
            logger.debug(f"Extracted: {business_data['name']}")
            
        except Exception as e:
            logger.error(f"Error extracting business details: {str(e)}")
        
        return business_data
    
    async def scrape_business(self, result_element) -> Optional[Dict[str, str]]:
        """
        Click on a business listing and extract its details
        
        Args:
            result_element: Playwright element handle for the result item
            
        Returns:
            Dictionary with business data or None if extraction failed
        """
        try:
            # Scroll element into view
            await result_element.scroll_into_view_if_needed()
            await wait_with_delay(0.5, 1)
            
            # Click the result
            async def click_operation():
                await result_element.click()
                await wait_with_delay(2, 3)
            
            await retry_operation(click_operation, max_retries=2)
            
            # Extract business details
            business_data = await self.extract_business_details()
            
            # Validate data
            if is_valid_business_data(business_data):
                return business_data
            else:
                logger.warning(f"Skipping business with insufficient data: {business_data.get('name', 'Unknown')}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping business: {str(e)}")
            return None
    
    async def scrape(self, keyword: str, location: str) -> List[Dict[str, str]]:
        """
        Main scraping method
        
        Args:
            keyword: Business type to search for
            location: Geographic location
            
        Returns:
            List of dictionaries containing business data
        """
        businesses = []
        skipped_count = 0
        failed_count = 0
        
        try:
            # Start browser
            await self.start_browser()
            
            # Search Google Maps
            await self.search_google_maps(keyword, location)
            
            # Load all results
            total_results = await self.load_all_results()
            
            if total_results == 0:
                logger.error("No results found. Please check your search terms or try again.")
                return businesses
            
            # Get all result elements using multiple selectors
            result_elements = []
            for selector in self.selectors['result_items']:
                try:
                    items = await self.page.query_selector_all(selector)
                    if len(items) > len(result_elements):
                        result_elements = items
                        logger.info(f"Using selector: {selector} ({len(items)} results)")
                except:
                    continue
            
            # Limit to max_results
            results_to_process = min(len(result_elements), self.max_results)
            logger.info(f"Processing {results_to_process} out of {len(result_elements)} results (limit: {self.max_results})")
            
            # Scrape each business
            for i in range(results_to_process):
                logger.info(f"Processing business {i + 1}/{results_to_process}")
                
                try:
                    # Re-query elements to avoid stale references
                    result_elements = []
                    for selector in self.selectors['result_items']:
                        try:
                            items = await self.page.query_selector_all(selector)
                            if len(items) > len(result_elements):
                                result_elements = items
                        except:
                            continue
                    
                    if i >= len(result_elements):
                        logger.warning(f"Result {i} no longer exists, stopping")
                        break
                    
                    result_element = result_elements[i]
                    
                    # Scrape business data
                    business_data = await self.scrape_business(result_element)
                    
                    if business_data:
                        businesses.append(business_data)
                        logger.info(f"✓ Successfully scraped: {business_data['name']}")
                    else:
                        skipped_count += 1
                        logger.info(f"✗ Skipped business {i + 1}")
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"✗ Failed to scrape business {i + 1}: {str(e)}")
                    continue
            
            # Summary
            logger.info(f"\n{'='*60}")
            logger.info(f"Scraping Summary:")
            logger.info(f"  Total processed: {results_to_process}")
            logger.info(f"  Successfully scraped: {len(businesses)}")
            logger.info(f"  Skipped (insufficient data): {skipped_count}")
            logger.info(f"  Failed (errors): {failed_count}")
            logger.info(f"{'='*60}\n")
            
        finally:
            # Close browser
            await self.close_browser()
        
        return businesses
