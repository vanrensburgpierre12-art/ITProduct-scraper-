"""
Configuration settings for the electronics distributors scraper
"""

import os
from datetime import datetime

# Base configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Scraper settings
REQUEST_DELAY = (1, 3)  # Random delay between requests (min, max) in seconds
MAX_RETRIES = 3
TIMEOUT = 30

# Output files
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