"""
Database configuration and models for the electronics distributors API
"""

import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    """User model for API authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Product(db.Model):
    """Product model for storing electronics distributor products"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(100), nullable=False, index=True)
    source = db.Column(db.String(50), nullable=False, index=True)  # Distributor name
    product_name = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(200))
    price_inc_vat = db.Column(db.Numeric(10, 2))
    price_ex_vat = db.Column(db.Numeric(10, 2))
    stock_status = db.Column(db.String(50), nullable=False, index=True)
    stock_quantity = db.Column(db.Integer)
    brand = db.Column(db.String(100))
    description = db.Column(db.Text)
    product_url = db.Column(db.String(1000))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # JSON field for additional metadata
    product_metadata = db.Column(JSONB)
    
    # Indexes for better query performance
    __table_args__ = (
        UniqueConstraint('sku', 'source', name='unique_sku_source'),
        Index('idx_sku_source', 'sku', 'source'),
        Index('idx_stock_status', 'stock_status'),
        Index('idx_last_updated', 'last_updated'),
        Index('idx_source_stock', 'source', 'stock_status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'source': self.source,
            'product_name': self.product_name,
            'category': self.category,
            'price_inc_vat': float(self.price_inc_vat) if self.price_inc_vat else None,
            'price_ex_vat': float(self.price_ex_vat) if self.price_ex_vat else None,
            'stock_status': self.stock_status,
            'stock_quantity': self.stock_quantity,
            'brand': self.brand,
            'description': self.description,
            'product_url': self.product_url,
            'last_updated': self.last_updated.isoformat(),
            'created_at': self.created_at.isoformat(),
            'metadata': self.product_metadata
        }

class StockHistory(db.Model):
    """Stock history model for tracking changes over time"""
    __tablename__ = 'stock_history'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    sku = db.Column(db.String(100), nullable=False, index=True)
    source = db.Column(db.String(50), nullable=False, index=True)
    price_inc_vat = db.Column(db.Numeric(10, 2))
    price_ex_vat = db.Column(db.Numeric(10, 2))
    stock_status = db.Column(db.String(50), nullable=False)
    stock_quantity = db.Column(db.Integer)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    product = db.relationship('Product', backref='stock_history')
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_product_recorded', 'product_id', 'recorded_at'),
        Index('idx_sku_recorded', 'sku', 'recorded_at'),
        Index('idx_source_recorded', 'source', 'recorded_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'sku': self.sku,
            'source': self.source,
            'price_inc_vat': float(self.price_inc_vat) if self.price_inc_vat else None,
            'price_ex_vat': float(self.price_ex_vat) if self.price_ex_vat else None,
            'stock_status': self.stock_status,
            'stock_quantity': self.stock_quantity,
            'recorded_at': self.recorded_at.isoformat()
        }

class ScrapingLog(db.Model):
    """Log model for tracking scraping runs"""
    __tablename__ = 'scraping_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    distributor = db.Column(db.String(50), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)  # 'started', 'completed', 'failed'
    products_found = db.Column(db.Integer, default=0)
    products_updated = db.Column(db.Integer, default=0)
    products_new = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'distributor': self.distributor,
            'status': self.status,
            'products_found': self.products_found,
            'products_updated': self.products_updated,
            'products_new': self.products_new,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds
        }

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate = Migrate(app, db)
    return migrate