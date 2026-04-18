"""
Google Maps Business Lead Scraper
Core scraping functionality
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
        
        # Selectors for Google Maps elements
        self.selectors = {
            'search_box': 'input#searchboxinput',
            'search_button': 'button#searchbox-searchbutton',
            'results_panel': 'div[role="feed"]',
            'result_items': 'div[role="feed"] > div > div > a',
            'business_name': 'h1.DUwDvf',
            'address': 'button[data-item-id="address"]',
            'phone': 'button[data-item-id^="phone"]',
            'website': 'a[data-item-id="authority"]',
        }
    
    async def start_browser(self):
        """Start Playwright browser"""
        logger.info("Starting browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--start-maximized']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
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
    
    async def search_google_maps(self, keyword: str, location: str):
        """
        Search Google Maps with keyword and location
        
        Args:
            keyword: Business type to search for
            location: Geographic location
        """
        search_query = f"{keyword} {location}"
        logger.info(f"Searching for: {search_query}")
        
        # Navigate to Google Maps
        await self.page.goto('https://www.google.com/maps', wait_until='domcontentloaded')
        await wait_with_delay(2, 3)
        
        # Enter search query
        search_box = await self.page.wait_for_selector(self.selectors['search_box'], timeout=10000)
        await search_box.fill(search_query)
        await wait_with_delay(1, 2)
        
        # Click search button
        search_button = await self.page.query_selector(self.selectors['search_button'])
        if search_button:
            await search_button.click()
        else:
            # Fallback: press Enter
            await search_box.press('Enter')
        
        # Wait for results to load
        logger.info("Waiting for results to load...")
        await wait_for_element(self.page, self.selectors['results_panel'], timeout=15000)
        await wait_with_delay(3, 4)
        
        logger.info("Search completed successfully")
    
    async def load_all_results(self) -> int:
        """
        Scroll the results panel to load all available listings
        
        Returns:
            Number of result items loaded
        """
        # Scroll to load more results
        await scroll_results_panel(
            self.page,
            self.selectors['results_panel'],
            max_scrolls=50
        )
        
        # Count loaded results
        result_items = await self.page.query_selector_all(self.selectors['result_items'])
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
            await wait_with_delay(1.5, 2.5)
            
            # Extract business name
            name_element = await self.page.query_selector(self.selectors['business_name'])
            business_data['name'] = await safe_get_text(name_element)
            
            # Extract address
            address_element = await self.page.query_selector(self.selectors['address'])
            if address_element:
                address_text = await safe_get_text(address_element)
                # Remove "Address: " prefix if present
                business_data['address'] = address_text.replace('Address:', '').strip()
            
            # Extract phone number
            phone_element = await self.page.query_selector(self.selectors['phone'])
            if phone_element:
                phone_text = await safe_get_text(phone_element)
                business_data['phone'] = clean_phone_number(phone_text)
            
            # Extract website
            website_element = await self.page.query_selector(self.selectors['website'])
            if website_element:
                website_url = await safe_get_attribute(website_element, 'href')
                business_data['website'] = clean_website(website_url)
            
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
            
            # Get all result elements
            result_elements = await self.page.query_selector_all(self.selectors['result_items'])
            
            # Limit to max_results
            results_to_process = min(len(result_elements), self.max_results)
            logger.info(f"Processing {results_to_process} out of {len(result_elements)} results (limit: {self.max_results})")
            
            # Scrape each business
            for i in range(results_to_process):
                logger.info(f"Processing business {i + 1}/{results_to_process}")
                
                try:
                    # Re-query elements to avoid stale references
                    result_elements = await self.page.query_selector_all(self.selectors['result_items'])
                    
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
