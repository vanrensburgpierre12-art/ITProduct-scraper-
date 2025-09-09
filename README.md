# Electronics Distributors Scraper

A comprehensive Python scraper for collecting product and stock information from South African electronics distributors.

## Features

- **Multi-Distributor Support**: Scrapes from Communica, MicroRobotics, and Miro Distribution
- **Web Interface**: Modern Flask-based UI for easy operation
- **Command Line Interface**: Full CLI support for automation
- **Multiple Output Formats**: CSV and JSON export options
- **Real-time Progress**: Live status updates during scraping
- **Error Handling**: Robust error handling and logging
- **Stock Tracking**: Detailed stock status and quantity information

## Supported Distributors

1. **Communica** (https://www.communica.co.za/)
   - Stock Status: "In Stock", "Notify Me", "Only X left"
   
2. **MicroRobotics** (https://www.robotics.org.za/)
   - Stock Status: Exact stock numbers (e.g., "Stock: 47")
   
3. **Miro Distribution** (https://miro.co.za/)
   - Stock Status: "In Stock", "Backorder", "Limited Stock"

## Data Extracted

For each product:
- Source (Distributor name)
- Product Name
- SKU/Product Code
- Category (from breadcrumb navigation)
- Price (including VAT)
- Price (excluding VAT)
- Stock Status
- Stock Quantity (when available)
- Brand/Manufacturer
- Description
- Product URL
- Last Updated timestamp

## Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Chrome browser (required for Selenium)

## Usage

### Web Interface (Recommended)

Start the web interface:
```bash
python main.py --web
```

Then open your browser and go to: http://localhost:5000

### Command Line Interface

Scrape all distributors:
```bash
python main.py
```

Scrape specific distributors:
```bash
python main.py --distributors Communica MicroRobotics
```

Custom output file:
```bash
python main.py --output my_products.csv
```

Export as JSON:
```bash
python main.py --format json
```

### Programmatic Usage

```python
from communica_scraper import CommunicaScraper
from microrobotics_scraper import MicroRoboticsScraper
from miro_scraper import MiroScraper

# Scrape Communica
communica = CommunicaScraper()
products = communica.run()

# Save to CSV
communica.save_to_csv('communica_products.csv', products)
```

## Output Files

- `distributors_products.csv` - Combined results from all distributors
- `communica.csv` - Communica products only
- `microrobotics.csv` - MicroRobotics products only
- `miro.csv` - Miro Distribution products only
- `distributors_products.json` - JSON format (when requested)

## Configuration

Edit `config.py` to modify:
- Request delays
- Timeout settings
- Output directories
- User agents
- Logging settings

## Scheduling

For daily automated runs, add to crontab:
```bash
# Run every day at 2 AM
0 2 * * * cd /path/to/scraper && python main.py
```

## Error Handling

- Failed products are logged to `logs/errors.log`
- Individual scraper errors don't stop the entire process
- Retry logic for network requests
- Graceful handling of missing elements

## Requirements

- Python 3.7+
- Chrome browser
- Internet connection
- Required Python packages (see requirements.txt)

## Troubleshooting

1. **Chrome not found**: Install Chrome browser
2. **Permission errors**: Check file permissions for output directories
3. **Network timeouts**: Increase timeout values in config.py
4. **Memory issues**: Reduce batch sizes or add delays

## Legal Notice

This scraper is for educational and research purposes. Please respect the robots.txt files and terms of service of the target websites. Use appropriate delays between requests to avoid overloading the servers.

## License

This project is provided as-is for educational purposes.