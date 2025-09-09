"""
Flask web application for the electronics distributors scraper
"""

import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd

from communica_scraper import CommunicaScraper
from microrobotics_scraper import MicroRoboticsScraper
from miro_scraper import MiroScraper
from config import *

app = Flask(__name__)
CORS(app)

# Global variables for tracking scraping progress
scraping_status = {
    'is_running': False,
    'progress': 0,
    'current_distributor': '',
    'total_products': 0,
    'completed_products': 0,
    'start_time': None,
    'end_time': None,
    'error': None
}

all_products = []

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/start_scraping', methods=['POST'])
def start_scraping():
    """Start the scraping process"""
    global scraping_status, all_products
    
    if scraping_status['is_running']:
        return jsonify({'error': 'Scraping is already running'}), 400
    
    # Get selected distributors from request
    data = request.get_json() or {}
    selected_distributors = data.get('distributors', ['Communica', 'MicroRobotics', 'Miro'])
    
    # Reset status
    scraping_status.update({
        'is_running': True,
        'progress': 0,
        'current_distributor': '',
        'total_products': 0,
        'completed_products': 0,
        'start_time': datetime.now().isoformat(),
        'end_time': None,
        'error': None
    })
    all_products = []
    
    # Start scraping in a separate thread
    thread = threading.Thread(target=run_scraping, args=(selected_distributors,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Scraping started'})

@app.route('/api/status')
def get_status():
    """Get current scraping status"""
    return jsonify(scraping_status)

@app.route('/api/products')
def get_products():
    """Get scraped products"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    products_page = all_products[start_idx:end_idx]
    
    return jsonify({
        'products': products_page,
        'total': len(all_products),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(all_products) + per_page - 1) // per_page
    })

@app.route('/api/download_csv')
def download_csv():
    """Download the CSV file"""
    if not all_products:
        return jsonify({'error': 'No products to download'}), 400
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(all_products)
    csv_path = os.path.join(OUTPUT_DIR, 'distributors_products.csv')
    df.to_csv(csv_path, index=False)
    
    return send_file(csv_path, as_attachment=True, download_name='distributors_products.csv')

@app.route('/api/download_json')
def download_json():
    """Download the JSON file"""
    if not all_products:
        return jsonify({'error': 'No products to download'}), 400
    
    json_path = os.path.join(OUTPUT_DIR, 'distributors_products.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    
    return send_file(json_path, as_attachment=True, download_name='distributors_products.json')

@app.route('/api/stats')
def get_stats():
    """Get statistics about scraped products"""
    if not all_products:
        return jsonify({'error': 'No products available'})
    
    df = pd.DataFrame(all_products)
    
    stats = {
        'total_products': len(all_products),
        'by_distributor': df['Source'].value_counts().to_dict(),
        'by_stock_status': df['Stock Status'].value_counts().to_dict(),
        'price_range': {
            'min': df['Price (Inc VAT)'].min() if 'Price (Inc VAT)' in df.columns else 0,
            'max': df['Price (Inc VAT)'].max() if 'Price (Inc VAT)' in df.columns else 0,
            'avg': df['Price (Inc VAT)'].mean() if 'Price (Inc VAT)' in df.columns else 0
        }
    }
    
    return jsonify(stats)

def run_scraping(distributors):
    """Run the scraping process"""
    global scraping_status, all_products
    
    try:
        scrapers = {
            'Communica': CommunicaScraper,
            'MicroRobotics': MicroRoboticsScraper,
            'Miro': MiroScraper
        }
        
        total_distributors = len(distributors)
        
        for i, distributor_name in enumerate(distributors):
            if distributor_name not in scrapers:
                continue
                
            scraping_status['current_distributor'] = distributor_name
            scraping_status['progress'] = int((i / total_distributors) * 100)
            
            try:
                scraper = scrapers[distributor_name]()
                products = scraper.run()
                all_products.extend(products)
                
                scraping_status['completed_products'] = len(all_products)
                scraping_status['total_products'] = len(all_products)
                
            except Exception as e:
                scraping_status['error'] = f"Error scraping {distributor_name}: {str(e)}"
                continue
        
        scraping_status['progress'] = 100
        scraping_status['end_time'] = datetime.now().isoformat()
        
    except Exception as e:
        scraping_status['error'] = f"Scraping failed: {str(e)}"
    
    finally:
        scraping_status['is_running'] = False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)