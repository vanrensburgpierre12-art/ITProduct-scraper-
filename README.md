# Electronics Distributors Realtime Database API

A comprehensive real-time database API for South African electronics distributors with live stock tracking, historical data, and WebSocket support.

## 🚀 Features

- **Real-time Database**: PostgreSQL-powered with live stock tracking
- **Multi-Distributor Support**: Scrapes from Communica, MicroRobotics, and Miro Distribution
- **RESTful API**: Comprehensive REST API with authentication
- **WebSocket Support**: Real-time updates via WebSocket connections
- **Historical Tracking**: Track price and stock changes over time
- **Scheduled Updates**: Automatic scraping every 25 minutes
- **Authentication**: API key and JWT token authentication
- **Export Options**: CSV and JSON export capabilities
- **Search & Filtering**: Advanced product search and filtering
- **Statistics**: Comprehensive analytics and reporting

## Supported Distributors

1. **Communica** (https://www.communica.co.za/)
   - Stock Status: "In Stock", "Notify Me", "Only X left"
   
2. **MicroRobotics** (https://www.robotics.org.za/)
   - Stock Status: Exact stock numbers (e.g., "Stock: 47")
   
3. **Miro Distribution** (https://miro.co.za/)
   - Stock Status: "In Stock", "Backorder", "Limited Stock"

## Data Extracted

For each product:
- Source (Distributor name)
- Product Name
- SKU/Product Code
- Category (from breadcrumb navigation)
- Price (including VAT)
- Price (excluding VAT)
- Stock Status
- Stock Quantity (when available)
- Brand/Manufacturer
- Description
- Product URL
- Last Updated timestamp

## 🛠️ Installation

### Prerequisites
- **Docker & Docker Compose** (Recommended)
- OR Python 3.7+ + PostgreSQL 12+ + Chrome browser

### 🐳 Docker Quick Start (Recommended)

1. **Clone and start**:
   ```bash
   git clone <your-repo>
   cd electronics-distributors-api
   ./docker-start.sh
   ```

That's it! The API will be available at `http://localhost:7000`

📖 **Full Docker Guide**: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

### 🐍 Manual Installation

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd electronics-distributors-api
   pip install -r requirements.txt
   ```

2. **Setup PostgreSQL**:
   ```bash
   createdb electronics_db
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Initialize database**:
   ```bash
   python init_db.py
   ```

5. **Start the API**:
   ```bash
   python start_api.py
   ```

The API will be available at `http://localhost:7000`

## 📖 API Usage

### Authentication

The API uses API key authentication. Get your API key from the admin user created during initialization.

```bash
# Using API key
curl -H "X-API-Key: your-api-key-here" http://localhost:7000/api/products

# Using JWT token
curl -H "Authorization: Bearer your-jwt-token" http://localhost:7000/api/products
```

### Example API Calls

```bash
# Get all products
curl -H "X-API-Key: your-key" http://localhost:7000/api/products

# Search products
curl -H "X-API-Key: your-key" "http://localhost:7000/api/products/search?q=arduino"

# Get stock info for a specific product
curl -H "X-API-Key: your-key" http://localhost:7000/api/stock/ABC123

# Get products from specific distributor
curl -H "X-API-Key: your-key" http://localhost:7000/api/distributors/Communica/products

# Get statistics
curl -H "X-API-Key: your-key" http://localhost:7000/api/stats
```

### WebSocket Integration

```javascript
const socket = io('http://localhost:7000');

// Join scraping updates room
socket.emit('join_room', { room: 'scraping' });

// Listen for real-time updates
socket.on('scraping_progress', (data) => {
  console.log('Scraping progress:', data);
});

socket.on('distributor_completed', (data) => {
  console.log('Distributor completed:', data);
});
```

## 🔧 Management Commands

### Docker Commands
```bash
# Start services
./docker-start.sh

# Test API
./docker-test.sh

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

### Legacy CLI Usage
The original CLI interface is still available:

```bash
# Scrape all distributors
python main.py

# Scrape specific distributors
python main.py --distributors Communica MicroRobotics

# Start web interface (legacy)
python main.py --web
```

## Output Files

- `distributors_products.csv` - Combined results from all distributors
- `communica.csv` - Communica products only
- `microrobotics.csv` - MicroRobotics products only
- `miro.csv` - Miro Distribution products only
- `distributors_products.json` - JSON format (when requested)

## Configuration

Edit `config.py` to modify:
- Request delays
- Timeout settings
- Output directories
- User agents
- Logging settings

## Scheduling

For daily automated runs, add to crontab:
```bash
# Run every day at 2 AM
0 2 * * * cd /path/to/scraper && python main.py
```

## Error Handling

- Failed products are logged to `logs/errors.log`
- Individual scraper errors don't stop the entire process
- Retry logic for network requests
- Graceful handling of missing elements

## Requirements

- Python 3.7+
- Chrome browser
- Internet connection
- Required Python packages (see requirements.txt)

## Troubleshooting

1. **Chrome not found**: Install Chrome browser
2. **Permission errors**: Check file permissions for output directories
3. **Network timeouts**: Increase timeout values in config.py
4. **Memory issues**: Reduce batch sizes or add delays

## Legal Notice

This scraper is for educational and research purposes. Please respect the robots.txt files and terms of service of the target websites. Use appropriate delays between requests to avoid overloading the servers.

## License

This project is provided as-is for educational purposes.