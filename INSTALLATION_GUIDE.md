# Google Maps Business Lead Scraper - Installation & Usage Guide

## 📦 Quick Installation

### Step 1: Install Python Dependencies

```bash
# Navigate to the project directory
cd google-maps-scraper

# Install required packages
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

### Step 2: Verify Installation

```bash
# Check if Playwright is installed correctly
playwright --version
```

## 🚀 Quick Start

### Option 1: Interactive Quick Start (Recommended for Beginners)

```bash
python quickstart.py
```

This will present you with a menu of example configurations to try.

### Option 2: Command Line Usage

**Basic Example:**
```bash
python main.py --keyword "cosmetic manufacturer" --location "Chennai"
```

**With Custom Settings:**
```bash
python main.py -k "restaurants" -l "Mumbai" --max-results 50 --headless
```

## 📊 Command Line Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--keyword` | `-k` | ✅ Yes | - | Business type (e.g., "cosmetic manufacturer") |
| `--location` | `-l` | ✅ Yes | - | Location (e.g., "Chennai") |
| `--max-results` | - | ❌ No | 100 | Maximum results to scrape |
| `--headless` | - | ❌ No | False | Run without browser window |
| `--output-dir` | - | ❌ No | output | Where to save CSV files |
| `--verbose` | - | ❌ No | False | Enable debug logging |

## 📋 Common Use Cases

### 1. Small Test Run (10 results, visible browser)
```bash
python main.py -k "cafes" -l "Bangalore" --max-results 10
```

### 2. Medium Run (50 results, headless)
```bash
python main.py -k "hotels" -l "Delhi" --max-results 50 --headless
```

### 3. Large Run (100+ results, headless with logging)
```bash
python main.py -k "gyms" -l "Mumbai" --max-results 150 --headless --verbose
```

### 4. Multiple Locations (run separately)
```bash
python main.py -k "restaurants" -l "Chennai" --max-results 30
python main.py -k "restaurants" -l "Mumbai" --max-results 30
python main.py -k "restaurants" -l "Delhi" --max-results 30
```

## 🔍 What Gets Scraped?

For each business, the scraper attempts to collect:

✅ **Business Name** (required)
✅ **Phone Number** (if available)
✅ **Address** (if available)
✅ **Website URL** (if available)

## 📁 Output

Results are saved as CSV files in the `output/` directory with the naming format:

```
{keyword}_{location}_{timestamp}.csv
```

Example: `cosmetic_manufacturer_Chennai_20240118_143022.csv`

## ⚙️ How It Works

1. **Launches Browser** → Opens Chromium via Playwright
2. **Searches Google Maps** → Enters your keyword + location
3. **Scrolls Results** → Automatically loads more listings
4. **Extracts Data** → Clicks each result and scrapes information
5. **Validates** → Skips entries with insufficient data
6. **Saves to CSV** → Exports clean data to file

## 🛠️ Troubleshooting

### Problem: "playwright: command not found"

**Solution:**
```bash
pip install playwright
playwright install chromium
```

### Problem: No results found

**Solutions:**
- Verify keyword and location are valid
- Run without `--headless` to see browser
- Check internet connection
- Try a more specific search term

### Problem: Scraper is slow

**Solutions:**
- Reduce `--max-results` value
- Use `--headless` mode
- Check system resources (CPU/RAM)

### Problem: Missing data in results

**Explanation:** Some businesses don't provide all information publicly. This is normal. The scraper logs skipped entries.

## ⚠️ Important Notes

### Rate Limiting
- Google may rate-limit excessive requests
- Recommended: Stay under 300 results per session
- Add delays between sessions

### Data Quality
- Not all businesses have complete information
- Phone numbers and websites are optional
- Address may be approximate

### Ethical Usage
- ✅ For learning and small-scale use only
- ✅ Respect Google's Terms of Service
- ❌ Don't use for large-scale commercial scraping
- ❌ Don't scrape excessively or too frequently

### Legal Considerations
- Verify compliance with local laws
- Respect data privacy regulations (GDPR, etc.)
- Consider using Google Places API for production use

## 📈 Performance Tips

### For Faster Scraping:
1. Use `--headless` mode
2. Reduce `--max-results`
3. Close other applications

### For Better Data Quality:
1. Use specific keywords
2. Include city/region in location
3. Manually verify critical data

### For Learning:
1. Start with small result limits (10-20)
2. Run without headless first
3. Enable `--verbose` to understand the process

## 🔄 Example Workflow

**Step 1: Small Test**
```bash
python main.py -k "cosmetic manufacturer" -l "Chennai" --max-results 10
```

**Step 2: Review Results**
Check the `output/` directory for the CSV file

**Step 3: Scale Up**
```bash
python main.py -k "cosmetic manufacturer" -l "Chennai" --max-results 50 --headless
```

**Step 4: Analyze Data**
Open CSV in Excel, Google Sheets, or pandas

## 📞 Getting Help

**Check Logs:**
- Enable `--verbose` for detailed logging
- Logs show what's happening at each step

**Common Issues:**
- Browser not opening → Reinstall playwright browsers
- No results → Check search parameters
- Slow performance → Reduce max-results or use headless

**Error Messages:**
- Read error messages carefully
- Most issues are related to network or selectors
- Google Maps structure may change over time

## 🎓 Learning Objectives

This project demonstrates:
- ✅ Web scraping with Playwright
- ✅ Browser automation techniques
- ✅ Async/await in Python
- ✅ Error handling and retries
- ✅ Data extraction and validation
- ✅ CSV export with pandas
- ✅ CLI argument parsing
- ✅ Modular code structure

## 🔐 Best Practices

1. **Start Small:** Test with 10-20 results first
2. **Use Delays:** Built-in delays prevent detection
3. **Validate Data:** Always verify scraped data
4. **Respect Limits:** Don't scrape excessively
5. **Monitor Logs:** Watch for warnings and errors
6. **Update Code:** Selectors may need updates over time

## 📚 Next Steps

After mastering basic scraping:
1. Experiment with different keywords and locations
2. Analyze patterns in the data
3. Export to different formats (JSON, Excel)
4. Integrate with other tools (CRM, databases)
5. Explore Google Places API for production use

## 🤝 Contributing

This is an educational project. Feel free to:
- Improve the code
- Add new features
- Fix bugs
- Enhance documentation

## ⚖️ Disclaimer

This tool is for educational purposes only. Users are responsible for:
- Complying with Google's Terms of Service
- Respecting data privacy laws
- Using scraped data ethically
- Obtaining necessary permissions

**Remember:** With great power comes great responsibility. Use this tool wisely! 🕷️
