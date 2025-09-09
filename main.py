"""
Main execution script for the electronics distributors scraper
"""

import os
import sys
import argparse
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from communica_scraper import CommunicaScraper
from microrobotics_scraper import MicroRoboticsScraper
from miro_scraper import MiroScraper
from config import *


def run_scraper(distributor_name, scraper_class):
    """Run a specific scraper and return results"""
    print(f"\n{'='*50}")
    print(f"Starting {distributor_name} scraper...")
    print(f"{'='*50}")
    
    try:
        scraper = scraper_class()
        products = scraper.run()
        
        print(f"\n✅ {distributor_name} completed successfully!")
        print(f"   Found {len(products)} products")
        
        # Save individual CSV
        individual_csv = os.path.join(OUTPUT_DIR, f"{distributor_name.lower().replace(' ', '_')}.csv")
        scraper.save_to_csv(individual_csv, products)
        
        return products
        
    except Exception as e:
        print(f"\n❌ {distributor_name} failed: {e}")
        return []


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Electronics Distributors Scraper')
    parser.add_argument('--distributors', nargs='+', 
                       choices=['Communica', 'MicroRobotics', 'Miro'],
                       default=['Communica', 'MicroRobotics', 'Miro'],
                       help='Distributors to scrape (default: all)')
    parser.add_argument('--output', '-o', default=MAIN_CSV,
                       help='Output CSV file path')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv',
                       help='Output format (default: csv)')
    parser.add_argument('--web', action='store_true',
                       help='Start web interface instead of command line')
    
    args = parser.parse_args()
    
    if args.web:
        # Start web interface
        print("Starting web interface...")
        print("Open your browser and go to: http://localhost:5000")
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        return
    
    print("🔧 Electronics Distributors Scraper")
    print("=" * 50)
    print(f"Target distributors: {', '.join(args.distributors)}")
    print(f"Output format: {args.format}")
    print(f"Output file: {args.output}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Scrapers mapping
    scrapers = {
        'Communica': CommunicaScraper,
        'MicroRobotics': MicroRoboticsScraper,
        'Miro': MiroScraper
    }
    
    all_products = []
    total_products = 0
    successful_distributors = 0
    
    # Run scrapers
    for distributor in args.distributors:
        if distributor in scrapers:
            products = run_scraper(distributor, scrapers[distributor])
            all_products.extend(products)
            total_products += len(products)
            if products:
                successful_distributors += 1
        else:
            print(f"\n⚠️  Unknown distributor: {distributor}")
    
    # Save combined results
    if all_products:
        print(f"\n{'='*50}")
        print("Saving combined results...")
        print(f"{'='*50}")
        
        if args.format == 'csv':
            # Create a temporary scraper instance to use save_to_csv method
            temp_scraper = CommunicaScraper()
            temp_scraper.save_to_csv(args.output, all_products)
        else:
            # Save as JSON
            import json
            with open(args.output.replace('.csv', '.json'), 'w', encoding='utf-8') as f:
                json.dump(all_products, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Combined results saved to: {args.output}")
        
        # Print summary
        print(f"\n{'='*50}")
        print("SCRAPING SUMMARY")
        print(f"{'='*50}")
        print(f"Total products scraped: {total_products}")
        print(f"Successful distributors: {successful_distributors}/{len(args.distributors)}")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Print distributor breakdown
        from collections import Counter
        distributor_counts = Counter([p['Source'] for p in all_products])
        print(f"\nProducts by distributor:")
        for distributor, count in distributor_counts.items():
            print(f"  {distributor}: {count} products")
            
    else:
        print(f"\n❌ No products were scraped successfully")
        sys.exit(1)


if __name__ == "__main__":
    main()