#!/bin/bash

echo "Restarting electronics API to apply database fixes..."

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Wait a moment
sleep 2

# Start the services
echo "Starting services with updated configuration..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check if API is responding
echo "Checking API health..."
for i in {1..30}; do
    if curl -s http://localhost:7000/api/health > /dev/null; then
        echo "✅ API is responding!"
        break
    else
        echo "⏳ Waiting for API... (attempt $i/30)"
        sleep 2
    fi
done

echo "API restart complete!"
echo "You can now test the fix with: python3 test_db_fix.py"