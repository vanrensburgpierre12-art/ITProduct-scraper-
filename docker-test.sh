#!/bin/bash

# Docker test script for electronics distributors API

set -e

echo "🧪 Testing Electronics Distributors API with Docker"
echo "=================================================="

# Check if services are running
echo "🔍 Checking if services are running..."
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Services are not running. Please start them first:"
    echo "   ./docker-start.sh"
    exit 1
fi

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:7000/api/auth/me > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Attempt $attempt/$max_attempts - waiting for API..."
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ API failed to start within expected time"
    exit 1
fi

# Get admin API key
echo "🔑 Getting admin API key..."
API_KEY=$(docker-compose exec -T postgres psql -U electronics_user -d electronics_db -t -c "SELECT api_key FROM users WHERE username = 'admin';" | tr -d ' \n')

if [ -z "$API_KEY" ]; then
    echo "❌ Could not retrieve admin API key"
    exit 1
fi

echo "✅ Admin API Key: $API_KEY"

# Test API endpoints
echo ""
echo "🧪 Testing API endpoints..."

# Test authentication
echo "🔐 Testing authentication..."
if curl -s -H "X-API-Key: $API_KEY" http://localhost:7000/api/auth/me | grep -q "admin"; then
    echo "✅ Authentication test passed"
else
    echo "❌ Authentication test failed"
    exit 1
fi

# Test products endpoint
echo "📦 Testing products endpoint..."
if curl -s -H "X-API-Key: $API_KEY" http://localhost:7000/api/products | grep -q "products"; then
    echo "✅ Products endpoint test passed"
else
    echo "❌ Products endpoint test failed"
    exit 1
fi

# Test distributors endpoint
echo "🏪 Testing distributors endpoint..."
if curl -s -H "X-API-Key: $API_KEY" http://localhost:7000/api/distributors | grep -q "distributors"; then
    echo "✅ Distributors endpoint test passed"
else
    echo "❌ Distributors endpoint test failed"
    exit 1
fi

# Test statistics endpoint
echo "📊 Testing statistics endpoint..."
if curl -s -H "X-API-Key: $API_KEY" http://localhost:7000/api/stats | grep -q "total_products"; then
    echo "✅ Statistics endpoint test passed"
else
    echo "❌ Statistics endpoint test failed"
    exit 1
fi

# Test search endpoint
echo "🔍 Testing search endpoint..."
if curl -s -H "X-API-Key: $API_KEY" "http://localhost:7000/api/products/search?q=test" | grep -q "products"; then
    echo "✅ Search endpoint test passed"
else
    echo "❌ Search endpoint test failed"
    exit 1
fi

# Test scraping status endpoint
echo "🔄 Testing scraping status endpoint..."
if curl -s -H "X-API-Key: $API_KEY" http://localhost:7000/api/scraping/status | grep -q "is_running"; then
    echo "✅ Scraping status endpoint test passed"
else
    echo "❌ Scraping status endpoint test failed"
    exit 1
fi

echo ""
echo "🎉 All tests passed!"
echo "=================================================="
echo "🌐 API URL: http://localhost:7000"
echo "🔑 Admin API Key: $API_KEY"
echo ""
echo "📖 Example API calls:"
echo "   curl -H \"X-API-Key: $API_KEY\" http://localhost:7000/api/products"
echo "   curl -H \"X-API-Key: $API_KEY\" http://localhost:7000/api/stats"
echo "   curl -H \"X-API-Key: $API_KEY\" \"http://localhost:7000/api/products/search?q=arduino\""
echo ""
echo "🔧 Management commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"