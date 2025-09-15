"""
Database initialization script for the electronics distributors API
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_app import create_app
from database import db, User, Product, StockHistory, ScrapingLog
from auth import create_user

def init_database():
    """Initialize the database with tables and default data"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("Creating default admin user...")
            admin_user, error = create_user('admin', 'admin@example.com', 'admin123')
            if admin_user:
                print(f"✅ Admin user created successfully")
                print(f"   Username: admin")
                print(f"   Password: admin123")
                print(f"   API Key: {admin_user.api_key}")
            else:
                print(f"❌ Failed to create admin user: {error}")
        else:
            print("✅ Admin user already exists")
            print(f"   Username: admin")
            print(f"   API Key: {admin_user.api_key}")
        
        # Create some sample data for testing (optional)
        if Product.query.count() == 0:
            print("No products found. You can start scraping to populate the database.")
        else:
            print(f"✅ Found {Product.query.count()} existing products in database")
        
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION COMPLETE")
        print("="*50)
        print("Next steps:")
        print("1. Start the API server: python api_app.py")
        print("2. Access the API at: http://localhost:7000")
        print("3. Use the admin credentials to authenticate")
        print("4. Start scraping to populate the database")

if __name__ == "__main__":
    init_database()