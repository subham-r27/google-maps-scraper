# Google Maps Business Lead Scraper

A Python-based browser automation tool using Playwright to collect business leads from Google Maps for small-scale usage and learning purposes.

## Features

- 🔍 Search Google Maps by keyword and location
- 📜 Automatic scrolling to load all available results
- 📊 Extract business name, phone, address, and website
- 🔄 Retry logic for handling failures
- 📁 Export data to CSV format
- ⚙️ Configurable result limits
- 🪵 Comprehensive logging
- 🎯 Smart validation and data cleaning

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### 1. Clone or Download the Project

```bash
# If you have the files, navigate to the project directory
cd google-maps-scraper
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Project Structure

```
google-maps-scraper/
├── main.py           # CLI entry point
├── scraper.py        # Core scraping logic
├── utils.py          # Helper functions
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── output/           # Output CSV files (created automatically)
```

## Usage

### Basic Usage

```bash
python main.py --keyword "cosmetic manufacturer" --location "Chennai"
```

### Advanced Options

```bash
# Scrape with custom max results
python main.py -k "restaurants" -l "Mumbai" --max-results 50

# Run in headless mode (no browser window)
python main.py -k "hotels" -l "Delhi" --headless --max-results 200

# Specify custom output directory
python main.py -k "cafes" -l "Bangalore" --output-dir "my_leads"

# Enable verbose logging
python main.py -k "gyms" -l "Pune" --verbose
```

### Command Line Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--keyword` | `-k` | Yes | - | Business type to search for |
| `--location` | `-l` | Yes | - | Geographic location |
| `--max-results` | - | No | 100 | Maximum number of results to scrape |
| `--headless` | - | No | False | Run browser in headless mode |
| `--output-dir` | - | No | output | Directory to save CSV files |
| `--verbose` | - | No | False | Enable debug logging |

## Output Format

Results are saved as CSV files with the following columns:

| Column | Description |
|--------|-------------|
| name | Business name |
| phone | Phone number (if available) |
| address | Physical address (if available) |
| website | Website URL (if available) |

### Output File Naming

Files are automatically named with the format:
```
{keyword}_{location}_{timestamp}.csv
```

Example: `cosmetic_manufacturer_Chennai_20240118_143022.csv`

## How It Works

1. **Browser Launch**: Opens a Chromium browser using Playwright
2. **Search**: Navigates to Google Maps and searches for the keyword + location
3. **Scrolling**: Continuously scrolls the results panel to load more listings
4. **Extraction**: Clicks each listing and extracts:
   - Business name (from heading)
   - Address (if visible)
   - Phone number (if visible)
   - Website link (if available)
5. **Validation**: Skips entries with missing critical data
6. **Storage**: Saves results to CSV in the output directory

## Reliability Features

- **Smart Delays**: Random delays (1-3 seconds) between actions to mimic human behavior
- **Retry Logic**: Automatically retries failed operations up to 3 times
- **Element Waiting**: Waits for elements to load before interaction
- **Error Handling**: Gracefully handles and logs errors
- **Data Validation**: Skips businesses without minimum required information
- **Scroll Detection**: Stops scrolling when no new results appear

## Limitations

- **Rate Limiting**: Google may rate-limit excessive requests
- **Max Results**: Configurable limit (default 100, max recommended 300)
- **Data Availability**: Not all businesses have complete information
- **Captchas**: May encounter captchas with heavy usage
- **Dynamic Content**: Google Maps structure may change over time

## Best Practices

1. **Start Small**: Begin with small result limits (10-20) to test
2. **Use Delays**: Don't set max-results too high to avoid detection
3. **Headless Mode**: Use `--headless` for faster, less resource-intensive scraping
4. **Respect Limits**: Don't scrape excessively; this is for learning purposes
5. **Monitor Logs**: Check logs for warnings and errors
6. **Update Selectors**: If scraping stops working, selectors may need updating

## Troubleshooting

### Issue: Browser doesn't open

```bash
# Reinstall Playwright browsers
playwright install chromium
```

### Issue: No results found

- Check if your keyword and location are valid
- Try running without `--headless` to see what's happening
- Verify internet connection

### Issue: Slow performance

- Reduce `--max-results`
- Use `--headless` mode
- Check system resources

### Issue: Missing data

- Some businesses don't provide all information
- This is expected; the scraper logs skipped entries

## Examples

### Example 1: Cosmetic Manufacturers in Chennai

```bash
python main.py -k "cosmetic manufacturer" -l "Chennai" --max-results 50
```

### Example 2: Restaurants in Mumbai (Headless)

```bash
python main.py -k "restaurants" -l "Mumbai" --headless --max-results 100
```

### Example 3: Hotels in Multiple Cities (Run Separately)

```bash
python main.py -k "hotels" -l "Delhi" --max-results 30
python main.py -k "hotels" -l "Bangalore" --max-results 30
python main.py -k "hotels" -l "Chennai" --max-results 30
```

## Ethical Considerations

⚠️ **Important Notice**:

- This tool is for **educational and small-scale use only**
- Respect Google's Terms of Service
- Do not scrape excessively or use for commercial purposes
- Consider using Google Places API for production applications
- Be mindful of data privacy and GDPR regulations
- Always verify and validate scraped data

## Dependencies

- `playwright==1.40.0` - Browser automation
- `pandas==2.1.4` - Data manipulation and CSV export

## License

This project is for educational purposes only. Use responsibly and ethically.

## Support

For issues or questions:
1. Check the logs for error messages
2. Review the troubleshooting section
3. Ensure all dependencies are installed correctly
4. Verify Python version compatibility (3.8+)

## Disclaimer

This tool is provided as-is for educational purposes. The authors are not responsible for misuse or any violations of terms of service. Always ensure you have permission to scrape data and comply with all applicable laws and regulations.
