"""
MicroRobotics scraper for https://www.robotics.org.za/
"""

import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from base_scraper import BaseScraper


class MicroRoboticsScraper(BaseScraper):
    """Scraper for MicroRobotics electronics distributor"""
    
    def __init__(self):
        super().__init__("MicroRobotics", "https://www.robotics.org.za/")
        self.driver = None
        
    def setup_driver(self):
        """Setup Selenium driver for JavaScript-heavy content"""
        if not self.driver:
            self.driver = self.setup_selenium_driver()
            
    def close_driver(self):
        """Close Selenium driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    def get_categories(self) -> list:
        """Get all product categories using Selenium"""
        categories = []
        try:
            self.setup_driver()
            self.driver.get(self.base_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for category links
            category_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/category/"], a[href*="/products/"], a[href*="/shop/"]')
            
            for link in category_links:
                href = link.get_attribute('href')
                if href and href not in categories:
                    categories.append(href)
                    
            self.logger.info(f"Found {len(categories)} categories")
            return categories
            
        except Exception as e:
            self.logger.error(f"Error getting categories: {e}")
            return categories
            
    def get_products_from_category(self, category_url: str) -> list:
        """Get all products from a specific category"""
        products = []
        page = 1
        
        try:
            self.setup_driver()
            
            while True:
                # Navigate to category page
                if page > 1:
                    if '?' in category_url:
                        page_url = f"{category_url}&page={page}"
                    else:
                        page_url = f"{category_url}?page={page}"
                else:
                    page_url = category_url
                    
                self.driver.get(page_url)
                
                # Wait for products to load
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".product, .item, [class*='product']"))
                    )
                except TimeoutException:
                    self.logger.warning(f"No products found on page {page} of {category_url}")
                    break
                    
                # Find product links
                product_links = self.find_product_links()
                if not product_links:
                    break
                    
                # Extract product details
                for product_url in product_links:
                    try:
                        product_data = self.extract_product_details(product_url)
                        if product_data:
                            products.append(product_data)
                    except Exception as e:
                        self.log_failed_product(product_url, e)
                        
                page += 1
                
                # Safety check
                if page > 50:
                    self.logger.warning(f"Reached page limit for {category_url}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Error processing category {category_url}: {e}")
            
        return products
        
    def find_product_links(self) -> list:
        """Find all product links on current page"""
        product_links = []
        
        try:
            # Common selectors for product links
            selectors = [
                'a[href*="/product/"]',
                'a[href*="/item/"]',
                'a[href*="/shop/"]',
                '.product-item a',
                '.product-link',
                '.product-title a',
                'h3 a',
                'h4 a',
                '.item-title a'
            ]
            
            for selector in selectors:
                links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for link in links:
                    href = link.get_attribute('href')
                    if href and href not in product_links:
                        product_links.append(href)
                        
        except Exception as e:
            self.logger.error(f"Error finding product links: {e}")
            
        return product_links
        
    def extract_product_details(self, product_url: str) -> dict:
        """Extract detailed product information from product page"""
        try:
            self.driver.get(product_url)
            
            # Wait for product details to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract product information
            product_name = self.extract_product_name()
            sku = self.extract_sku()
            category = self.extract_category()
            price_inc_vat, price_ex_vat = self.extract_prices()
            stock_status, stock_quantity = self.extract_stock_info()
            brand = self.extract_brand()
            description = self.extract_description()
            
            return {
                'Source': self.distributor_name,
                'Product Name': product_name,
                'SKU': sku,
                'Category': category,
                'Price (Inc VAT)': price_inc_vat,
                'Price (Ex VAT)': price_ex_vat,
                'Stock Status': stock_status,
                'Stock Quantity': stock_quantity,
                'Brand': brand,
                'Description': description,
                'Product URL': product_url,
                'Last Updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log_failed_product(product_url, e)
            return None
            
    def extract_product_name(self) -> str:
        """Extract product name from product page"""
        selectors = [
            'h1.product-title',
            'h1',
            '.product-name',
            '.product-title',
            '.item-title',
            'title'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    return element.text.strip()
            except NoSuchElementException:
                continue
                
        return "Unknown Product"
        
    def extract_sku(self) -> str:
        """Extract SKU/Product Code"""
        # Look for SKU in various places
        sku_selectors = [
            '.sku',
            '.product-code',
            '.item-code',
            '[class*="sku"]',
            '[class*="code"]'
        ]
        
        for selector in sku_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    return element.text.strip()
            except NoSuchElementException:
                continue
                
        # Look in page text
        page_text = self.driver.page_source
        sku_patterns = [
            r'SKU[:\s]*([A-Z0-9\-]+)',
            r'Product Code[:\s]*([A-Z0-9\-]+)',
            r'Item[:\s]*([A-Z0-9\-]+)',
            r'Code[:\s]*([A-Z0-9\-]+)'
        ]
        
        for pattern in sku_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        return "N/A"
        
    def extract_category(self) -> str:
        """Extract category from breadcrumb navigation"""
        breadcrumb_selectors = [
            '.breadcrumb',
            '.breadcrumbs',
            '.breadcrumb-nav',
            'nav[aria-label="breadcrumb"]'
        ]
        
        for selector in breadcrumb_selectors:
            try:
                breadcrumb = self.driver.find_element(By.CSS_SELECTOR, selector)
                if breadcrumb:
                    links = breadcrumb.find_elements(By.TAG_NAME, 'a')
                    if len(links) > 1:
                        return links[-2].text.strip()
            except NoSuchElementException:
                continue
                
        return "Uncategorized"
        
    def extract_prices(self) -> tuple:
        """Extract prices including and excluding VAT"""
        price_text = ""
        
        # Look for price elements
        price_selectors = [
            '.price',
            '.product-price',
            '.current-price',
            '.price-current',
            '[class*="price"]'
        ]
        
        for selector in price_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    price_text = element.text.strip()
                    break
            except NoSuchElementException:
                continue
                
        if not price_text:
            # Look for price patterns in page text
            page_text = self.driver.page_source
            price_match = re.search(r'R\s*[\d,]+\.?\d*', page_text)
            if price_match:
                price_text = price_match.group()
                
        return self.extract_price(price_text)
        
    def extract_stock_info(self) -> tuple:
        """Extract stock status and quantity - MicroRobotics usually shows exact numbers"""
        stock_text = ""
        stock_quantity = None
        
        # Look for stock information
        stock_selectors = [
            '.stock',
            '.availability',
            '.inventory',
            '.quantity',
            '[class*="stock"]',
            '[class*="availability"]'
        ]
        
        for selector in stock_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    stock_text = element.text.strip()
                    break
            except NoSuchElementException:
                continue
                
        if not stock_text:
            # Look for stock patterns in page text
            page_text = self.driver.page_source
            stock_patterns = [
                r'Stock[:\s]*(\d+)',
                r'Quantity[:\s]*(\d+)',
                r'Available[:\s]*(\d+)',
                r'(\d+)\s*in\s*stock',
                r'(\d+)\s*available'
            ]
            
            for pattern in stock_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    stock_text = match.group(0)
                    try:
                        stock_quantity = int(match.group(1))
                    except (ValueError, IndexError):
                        pass
                    break
                    
        # If we found a quantity but no text, create appropriate text
        if stock_quantity is not None and not stock_text:
            if stock_quantity > 0:
                stock_text = f"Stock: {stock_quantity}"
            else:
                stock_text = "Out of Stock"
                
        stock_status = self.determine_stock_status(stock_text, stock_quantity)
        return stock_status, stock_quantity
        
    def extract_brand(self) -> str:
        """Extract brand/manufacturer information"""
        brand_selectors = [
            '.brand',
            '.manufacturer',
            '.vendor',
            '[class*="brand"]',
            '[class*="manufacturer"]'
        ]
        
        for selector in brand_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    return element.text.strip()
            except NoSuchElementException:
                continue
                
        return "Unknown"
        
    def extract_description(self) -> str:
        """Extract product description"""
        desc_selectors = [
            '.product-description',
            '.description',
            '.product-details',
            '.product-info',
            '[class*="description"]'
        ]
        
        for selector in desc_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    return element.text.strip()[:500]  # Limit to 500 chars
            except NoSuchElementException:
                continue
                
        return "No description available"
        
    def get_products(self) -> list:
        """Main method to get all products from MicroRobotics"""
        all_products = []
        
        try:
            # Get categories
            categories = self.get_categories()
            
            if not categories:
                # If no categories found, try to scrape from main page
                self.logger.info("No categories found, trying to scrape from main page")
                categories = [self.base_url]
                
            # Scrape products from each category
            for category_url in categories:
                self.logger.info(f"Scraping category: {category_url}")
                try:
                    products = self.get_products_from_category(category_url)
                    all_products.extend(products)
                    self.logger.info(f"Found {len(products)} products in {category_url}")
                except Exception as e:
                    self.logger.error(f"Error scraping category {category_url}: {e}")
                    
        finally:
            # Always close the driver
            self.close_driver()
            
        return all_products