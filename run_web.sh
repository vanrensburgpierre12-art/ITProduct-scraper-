#!/bin/bash

# Electronics Distributors Scraper - Web Interface Launcher

echo "🔧 Electronics Distributors Scraper"
echo "=================================="
echo "Starting web interface..."
echo ""
echo "The web interface will be available at:"
echo "  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if requirements are installed
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

# Install requirements if needed
echo "📦 Checking dependencies..."
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p output logs templates

# Start the web interface
echo "🚀 Starting Flask application..."
python3 main.py --web