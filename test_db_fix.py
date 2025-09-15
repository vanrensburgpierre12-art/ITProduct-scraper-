#!/usr/bin/env python3
"""
Test script to verify the database connection fix
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:7000/api/health', timeout=10)
        print(f"Health check status: {response.status_code}")
        print(f"Health check response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_login_endpoint():
    """Test the login endpoint that was failing"""
    try:
        # Test with invalid credentials first
        response = requests.post('http://localhost:7000/api/auth/login', 
                               json={'username': 'test', 'password': 'wrong'}, 
                               timeout=10)
        print(f"Login with invalid credentials: {response.status_code}")
        
        # Test with valid credentials (if admin user exists)
        response = requests.post('http://localhost:7000/api/auth/login', 
                               json={'username': 'admin', 'password': 'admin123'}, 
                               timeout=10)
        print(f"Login with valid credentials: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Login successful, got token: {data.get('access_token', 'No token')[:20]}...")
            return True
        else:
            print(f"Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"Login test failed: {e}")
        return False

def test_multiple_requests():
    """Test multiple concurrent requests to check for threading issues"""
    import threading
    import queue
    
    results = queue.Queue()
    
    def make_request():
        try:
            response = requests.get('http://localhost:7000/api/health', timeout=5)
            results.put(('success', response.status_code))
        except Exception as e:
            results.put(('error', str(e)))
    
    # Start multiple threads
    threads = []
    for i in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Collect results
    success_count = 0
    error_count = 0
    
    while not results.empty():
        result_type, data = results.get()
        if result_type == 'success':
            success_count += 1
            print(f"Request succeeded: {data}")
        else:
            error_count += 1
            print(f"Request failed: {data}")
    
    print(f"Concurrent requests: {success_count} success, {error_count} errors")
    return error_count == 0

if __name__ == '__main__':
    print("Testing database connection fix...")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    health_ok = test_health_endpoint()
    print()
    
    # Test 2: Login endpoint
    print("2. Testing login endpoint...")
    login_ok = test_login_endpoint()
    print()
    
    # Test 3: Concurrent requests
    print("3. Testing concurrent requests...")
    concurrent_ok = test_multiple_requests()
    print()
    
    # Summary
    print("=" * 50)
    print("Test Results:")
    print(f"Health check: {'PASS' if health_ok else 'FAIL'}")
    print(f"Login endpoint: {'PASS' if login_ok else 'FAIL'}")
    print(f"Concurrent requests: {'PASS' if concurrent_ok else 'FAIL'}")
    
    if all([health_ok, login_ok, concurrent_ok]):
        print("\n✅ All tests passed! Database connection issue appears to be fixed.")
    else:
        print("\n❌ Some tests failed. Database connection issue may still exist.")