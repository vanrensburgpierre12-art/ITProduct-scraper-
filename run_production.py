#!/usr/bin/env python3
"""
Production startup script for the electronics distributors API
This script uses Gunicorn for production deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import psycopg2
        import sqlalchemy
        import flask
        import flask_socketio
        import apscheduler
        import gunicorn
        import eventlet
        print("✅ All Python requirements are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_postgresql():
    """Check if PostgreSQL is running and accessible"""
    try:
        from config import DATABASE_URL
        from sqlalchemy import create_engine
        
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        connection.close()
        print("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("Please ensure PostgreSQL is running and the database exists")
        return False

def main():
    """Main startup function"""
    print("🚀 Starting Electronics Distributors API (Production Mode)")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check PostgreSQL
    if not check_postgresql():
        sys.exit(1)
    
    # Initialize database
    print("\n📊 Initializing database...")
    try:
        from init_db import init_database
        init_database()
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Start the API server with Gunicorn
    print("\n🌐 Starting API server with Gunicorn...")
    print("✅ API server starting on http://localhost:7000")
    print("📡 WebSocket support enabled")
    print("⏰ Scheduled scraping enabled (every 25 minutes)")
    print("🔧 Production server: Gunicorn with Eventlet workers")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Gunicorn command with proper configuration for WebSockets
        cmd = [
            "gunicorn",
            "--bind", "0.0.0.0:7000",
            "--workers", "4",
            "--worker-class", "eventlet",
            "--worker-connections", "1000",
            "--timeout", "120",
            "--keep-alive", "2",
            "--max-requests", "1000",
            "--max-requests-jitter", "100",
            "--preload",
            "--access-logfile", "-",
            "--error-logfile", "-",
            "api_app:app"
        ]
        
        # Run Gunicorn
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()