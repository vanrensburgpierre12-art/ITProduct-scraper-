#!/bin/bash

# Electronics Distributors Scraper - Command Line Interface

echo "🔧 Electronics Distributors Scraper"
echo "=================================="
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

# Parse command line arguments
DISTRIBUTORS=""
OUTPUT=""
FORMAT="csv"

while [[ $# -gt 0 ]]; do
    case $1 in
        --distributors)
            DISTRIBUTORS="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --distributors DIST1 DIST2    Scrape specific distributors (Communica, MicroRobotics, Miro)"
            echo "  --output FILE                 Output file path"
            echo "  --format FORMAT               Output format (csv or json)"
            echo "  --help                        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Scrape all distributors"
            echo "  $0 --distributors Communica Miro     # Scrape specific distributors"
            echo "  $0 --output my_products.csv          # Custom output file"
            echo "  $0 --format json                     # Export as JSON"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build command
CMD="python3 main.py"

if [ ! -z "$DISTRIBUTORS" ]; then
    CMD="$CMD --distributors $DISTRIBUTORS"
fi

if [ ! -z "$OUTPUT" ]; then
    CMD="$CMD --output $OUTPUT"
fi

if [ ! -z "$FORMAT" ]; then
    CMD="$CMD --format $FORMAT"
fi

echo "🚀 Starting scraper..."
echo "Command: $CMD"
echo ""

# Run the scraper
eval $CMD