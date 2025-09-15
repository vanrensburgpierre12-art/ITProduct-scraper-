"""
Configuration settings for the electronics distributors scraper and API
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/electronics_db')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'electronics_db')
DB_USER = os.getenv('DB_USER', 'username')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

# Flask Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

# API Configuration
API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '1000'))
DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', '50'))
MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', '1000'))

# Scraping Configuration
SCRAPING_INTERVAL_MINUTES = int(os.getenv('SCRAPING_INTERVAL_MINUTES', '25'))
SCRAPING_ENABLED = os.getenv('SCRAPING_ENABLED', 'true').lower() == 'true'

# WebSocket Configuration
WEBSOCKET_ENABLED = os.getenv('WEBSOCKET_ENABLED', 'true').lower() == 'true'

# Scraper settings
REQUEST_DELAY = (1, 3)  # Random delay between requests (min, max) in seconds
MAX_RETRIES = 3
TIMEOUT = 30

# Output files (for backup/export)
MAIN_CSV = os.path.join(OUTPUT_DIR, 'distributors_products.csv')
COMMUNICA_CSV = os.path.join(OUTPUT_DIR, 'communica.csv')
MICROROBOTICS_CSV = os.path.join(OUTPUT_DIR, 'microrobotics.csv')
MIRO_CSV = os.path.join(OUTPUT_DIR, 'miro.csv')

# Log files
MAIN_LOG = os.path.join(LOGS_DIR, f'scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
ERROR_LOG = os.path.join(LOGS_DIR, 'errors.log')

# User agents for requests
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

# Distributor URLs
DISTRIBUTORS = {
    'Communica': 'https://www.communica.co.za/',
    'MicroRobotics': 'https://www.robotics.org.za/',
    'Miro': 'https://miro.co.za/'
}