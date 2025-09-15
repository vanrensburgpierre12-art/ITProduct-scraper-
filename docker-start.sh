#!/bin/bash

# Docker startup script for electronics distributors API

set -e

echo "🐳 Starting Electronics Distributors API with Docker"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p output logs ssl

# Set proper permissions
chmod 755 output logs

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before starting the services."
    echo "   The default configuration should work with Docker Compose."
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

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
    echo "📋 Checking logs..."
    docker-compose logs api
    exit 1
fi

# Get admin API key
echo "🔑 Getting admin API key..."
API_KEY=$(docker-compose exec -T postgres psql -U electronics_user -d electronics_db -t -c "SELECT api_key FROM users WHERE username = 'admin';" | tr -d ' \n')

if [ -n "$API_KEY" ]; then
    echo "✅ Admin API Key: $API_KEY"
    echo "📝 Save this API key for testing the API"
else
    echo "⚠️  Could not retrieve admin API key. You may need to initialize the database manually."
fi

echo ""
echo "🎉 Services started successfully!"
echo "=================================================="
echo "🌐 API URL: http://localhost:7000"
echo "📊 Database: localhost:5432 (electronics_db)"
echo "🔑 Admin API Key: $API_KEY"
echo ""
echo "📖 API Documentation:"
echo "   curl -H \"X-API-Key: $API_KEY\" http://localhost:7000/api/products"
echo "   curl -H \"X-API-Key: $API_KEY\" http://localhost:7000/api/stats"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose up --build -d"
echo ""
echo "📚 Full documentation: API_DOCUMENTATION.md"