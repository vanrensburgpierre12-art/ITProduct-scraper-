"""
Main Flask API application for the electronics distributors realtime database
"""

import os
import json
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import joinedload
from sqlalchemy.pool import QueuePool
import pandas as pd

from database import db, Product, StockHistory, ScrapingLog, User
from auth import init_auth, require_auth, require_admin, create_user, authenticate_user, create_access_token
from config import *
from communica_scraper import CommunicaScraper
from microrobotics_scraper import MicroRoboticsScraper
from miro_scraper import MiroScraper

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': QueuePool,
    'pool_size': 5,  # Reduced pool size to avoid threading issues
    'max_overflow': 10,  # Reduced max overflow
    'pool_pre_ping': True,
    'pool_recycle': 1800,  # 30 minutes
    'pool_timeout': 20,  # Reduced timeout
    'echo': False,
    'connect_args': {
        'connect_timeout': 10,
        'application_name': 'electronics_api'
    }
}

# Initialize extensions
CORS(app)
db.init_app(app)
jwt = init_auth(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Add request teardown handler for proper session cleanup
@app.teardown_appcontext
def close_db(error):
    """Close database connection on request teardown"""
    if error:
        db.session.rollback()
    else:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Database error during teardown: {str(e)}")

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

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    user, error = create_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict(),
        'api_key': user.api_key
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = authenticate_user(data['username'], data['password'])
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user)
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict(),
        'api_key': user.api_key
    })

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information"""
    return jsonify(request.current_user.to_dict())

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@app.route('/api/products', methods=['GET'])
@require_auth
def get_products():
    """Get all products with pagination and filtering"""
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
    
    # Filters
    source = request.args.get('source')
    stock_status = request.args.get('stock_status')
    category = request.args.get('category')
    brand = request.args.get('brand')
    search = request.args.get('search')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Build query
    query = Product.query
    
    if source:
        query = query.filter(Product.source == source)
    if stock_status:
        query = query.filter(Product.stock_status == stock_status)
    if category:
        query = query.filter(Product.category.ilike(f'%{category}%'))
    if brand:
        query = query.filter(Product.brand.ilike(f'%{brand}%'))
    if search:
        query = query.filter(
            or_(
                Product.product_name.ilike(f'%{search}%'),
                Product.sku.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )
    if min_price is not None:
        query = query.filter(Product.price_inc_vat >= min_price)
    if max_price is not None:
        query = query.filter(Product.price_inc_vat <= max_price)
    
    # Order by last updated
    query = query.order_by(desc(Product.last_updated))
    
    # Paginate
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'products': [product.to_dict() for product in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@app.route('/api/products/<sku>', methods=['GET'])
@require_auth
def get_product_by_sku(sku):
    """Get specific product by SKU"""
    source = request.args.get('source')
    
    if source:
        product = Product.query.filter_by(sku=sku, source=source).first()
    else:
        # Return all products with this SKU from all sources
        products = Product.query.filter_by(sku=sku).all()
        return jsonify({
            'products': [product.to_dict() for product in products],
            'total': len(products)
        })
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify(product.to_dict())

@app.route('/api/products/search', methods=['GET'])
@require_auth
def search_products():
    """Search products with advanced filtering"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
    
    # Search in multiple fields
    search_filter = or_(
        Product.product_name.ilike(f'%{query}%'),
        Product.sku.ilike(f'%{query}%'),
        Product.description.ilike(f'%{query}%'),
        Product.brand.ilike(f'%{query}%'),
        Product.category.ilike(f'%{query}%')
    )
    
    products = Product.query.filter(search_filter).order_by(desc(Product.last_updated))
    
    # Paginate
    pagination = products.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'products': [product.to_dict() for product in pagination.items],
        'query': query,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

# ============================================================================
# STOCK ENDPOINTS
# ============================================================================

@app.route('/api/stock/<sku>', methods=['GET'])
@require_auth
def get_stock_info(sku):
    """Get current stock information for a product"""
    source = request.args.get('source')
    
    if source:
        product = Product.query.filter_by(sku=sku, source=source).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'sku': product.sku,
            'source': product.source,
            'stock_status': product.stock_status,
            'stock_quantity': product.stock_quantity,
            'last_updated': product.last_updated.isoformat()
        })
    else:
        # Return stock info from all sources
        products = Product.query.filter_by(sku=sku).all()
        if not products:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'sku': sku,
            'sources': [{
                'source': product.source,
                'stock_status': product.stock_status,
                'stock_quantity': product.stock_quantity,
                'last_updated': product.last_updated.isoformat()
            } for product in products]
        })

@app.route('/api/stock/history/<sku>', methods=['GET'])
@require_auth
def get_stock_history(sku):
    """Get stock history for a product"""
    source = request.args.get('source')
    days = int(request.args.get('days', 30))
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = StockHistory.query.filter(
        and_(
            StockHistory.sku == sku,
            StockHistory.recorded_at >= start_date
        )
    )
    
    if source:
        query = query.filter(StockHistory.source == source)
    
    history = query.order_by(desc(StockHistory.recorded_at)).all()
    
    return jsonify({
        'sku': sku,
        'source': source,
        'history': [record.to_dict() for record in history],
        'total_records': len(history)
    })

# ============================================================================
# DISTRIBUTOR ENDPOINTS
# ============================================================================

@app.route('/api/distributors', methods=['GET'])
@require_auth
def get_distributors():
    """Get list of available distributors"""
    distributors = db.session.query(
        Product.source,
        func.count(Product.id).label('product_count'),
        func.max(Product.last_updated).label('last_updated')
    ).group_by(Product.source).all()
    
    return jsonify({
        'distributors': [{
            'name': dist.source,
            'product_count': dist.product_count,
            'last_updated': dist.last_updated.isoformat() if dist.last_updated else None
        } for dist in distributors]
    })

@app.route('/api/distributors/<distributor_name>/products', methods=['GET'])
@require_auth
def get_distributor_products(distributor_name):
    """Get products from a specific distributor"""
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
    
    query = Product.query.filter_by(source=distributor_name)
    
    # Apply filters
    stock_status = request.args.get('stock_status')
    category = request.args.get('category')
    brand = request.args.get('brand')
    
    if stock_status:
        query = query.filter(Product.stock_status == stock_status)
    if category:
        query = query.filter(Product.category.ilike(f'%{category}%'))
    if brand:
        query = query.filter(Product.brand.ilike(f'%{brand}%'))
    
    query = query.order_by(desc(Product.last_updated))
    
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'distributor': distributor_name,
        'products': [product.to_dict() for product in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@app.route('/api/stats', methods=['GET'])
@require_auth
def get_statistics():
    """Get overall statistics"""
    total_products = Product.query.count()
    
    # Products by distributor
    by_distributor = db.session.query(
        Product.source,
        func.count(Product.id).label('count')
    ).group_by(Product.source).all()
    
    # Products by stock status
    by_stock_status = db.session.query(
        Product.stock_status,
        func.count(Product.id).label('count')
    ).group_by(Product.stock_status).all()
    
    # Price statistics
    price_stats = db.session.query(
        func.min(Product.price_inc_vat).label('min_price'),
        func.max(Product.price_inc_vat).label('max_price'),
        func.avg(Product.price_inc_vat).label('avg_price')
    ).filter(Product.price_inc_vat.isnot(None)).first()
    
    # Recent updates
    recent_updates = db.session.query(
        func.count(Product.id).label('count')
    ).filter(
        Product.last_updated >= datetime.utcnow() - timedelta(hours=24)
    ).first()
    
    return jsonify({
        'total_products': total_products,
        'by_distributor': {dist.source: dist.count for dist in by_distributor},
        'by_stock_status': {status.stock_status: status.count for status in by_stock_status},
        'price_range': {
            'min': float(price_stats.min_price) if price_stats.min_price else 0,
            'max': float(price_stats.max_price) if price_stats.max_price else 0,
            'avg': float(price_stats.avg_price) if price_stats.avg_price else 0
        },
        'recent_updates_24h': recent_updates.count if recent_updates else 0
    })

# ============================================================================
# SCRAPING ENDPOINTS
# ============================================================================

@app.route('/api/scraping/status', methods=['GET'])
@require_auth
def get_scraping_status():
    """Get current scraping status"""
    return jsonify(scraping_status)

@app.route('/api/scraping/start', methods=['POST'])
@require_auth
@require_admin
def start_scraping():
    """Start manual scraping"""
    global scraping_status
    
    if scraping_status['is_running']:
        return jsonify({'error': 'Scraping is already running'}), 400
    
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
    
    # Start scraping in a separate thread
    thread = threading.Thread(target=run_scraping, args=(selected_distributors,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Scraping started'})

@app.route('/api/scraping/logs', methods=['GET'])
@require_auth
def get_scraping_logs():
    """Get scraping logs"""
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 100)
    
    logs = ScrapingLog.query.order_by(desc(ScrapingLog.started_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': logs.total,
            'pages': logs.pages,
            'has_next': logs.has_next,
            'has_prev': logs.has_prev
        }
    })

# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@app.route('/api/export/csv', methods=['GET'])
@require_auth
def export_csv():
    """Export products to CSV"""
    source = request.args.get('source')
    
    query = Product.query
    if source:
        query = query.filter_by(source=source)
    
    products = query.all()
    
    if not products:
        return jsonify({'error': 'No products to export'}), 400
    
    # Create DataFrame
    df = pd.DataFrame([product.to_dict() for product in products])
    csv_path = os.path.join(OUTPUT_DIR, f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    df.to_csv(csv_path, index=False)
    
    return send_file(csv_path, as_attachment=True, download_name='products_export.csv')

@app.route('/api/export/json', methods=['GET'])
@require_auth
def export_json():
    """Export products to JSON"""
    source = request.args.get('source')
    
    query = Product.query
    if source:
        query = query.filter_by(source=source)
    
    products = query.all()
    
    if not products:
        return jsonify({'error': 'No products to export'}), 400
    
    json_path = os.path.join(OUTPUT_DIR, f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump([product.to_dict() for product in products], f, indent=2, ensure_ascii=False)
    
    return send_file(json_path, as_attachment=True, download_name='products_export.json')

# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to real-time updates'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('join_room')
def handle_join_room(data):
    """Join a room for specific updates"""
    room = data.get('room', 'general')
    join_room(room)
    emit('joined_room', {'room': room})

@socketio.on('leave_room')
def handle_leave_room(data):
    """Leave a room"""
    room = data.get('room', 'general')
    leave_room(room)
    emit('left_room', {'room': room})

# ============================================================================
# SCRAPING FUNCTIONS
# ============================================================================

def run_scraping(distributors):
    """Run the scraping process"""
    global scraping_status
    
    try:
        scrapers = {
            'Communica': CommunicaScraper,
            'MicroRobotics': MicroRoboticsScraper,
            'Miro': MiroScraper
        }
        
        total_distributors = len(distributors)
        total_products = 0
        total_updated = 0
        total_new = 0
        
        for i, distributor_name in enumerate(distributors):
            if distributor_name not in scrapers:
                continue
            
            # Create scraping log
            log = ScrapingLog(
                distributor=distributor_name,
                status='started'
            )
            db.session.add(log)
            db.session.commit()
            
            scraping_status['current_distributor'] = distributor_name
            scraping_status['progress'] = int((i / total_distributors) * 100)
            
            # Emit progress update
            socketio.emit('scraping_progress', scraping_status, room='scraping')
            
            try:
                scraper = scrapers[distributor_name]()
                products = scraper.run()
                
                # Update database
                updated, new = update_products_in_db(products, distributor_name)
                total_updated += updated
                total_new += new
                total_products += len(products)
                
                scraping_status['completed_products'] = total_products
                scraping_status['total_products'] = total_products
                
                # Update log
                log.status = 'completed'
                log.products_found = len(products)
                log.products_updated = updated
                log.products_new = new
                log.completed_at = datetime.utcnow()
                log.duration_seconds = int((log.completed_at - log.started_at).total_seconds())
                db.session.commit()
                
                # Emit completion update
                socketio.emit('distributor_completed', {
                    'distributor': distributor_name,
                    'products_found': len(products),
                    'products_updated': updated,
                    'products_new': new
                }, room='scraping')
                
            except Exception as e:
                scraping_status['error'] = f"Error scraping {distributor_name}: {str(e)}"
                
                # Update log
                log.status = 'failed'
                log.error_message = str(e)
                log.completed_at = datetime.utcnow()
                log.duration_seconds = int((log.completed_at - log.started_at).total_seconds())
                db.session.commit()
                
                # Emit error update
                socketio.emit('scraping_error', {
                    'distributor': distributor_name,
                    'error': str(e)
                }, room='scraping')
                
                continue
        
        scraping_status['progress'] = 100
        scraping_status['end_time'] = datetime.now().isoformat()
        
        # Emit final completion
        socketio.emit('scraping_completed', {
            'total_products': total_products,
            'total_updated': total_updated,
            'total_new': total_new
        }, room='scraping')
        
    except Exception as e:
        scraping_status['error'] = f"Scraping failed: {str(e)}"
        socketio.emit('scraping_error', {'error': str(e)}, room='scraping')
    
    finally:
        scraping_status['is_running'] = False

def update_products_in_db(products, distributor_name):
    """Update products in database and track changes"""
    updated = 0
    new = 0
    
    for product_data in products:
        # Check if product exists
        existing_product = Product.query.filter_by(
            sku=product_data['SKU'],
            source=distributor_name
        ).first()
        
        if existing_product:
            # Check if there are changes
            changes = False
            old_stock_status = existing_product.stock_status
            old_stock_quantity = existing_product.stock_quantity
            old_price_inc_vat = existing_product.price_inc_vat
            
            # Update fields
            if existing_product.product_name != product_data['Product Name']:
                existing_product.product_name = product_data['Product Name']
                changes = True
            
            if existing_product.price_inc_vat != product_data['Price (Inc VAT)']:
                existing_product.price_inc_vat = product_data['Price (Inc VAT)']
                changes = True
            
            if existing_product.price_ex_vat != product_data['Price (Ex VAT)']:
                existing_product.price_ex_vat = product_data['Price (Ex VAT)']
                changes = True
            
            if existing_product.stock_status != product_data['Stock Status']:
                existing_product.stock_status = product_data['Stock Status']
                changes = True
            
            if existing_product.stock_quantity != product_data['Stock Quantity']:
                existing_product.stock_quantity = product_data['Stock Quantity']
                changes = True
            
            if changes:
                existing_product.last_updated = datetime.utcnow()
                
                # Create stock history record
                history = StockHistory(
                    product_id=existing_product.id,
                    sku=existing_product.sku,
                    source=existing_product.source,
                    price_inc_vat=existing_product.price_inc_vat,
                    price_ex_vat=existing_product.price_ex_vat,
                    stock_status=existing_product.stock_status,
                    stock_quantity=existing_product.stock_quantity
                )
                db.session.add(history)
                updated += 1
        else:
            # Create new product
            new_product = Product(
                sku=product_data['SKU'],
                source=distributor_name,
                product_name=product_data['Product Name'],
                category=product_data.get('Category'),
                price_inc_vat=product_data['Price (Inc VAT)'],
                price_ex_vat=product_data['Price (Ex VAT)'],
                stock_status=product_data['Stock Status'],
                stock_quantity=product_data['Stock Quantity'],
                brand=product_data.get('Brand'),
                description=product_data.get('Description'),
                product_url=product_data.get('Product URL'),
                last_updated=datetime.utcnow()
            )
            db.session.add(new_product)
            db.session.flush()  # Get the ID
            
            # Create initial stock history record
            history = StockHistory(
                product_id=new_product.id,
                sku=new_product.sku,
                source=new_product.source,
                price_inc_vat=new_product.price_inc_vat,
                price_ex_vat=new_product.price_ex_vat,
                stock_status=new_product.stock_status,
                stock_quantity=new_product.stock_quantity
            )
            db.session.add(history)
            new += 1
    
    db.session.commit()
    return updated, new

# ============================================================================
# SCHEDULER SETUP
# ============================================================================

def setup_scheduler():
    """Setup the scheduled scraping"""
    if not SCRAPING_ENABLED:
        return None
    
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    
    scheduler = BackgroundScheduler()
    
    # Add scraping job
    scheduler.add_job(
        func=run_scheduled_scraping,
        trigger=IntervalTrigger(minutes=SCRAPING_INTERVAL_MINUTES),
        id='scraping_job',
        name='Scheduled scraping',
        replace_existing=True
    )
    
    scheduler.start()
    return scheduler

def run_scheduled_scraping():
    """Run scheduled scraping"""
    global scraping_status
    
    if scraping_status['is_running']:
        print("Scraping already running, skipping scheduled run")
        return
    
    print(f"Starting scheduled scraping at {datetime.now()}")
    run_scraping(['Communica', 'MicroRobotics', 'Miro'])

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

def create_app():
    """Create and configure the Flask application"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin_user, error = create_user('admin', 'admin@example.com', 'admin123')
            if admin_user:
                print(f"Created default admin user with API key: {admin_user.api_key}")
        
        # Setup scheduler
        scheduler = setup_scheduler()
        if scheduler:
            print(f"Scheduled scraping enabled - running every {SCRAPING_INTERVAL_MINUTES} minutes")
    
    return app

if __name__ == '__main__':
    app = create_app()
    # For development only - use start_api.py for production
    socketio.run(app, debug=True, host='0.0.0.0', port=7000, allow_unsafe_werkzeug=True)