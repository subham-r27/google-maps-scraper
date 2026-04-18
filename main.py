"""
Google Maps Business Lead Scraper - Main Entry Point
"""
import asyncio
import argparse
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from scraper import GoogleMapsScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def save_to_csv(businesses: list, keyword: str, location: str, output_dir: str = 'output'):
    """
    Save scraped business data to CSV file
    
    Args:
        businesses: List of business dictionaries
        keyword: Search keyword used
        location: Search location used
        output_dir: Directory to save output files
    """
    if not businesses:
        logger.warning("No businesses to save")
        return
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{keyword.replace(' ', '_')}_{location.replace(' ', '_')}_{timestamp}.csv"
    filepath = output_path / filename
    
    # Convert to DataFrame and save
    df = pd.DataFrame(businesses)
    
    # Ensure column order
    columns = ['name', 'phone', 'address', 'website']
    df = df[columns]
    
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    logger.info(f"✓ Saved {len(businesses)} businesses to: {filepath}")
    
    # Print preview
    print("\n" + "="*60)
    print("Preview of scraped data:")
    print("="*60)
    print(df.head(10).to_string(index=False))
    print("="*60)
    print(f"\nFull data saved to: {filepath}\n")


async def main():
    """Main execution function"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Google Maps Business Lead Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --keyword "cosmetic manufacturer" --location "Chennai"
  python main.py -k "restaurants" -l "Mumbai" --max-results 50
  python main.py -k "hotels" -l "Delhi" --headless --max-results 200
        """
    )
    
    parser.add_argument(
        '-k', '--keyword',
        type=str,
        required=True,
        help='Business type or keyword to search for (e.g., "cosmetic manufacturer")'
    )
    
    parser.add_argument(
        '-l', '--location',
        type=str,
        required=True,
        help='Geographic location (e.g., "Chennai", "Mumbai, India")'
    )
    
    parser.add_argument(
        '--max-results',
        type=int,
        default=100,
        help='Maximum number of results to scrape (default: 100)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (no GUI)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Directory to save output CSV files (default: output)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print configuration
    print("\n" + "="*60)
    print("Google Maps Business Lead Scraper")
    print("="*60)
    print(f"Keyword:      {args.keyword}")
    print(f"Location:     {args.location}")
    print(f"Max Results:  {args.max_results}")
    print(f"Headless:     {args.headless}")
    print(f"Output Dir:   {args.output_dir}")
    print("="*60 + "\n")
    
    # Validate max_results
    if args.max_results < 1:
        logger.error("max-results must be at least 1")
        return
    
    if args.max_results > 500:
        logger.warning("Large max-results value may take a long time and could trigger rate limits")
    
    # Create scraper instance
    scraper = GoogleMapsScraper(
        headless=args.headless,
        max_results=args.max_results
    )
    
    try:
        # Run scraper
        logger.info("Starting scraping process...")
        businesses = await scraper.scrape(args.keyword, args.location)
        
        # Save results
        if businesses:
            save_to_csv(businesses, args.keyword, args.location, args.output_dir)
        else:
            logger.warning("No businesses were scraped. Check your search parameters.")
        
    except KeyboardInterrupt:
        logger.info("\nScraping interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        logger.info("Scraping session completed")


if __name__ == '__main__':
    # Run the async main function
    asyncio.run(main())
