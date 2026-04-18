# Example Configuration File
# This file demonstrates how you could extend the scraper with a config file

# Search Parameters
KEYWORD = "cosmetic manufacturer"
LOCATION = "Chennai"
MAX_RESULTS = 100

# Browser Settings
HEADLESS = False
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# Timing Settings (seconds)
MIN_DELAY = 1.0
MAX_DELAY = 3.0
SCROLL_DELAY = 2.0

# Retry Settings
MAX_RETRIES = 3
RETRY_DELAY = 2.0

# Output Settings
OUTPUT_DIR = "output"
CSV_ENCODING = "utf-8"

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Selector Overrides (if Google Maps changes their structure)
# Leave empty to use defaults
SELECTORS = {
    # "search_box": "input#searchboxinput",
    # "search_button": "button#searchbox-searchbutton",
    # "results_panel": "div[role='feed']",
    # "result_items": "div[role='feed'] > div > div > a",
    # "business_name": "h1.DUwDvf",
    # "address": "button[data-item-id='address']",
    # "phone": "button[data-item-id^='phone']",
    # "website": "a[data-item-id='authority']",
}

# Data Validation
REQUIRE_NAME = True
REQUIRE_PHONE = False
REQUIRE_ADDRESS = False
REQUIRE_WEBSITE = False

# Advanced Features
ENABLE_SCREENSHOTS = False  # Save screenshot of each business
SCREENSHOT_DIR = "screenshots"
ENABLE_DEDUPLICATION = True  # Remove duplicate entries
