"""
Communica scraper for https://www.communica.co.za/
"""

import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from base_scraper import BaseScraper


class CommunicaScraper(BaseScraper):
    """Scraper for Communica electronics distributor"""
    
    def __init__(self):
        super().__init__("Communica", "https://www.communica.co.za/")
        
    def get_categories(self) -> list:
        """Get all product categories from the main page"""
        categories = []
        try:
            response = self.make_request(self.base_url)
            if not response:
                return categories
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for category links in navigation
            category_links = soup.find_all('a', href=True)
            for link in category_links:
                href = link.get('href', '')
                if '/category/' in href or '/products/' in href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in categories:
                        categories.append(full_url)
                        
            self.logger.info(f"Found {len(categories)} categories")
            return categories
            
        except Exception as e:
            self.logger.error(f"Error getting categories: {e}")
            return categories
            
    def get_products_from_category(self, category_url: str) -> list:
        """Get all products from a specific category"""
        products = []
        page = 1
        
        while True:
            try:
                # Try pagination
                if page > 1:
                    if '?' in category_url:
                        page_url = f"{category_url}&page={page}"
                    else:
                        page_url = f"{category_url}?page={page}"
                else:
                    page_url = category_url
                    
                response = self.make_request(page_url)
                if not response:
                    break
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find product links on the page
                product_links = self.find_product_links(soup)
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
                
                # Safety check to prevent infinite loops
                if page > 50:
                    self.logger.warning(f"Reached page limit for {category_url}")
                    break
                    
            except Exception as e:
                self.logger.error(f"Error processing page {page} of {category_url}: {e}")
                break
                
        return products
        
    def find_product_links(self, soup: BeautifulSoup) -> list:
        """Find all product links on a category page"""
        product_links = []
        
        # Look for common product link patterns
        selectors = [
            'a[href*="/product/"]',
            'a[href*="/item/"]',
            '.product-item a',
            '.product-link',
            '.product-title a',
            'h3 a',
            'h4 a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in product_links:
                        product_links.append(full_url)
                        
        return product_links
        
    def extract_product_details(self, product_url: str) -> dict:
        """Extract detailed product information from product page"""
        try:
            response = self.make_request(product_url)
            if not response:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product name
            product_name = self.extract_product_name(soup)
            
            # Extract SKU
            sku = self.extract_sku(soup)
            
            # Extract category from breadcrumb
            category = self.extract_category(soup)
            
            # Extract prices
            price_inc_vat, price_ex_vat = self.extract_prices(soup)
            
            # Extract stock information
            stock_status, stock_quantity = self.extract_stock_info(soup)
            
            # Extract brand
            brand = self.extract_brand(soup)
            
            # Extract description
            description = self.extract_description(soup)
            
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
            
    def extract_product_name(self, soup: BeautifulSoup) -> str:
        """Extract product name from product page"""
        selectors = [
            'h1.product-title',
            'h1',
            '.product-name',
            '.product-title',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return "Unknown Product"
        
    def extract_sku(self, soup: BeautifulSoup) -> str:
        """Extract SKU/Product Code"""
        # Look for SKU in various places
        sku_patterns = [
            r'SKU[:\s]*([A-Z0-9\-]+)',
            r'Product Code[:\s]*([A-Z0-9\-]+)',
            r'Item[:\s]*([A-Z0-9\-]+)',
            r'Code[:\s]*([A-Z0-9\-]+)'
        ]
        
        text = soup.get_text()
        for pattern in sku_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        # Try to find in meta tags or data attributes
        meta_sku = soup.find('meta', {'name': 'sku'}) or soup.find('meta', {'name': 'product-code'})
        if meta_sku and meta_sku.get('content'):
            return meta_sku.get('content').strip()
            
        return "N/A"
        
    def extract_category(self, soup: BeautifulSoup) -> str:
        """Extract category from breadcrumb navigation"""
        breadcrumb_selectors = [
            '.breadcrumb',
            '.breadcrumbs',
            '.breadcrumb-nav',
            'nav[aria-label="breadcrumb"]'
        ]
        
        for selector in breadcrumb_selectors:
            breadcrumb = soup.select_one(selector)
            if breadcrumb:
                links = breadcrumb.find_all('a')
                if len(links) > 1:
                    # Return the second to last link (usually the category)
                    return links[-2].get_text().strip()
                    
        return "Uncategorized"
        
    def extract_prices(self, soup: BeautifulSoup) -> tuple:
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
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text().strip()
                break
                
        if not price_text:
            # Try to find any text that looks like a price
            text = soup.get_text()
            price_match = re.search(r'R\s*[\d,]+\.?\d*', text)
            if price_match:
                price_text = price_match.group()
                
        return self.extract_price(price_text)
        
    def extract_stock_info(self, soup: BeautifulSoup) -> tuple:
        """Extract stock status and quantity"""
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
            element = soup.select_one(selector)
            if element:
                stock_text = element.get_text().strip()
                break
                
        if not stock_text:
            # Look for common stock phrases in the text
            text = soup.get_text()
            stock_patterns = [
                r'(In Stock|Out of Stock|Notify Me|Only \d+ left)',
                r'(Available|Unavailable|Backorder)',
                r'Stock[:\s]*(\d+)',
                r'Quantity[:\s]*(\d+)'
            ]
            
            for pattern in stock_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    stock_text = match.group(1) if match.groups() else match.group()
                    break
                    
        # Extract quantity if mentioned
        if stock_text:
            quantity_match = re.search(r'(\d+)', stock_text)
            if quantity_match:
                try:
                    stock_quantity = int(quantity_match.group(1))
                except ValueError:
                    pass
                    
        stock_status = self.determine_stock_status(stock_text, stock_quantity)
        return stock_status, stock_quantity
        
    def extract_brand(self, soup: BeautifulSoup) -> str:
        """Extract brand/manufacturer information"""
        brand_selectors = [
            '.brand',
            '.manufacturer',
            '.vendor',
            '[class*="brand"]',
            '[class*="manufacturer"]'
        ]
        
        for selector in brand_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
                
        # Try to find in meta tags
        meta_brand = soup.find('meta', {'name': 'brand'}) or soup.find('meta', {'name': 'manufacturer'})
        if meta_brand and meta_brand.get('content'):
            return meta_brand.get('content').strip()
            
        return "Unknown"
        
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description"""
        desc_selectors = [
            '.product-description',
            '.description',
            '.product-details',
            '.product-info',
            '[class*="description"]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()[:500]  # Limit to 500 chars
                
        return "No description available"
        
    def get_products(self) -> list:
        """Main method to get all products from Communica"""
        all_products = []
        
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
                
        return all_products