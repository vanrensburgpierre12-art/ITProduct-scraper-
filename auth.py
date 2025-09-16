"""
Authentication system for the electronics distributors API
"""

import secrets
import string
import time
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from database import db, User, DatabaseSession

jwt = JWTManager()

def generate_api_key():
    """Generate a secure API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(64))

def init_auth(app):
    """Initialize authentication with Flask app"""
    jwt.init_app(app)
    return jwt

def create_user(username, email, password):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return None, "Username already exists"
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return None, "Email already exists"
        
        # Create new user
        user = User(
            username=username,
            email=email,
            api_key=generate_api_key()
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    try:
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_active:
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        return None
    except Exception as e:
        current_app.logger.error(f"Error in authenticate_user: {str(e)}")
        db.session.rollback()
        return None

def authenticate_api_key(api_key):
    """Authenticate user with API key"""
    try:
        user = User.query.filter_by(api_key=api_key, is_active=True).first()
        if user:
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        return None
    except Exception as e:
        current_app.logger.error(f"Error in authenticate_api_key: {str(e)}")
        db.session.rollback()
        return None

def require_auth(f):
    """Decorator to require authentication via API key or JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key')
        if api_key:
            user = authenticate_api_key(api_key)
            if user:
                request.current_user = user
                return f(*args, **kwargs)
        
        # Check for JWT token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)
                if user and user.is_active:
                    request.current_user = user
                    return f(*args, **kwargs)
            except Exception:
                pass
        
        return jsonify({'error': 'Authentication required'}), 401
    
    return decorated_function

def require_admin(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user') or not request.current_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # For now, all users are admins. You can add an admin field to User model later
        return f(*args, **kwargs)
    
    return decorated_function

@jwt.user_identity_loader
def user_identity_lookup(user):
    """Tell Flask-JWT-Extended how to get user identity from user object"""
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Tell Flask-JWT-Extended how to get user from JWT data"""
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()

def rate_limit_exceeded_handler(e):
    """Handle rate limit exceeded"""
    return jsonify({'error': 'Rate limit exceeded'}), 429