"""
Utility functions for Google Maps scraper
"""
import asyncio
import logging
from typing import Optional
from playwright.async_api import Page, ElementHandle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def wait_with_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """
    Wait for a random time between min and max seconds
    
    Args:
        min_seconds: Minimum wait time
        max_seconds: Maximum wait time
    """
    import random
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


async def scroll_results_panel(page: Page, panel_selector: str, max_scrolls: int = 50) -> int:
    """
    Scroll the results panel to load more listings
    
    Args:
        page: Playwright page object
        panel_selector: CSS selector for the scrollable panel
        max_scrolls: Maximum number of scroll attempts
        
    Returns:
        Number of scrolls performed
    """
    logger.info("Starting to scroll results panel...")
    scroll_count = 0
    no_change_count = 0
    previous_height = 0
    
    for i in range(max_scrolls):
        try:
            # Get current scroll height
            current_height = await page.evaluate(f'''
                () => {{
                    const panel = document.querySelector("{panel_selector}");
                    return panel ? panel.scrollHeight : 0;
                }}
            ''')
            
            # Scroll to bottom
            await page.evaluate(f'''
                () => {{
                    const panel = document.querySelector("{panel_selector}");
                    if (panel) {{
                        panel.scrollTo(0, panel.scrollHeight);
                    }}
                }}
            ''')
            
            # Wait for content to load
            await wait_with_delay(1.5, 2.5)
            
            # Check if new content loaded
            if current_height == previous_height:
                no_change_count += 1
                logger.debug(f"No height change detected (attempt {no_change_count}/3)")
                
                # If no change after 3 attempts, we've reached the end
                if no_change_count >= 3:
                    logger.info(f"Reached end of results after {scroll_count} scrolls")
                    break
            else:
                no_change_count = 0
                scroll_count += 1
                logger.debug(f"Scroll {scroll_count}: Height changed from {previous_height} to {current_height}")
            
            previous_height = current_height
            
        except Exception as e:
            logger.error(f"Error during scrolling: {str(e)}")
            break
    
    logger.info(f"Completed scrolling. Total scrolls: {scroll_count}")
    return scroll_count


async def safe_get_text(element: Optional[ElementHandle], default: str = "") -> str:
    """
    Safely extract text from an element
    
    Args:
        element: Playwright element handle
        default: Default value if extraction fails
        
    Returns:
        Extracted text or default value
    """
    if not element:
        return default
    
    try:
        text = await element.inner_text()
        return text.strip() if text else default
    except Exception as e:
        logger.debug(f"Error extracting text: {str(e)}")
        return default


async def safe_get_attribute(element: Optional[ElementHandle], attribute: str, default: str = "") -> str:
    """
    Safely extract an attribute from an element
    
    Args:
        element: Playwright element handle
        attribute: Attribute name to extract
        default: Default value if extraction fails
        
    Returns:
        Attribute value or default value
    """
    if not element:
        return default
    
    try:
        value = await element.get_attribute(attribute)
        return value.strip() if value else default
    except Exception as e:
        logger.debug(f"Error extracting attribute {attribute}: {str(e)}")
        return default


async def retry_operation(operation, max_retries: int = 3, delay: float = 2.0):
    """
    Retry an async operation with exponential backoff
    
    Args:
        operation: Async function to retry
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (doubles each time)
        
    Returns:
        Result of the operation
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"All {max_retries} attempts failed")
    
    raise last_exception


async def wait_for_element(page: Page, selector: str, timeout: int = 10000) -> bool:
    """
    Wait for an element to appear on the page
    
    Args:
        page: Playwright page object
        selector: CSS selector to wait for
        timeout: Timeout in milliseconds
        
    Returns:
        True if element appeared, False otherwise
    """
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception as e:
        logger.debug(f"Element {selector} not found within timeout: {str(e)}")
        return False


def clean_phone_number(phone: str) -> str:
    """
    Clean and format phone number
    
    Args:
        phone: Raw phone number string
        
    Returns:
        Cleaned phone number
    """
    if not phone:
        return ""
    
    # Remove common prefixes and clean up
    phone = phone.replace("Phone:", "").replace("Tel:", "").strip()
    return phone


def clean_website(website: str) -> str:
    """
    Clean and format website URL
    
    Args:
        website: Raw website URL
        
    Returns:
        Cleaned website URL
    """
    if not website:
        return ""
    
    # Ensure it starts with http/https
    if website and not website.startswith(('http://', 'https://')):
        website = 'https://' + website
    
    return website


def is_valid_business_data(data: dict) -> bool:
    """
    Check if business data has minimum required fields
    
    Args:
        data: Dictionary containing business information
        
    Returns:
        True if data is valid, False otherwise
    """
    # At minimum, we need a name
    if not data.get('name'):
        return False
    
    # Prefer entries that have at least one contact method
    has_contact = bool(data.get('phone') or data.get('website') or data.get('address'))
    
    return has_contact
