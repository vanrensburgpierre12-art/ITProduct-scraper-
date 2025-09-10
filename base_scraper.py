"""
Base scraper class with common functionality for all distributors
"""

import requests
import time
import random
import logging
import csv
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from config import *


class BaseScraper:
    """Base class for all distributor scrapers"""
    
    def __init__(self, distributor_name: str, base_url: str):
        self.distributor_name = distributor_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.products = []
        self.failed_products = []
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(MAIN_LOG),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.distributor_name)
        
    def get_random_delay(self) -> float:
        """Get random delay between requests"""
        return random.uniform(*REQUEST_DELAY)
        
    def make_request(self, url: str, retries: int = MAX_RETRIES) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and delays"""
        for attempt in range(retries):
            try:
                time.sleep(self.get_random_delay())
                response = self.session.get(url, timeout=TIMEOUT)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    self.logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
        
    def setup_selenium_driver(self) -> webdriver.Chrome:
        """Setup Selenium WebDriver for JavaScript-heavy sites"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={random.choice(USER_AGENTS)}')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
        
    def extract_price(self, price_text: str) -> Tuple[Optional[float], Optional[float]]:
        """Extract price including and excluding VAT from price text"""
        if not price_text:
            return None, None
            
        # Remove common currency symbols and clean text
        price_text = price_text.replace('R', '').replace('ZAR', '').replace(',', '').strip()
        
        # Try to extract numbers
        import re
        numbers = re.findall(r'[\d,]+\.?\d*', price_text)
        
        if not numbers:
            return None, None
            
        try:
            # If only one number, assume it's including VAT
            if len(numbers) == 1:
                price_inc_vat = float(numbers[0])
                # Estimate ex VAT (assuming 15% VAT)
                price_ex_vat = round(price_inc_vat / 1.15, 2)
                return price_inc_vat, price_ex_vat
            elif len(numbers) >= 2:
                # First number is usually ex VAT, second is inc VAT
                price_ex_vat = float(numbers[0])
                price_inc_vat = float(numbers[1])
                return price_inc_vat, price_ex_vat
        except ValueError:
            pass
            
        return None, None
        
    def determine_stock_status(self, stock_text: str, stock_quantity: Optional[int] = None) -> str:
        """Determine stock status from text and quantity"""
        if not stock_text:
            return "Unknown"
            
        stock_text = stock_text.lower().strip()
        
        if any(word in stock_text for word in ['in stock', 'available', 'ready']):
            if stock_quantity and stock_quantity < 10:
                return "Low Stock"
            return "In Stock"
        elif any(word in stock_text for word in ['out of stock', 'unavailable', 'sold out']):
            return "Out of Stock"
        elif any(word in stock_text for word in ['notify', 'backorder', 'pre-order']):
            return "Notify Me"
        elif stock_quantity and stock_quantity > 0:
            if stock_quantity < 10:
                return "Low Stock"
            return "In Stock"
        else:
            return "Out of Stock"
            
    def save_to_csv(self, filename: str, products: List[Dict]):
        """Save products to CSV file"""
        if not products:
            self.logger.warning(f"No products to save to {filename}")
            return
            
        fieldnames = [
            'Source', 'Product Name', 'SKU', 'Category', 'Price (Inc VAT)', 
            'Price (Ex VAT)', 'Stock Status', 'Stock Quantity', 'Brand', 
            'Description', 'Product URL', 'Last Updated'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
            
        self.logger.info(f"Saved {len(products)} products to {filename}")
        
    def save_to_json(self, filename: str, products: List[Dict]):
        """Save products to JSON file"""
        if not products:
            self.logger.warning(f"No products to save to {filename}")
            return
            
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(products, jsonfile, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Saved {len(products)} products to {filename}")
        
    def log_failed_product(self, product_url: str, error: str):
        """Log failed product extraction"""
        self.failed_products.append({
            'url': product_url,
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
        self.logger.error(f"Failed to extract product from {product_url}: {error}")
        
    def get_products(self) -> List[Dict]:
        """Abstract method to be implemented by each distributor scraper"""
        raise NotImplementedError("Subclasses must implement get_products method")
        
    def run(self) -> List[Dict]:
        """Run the scraper and return products"""
        self.logger.info(f"Starting {self.distributor_name} scraper")
        try:
            products = self.get_products()
            self.logger.info(f"Successfully scraped {len(products)} products from {self.distributor_name}")
            return products
        except Exception as e:
            self.logger.error(f"Error running {self.distributor_name} scraper: {e}")
            return []