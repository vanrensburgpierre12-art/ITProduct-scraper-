#!/usr/bin/env python3
"""
Test script for the electronics distributors API
"""

import requests
import json
import time
import sys
from datetime import datetime

API_BASE_URL = "http://localhost:7000"

def test_api_connection():
    """Test basic API connection"""
    print("🔌 Testing API connection...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/auth/me", timeout=5)
        if response.status_code == 401:
            print("✅ API is running (authentication required)")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_authentication():
    """Test authentication endpoints"""
    print("\n🔐 Testing authentication...")
    
    # Test login
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            api_key = data.get('api_key')
            print("✅ Login successful")
            return api_key
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_products_endpoints(api_key):
    """Test products endpoints"""
    print("\n📦 Testing products endpoints...")
    
    headers = {"X-API-Key": api_key}
    
    # Test get products
    try:
        response = requests.get(f"{API_BASE_URL}/api/products", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get products successful - {data['pagination']['total']} total products")
        else:
            print(f"❌ Get products failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get products error: {e}")
    
    # Test search products
    try:
        response = requests.get(f"{API_BASE_URL}/api/products/search?q=arduino", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search products successful - {data['pagination']['total']} results for 'arduino'")
        else:
            print(f"❌ Search products failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search products error: {e}")

def test_distributors_endpoints(api_key):
    """Test distributors endpoints"""
    print("\n🏪 Testing distributors endpoints...")
    
    headers = {"X-API-Key": api_key}
    
    # Test get distributors
    try:
        response = requests.get(f"{API_BASE_URL}/api/distributors", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get distributors successful - {len(data['distributors'])} distributors")
            for dist in data['distributors']:
                print(f"   - {dist['name']}: {dist['product_count']} products")
        else:
            print(f"❌ Get distributors failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get distributors error: {e}")

def test_statistics_endpoints(api_key):
    """Test statistics endpoints"""
    print("\n📊 Testing statistics endpoints...")
    
    headers = {"X-API-Key": api_key}
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Get statistics successful")
            print(f"   - Total products: {data['total_products']}")
            print(f"   - Recent updates (24h): {data['recent_updates_24h']}")
            print(f"   - Price range: R{data['price_range']['min']:.2f} - R{data['price_range']['max']:.2f}")
        else:
            print(f"❌ Get statistics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get statistics error: {e}")

def test_scraping_endpoints(api_key):
    """Test scraping endpoints"""
    print("\n🔄 Testing scraping endpoints...")
    
    headers = {"X-API-Key": api_key}
    
    # Test get scraping status
    try:
        response = requests.get(f"{API_BASE_URL}/api/scraping/status", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Get scraping status successful")
            print(f"   - Running: {data['is_running']}")
            print(f"   - Progress: {data['progress']}%")
        else:
            print(f"❌ Get scraping status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get scraping status error: {e}")
    
    # Test get scraping logs
    try:
        response = requests.get(f"{API_BASE_URL}/api/scraping/logs", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get scraping logs successful - {data['pagination']['total']} logs")
        else:
            print(f"❌ Get scraping logs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get scraping logs error: {e}")

def test_websocket_connection():
    """Test WebSocket connection"""
    print("\n🔌 Testing WebSocket connection...")
    
    try:
        import socketio
        
        sio = socketio.Client()
        
        @sio.event
        def connect():
            print("✅ WebSocket connected successfully")
            sio.emit('join_room', {'room': 'scraping'})
            sio.disconnect()
        
        @sio.event
        def disconnect():
            print("✅ WebSocket disconnected successfully")
        
        sio.connect(API_BASE_URL)
        time.sleep(1)  # Give time for connection
        
    except ImportError:
        print("⚠️  socketio-client not installed, skipping WebSocket test")
        print("   Install with: pip install python-socketio[client]")
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")

def main():
    """Main test function"""
    print("🧪 Electronics Distributors API Test Suite")
    print("=" * 50)
    
    # Test API connection
    if not test_api_connection():
        print("\n❌ API connection failed. Please start the API server first:")
        print("   python start_api.py")
        sys.exit(1)
    
    # Test authentication
    api_key = test_authentication()
    if not api_key:
        print("\n❌ Authentication failed. Please check admin credentials.")
        sys.exit(1)
    
    # Test all endpoints
    test_products_endpoints(api_key)
    test_distributors_endpoints(api_key)
    test_statistics_endpoints(api_key)
    test_scraping_endpoints(api_key)
    test_websocket_connection()
    
    print("\n" + "=" * 50)
    print("✅ API test suite completed!")
    print(f"📝 API Key for manual testing: {api_key}")
    print("📖 Full documentation: API_DOCUMENTATION.md")

if __name__ == "__main__":
    main()