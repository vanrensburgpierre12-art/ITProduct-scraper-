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

The API supports two authentication methods:

#### 1. API Key Authentication (Recommended)
Include your API key in the request header:
```bash
curl -H "X-API-Key: your-api-key-here" http://localhost:7000/api/products
```

#### 2. JWT Token Authentication
Login to get a JWT token:
```bash
curl -X POST http://localhost:7000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Then use the token:
```bash
curl -H "Authorization: Bearer your-jwt-token" http://localhost:7000/api/products
```

### 🔐 Authentication Endpoints

#### POST `/api/auth/register`
Register a new user.

**Request Body**:
```json
{
  "username": "string",
  "email": "string", 
  "password": "string"
}
```

**Response**:
```json
{
  "message": "User created successfully",
  "user": {...},
  "api_key": "string"
}
```

#### POST `/api/auth/login`
Login and get JWT token.

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "access_token": "string",
  "user": {...},
  "api_key": "string"
}
```

#### GET `/api/auth/me`
Get current user information.

**Headers**: `X-API-Key` or `Authorization: Bearer <token>`

### 📦 Product Endpoints

#### GET `/api/products`
Get all products with pagination and filtering.

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 50, max: 1000)
- `source` (string): Filter by distributor
- `stock_status` (string): Filter by stock status
- `category` (string): Filter by category
- `brand` (string): Filter by brand
- `search` (string): Search in name, SKU, description
- `min_price` (float): Minimum price filter
- `max_price` (float): Maximum price filter

**Example**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/products?source=Communica&stock_status=In%20Stock&page=1&per_page=20"
```

**Response**:
```json
{
  "products": [
    {
      "id": 1,
      "sku": "ABC123",
      "source": "Communica",
      "product_name": "Arduino Uno R3",
      "category": "Microcontrollers",
      "price_inc_vat": 150.00,
      "price_ex_vat": 130.43,
      "stock_status": "In Stock",
      "stock_quantity": 25,
      "brand": "Arduino",
      "description": "Popular microcontroller board",
      "product_url": "https://...",
      "last_updated": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1500,
    "pages": 75,
    "has_next": true,
    "has_prev": false
  }
}
```

#### GET `/api/products/{sku}`
Get specific product by SKU.

**Query Parameters**:
- `source` (string, optional): Filter by distributor

**Example**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/products/ABC123?source=Communica"
```

#### GET `/api/products/search`
Search products with advanced filtering.

**Query Parameters**:
- `q` (string, required): Search query
- `page` (int): Page number
- `per_page` (int): Items per page

**Example**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/products/search?q=arduino&page=1"
```

### 📊 Stock Information Endpoints

#### GET `/api/stock/{sku}`
Get current stock information for a product.

**Query Parameters**:
- `source` (string, optional): Filter by distributor

**Example**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/stock/ABC123"
```

**Response**:
```json
{
  "sku": "ABC123",
  "sources": [
    {
      "source": "Communica",
      "stock_status": "In Stock",
      "stock_quantity": 25,
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### GET `/api/stock/history/{sku}`
Get stock history for a product.

**Query Parameters**:
- `source` (string, optional): Filter by distributor
- `days` (int): Number of days to look back (default: 30)

**Example**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/stock/history/ABC123?days=7"
```

### 🏢 Distributor Endpoints

#### GET `/api/distributors`
Get list of available distributors.

**Example**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/distributors"
```

**Response**:
```json
{
  "distributors": [
    {
      "name": "Communica",
      "product_count": 500,
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### GET `/api/distributors/{distributor_name}/products`
Get products from a specific distributor.

**Query Parameters**:
- `page` (int): Page number
- `per_page` (int): Items per page
- `stock_status` (string): Filter by stock status
- `category` (string): Filter by category
- `brand` (string): Filter by brand

**Example**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/distributors/Communica/products?stock_status=In%20Stock"
```

### 📈 Statistics Endpoints

#### GET `/api/stats`
Get overall statistics.

**Example**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/stats"
```

**Response**:
```json
{
  "total_products": 1500,
  "by_distributor": {
    "Communica": 500,
    "MicroRobotics": 400,
    "Miro": 600
  },
  "by_stock_status": {
    "In Stock": 800,
    "Out of Stock": 300,
    "Low Stock": 200,
    "Notify Me": 200
  },
  "price_range": {
    "min": 5.50,
    "max": 2500.00,
    "avg": 125.75
  },
  "recent_updates_24h": 150
}
```

### 🔄 Scraping Control Endpoints

#### GET `/api/scraping/status`
Get current scraping status.

**Example**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/scraping/status"
```

#### POST `/api/scraping/start`
Start manual scraping (admin only).

**Request Body**:
```json
{
  "distributors": ["Communica", "MicroRobotics", "Miro"]
}
```

#### GET `/api/scraping/logs`
Get scraping logs.

**Query Parameters**:
- `page` (int): Page number
- `per_page` (int): Items per page

### 📤 Export Endpoints

#### GET `/api/export/csv`
Export products to CSV.

**Query Parameters**:
- `source` (string, optional): Filter by distributor

**Example**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/export/csv?source=Communica" \
  --output products.csv
```

#### GET `/api/export/json`
Export products to JSON.

**Query Parameters**:
- `source` (string, optional): Filter by distributor

### 🌐 Web Interface API (Legacy)

The following endpoints are available for the simple web interface:

#### POST `/api/start_scraping`
Start the scraping process.

**Request Body**:
```json
{
  "distributors": ["Communica", "MicroRobotics", "Miro"]
}
```

#### GET `/api/status`
Get current scraping status.

#### GET `/api/products`
Get scraped products (web interface).

**Query Parameters**:
- `page` (int): Page number
- `per_page` (int): Items per page

#### GET `/api/download_csv`
Download the CSV file.

#### GET `/api/download_json`
Download the JSON file.

#### GET `/api/stats`
Get statistics about scraped products.

### 🔌 WebSocket Integration

Connect to WebSocket for real-time updates:

```javascript
const socket = io('http://localhost:7000');

// Join scraping updates room
socket.emit('join_room', { room: 'scraping' });

// Listen for events
socket.on('scraping_progress', (data) => {
  console.log('Scraping progress:', data);
});

socket.on('distributor_completed', (data) => {
  console.log('Distributor completed:', data);
});

socket.on('scraping_completed', (data) => {
  console.log('Scraping completed:', data);
});

socket.on('scraping_error', (data) => {
  console.log('Scraping error:', data);
});
```

**WebSocket Events**:
- `connected`: Client connected confirmation
- `joined_room`: Confirmation of joining a room
- `left_room`: Confirmation of leaving a room
- `scraping_progress`: Real-time scraping progress updates
- `distributor_completed`: When a distributor scraping is completed
- `scraping_completed`: When all scraping is finished
- `scraping_error`: When scraping encounters an error

### 📊 Data Structure

#### Product Object
```json
{
  "id": 1,
  "sku": "string",
  "source": "string",
  "product_name": "string",
  "category": "string",
  "price_inc_vat": 150.00,
  "price_ex_vat": 130.43,
  "stock_status": "In Stock|Out of Stock|Low Stock|Notify Me",
  "stock_quantity": 25,
  "brand": "string",
  "description": "string",
  "product_url": "string",
  "last_updated": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "metadata": {}
}
```

#### Stock History Object
```json
{
  "id": 1,
  "product_id": 1,
  "sku": "string",
  "source": "string",
  "price_inc_vat": 150.00,
  "price_ex_vat": 130.43,
  "stock_status": "string",
  "stock_quantity": 25,
  "recorded_at": "2024-01-15T10:30:00Z"
}
```

### ⚙️ Configuration

#### Environment Variables

Create a `.env` file with:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/electronics_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=electronics_db
DB_USER=username
DB_PASSWORD=password

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# API Configuration
API_RATE_LIMIT=1000
DEFAULT_PAGE_SIZE=50
MAX_PAGE_SIZE=1000

# Scraping Configuration
SCRAPING_INTERVAL_MINUTES=25
SCRAPING_ENABLED=true

# WebSocket Configuration
WEBSOCKET_ENABLED=true
```

### 🔄 Scheduled Updates

The API automatically scrapes all distributors every 25 minutes by default. You can:

- Change the interval by setting `SCRAPING_INTERVAL_MINUTES` in `.env`
- Disable scheduled scraping by setting `SCRAPING_ENABLED=false`
- Trigger manual scraping via the `/api/scraping/start` endpoint

### 🚨 Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (missing or invalid authentication)
- `404`: Not Found
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error

Error responses include a descriptive message:

```json
{
  "error": "Authentication required"
}
```

### 📝 Rate Limiting

- Default: 1000 requests per hour per user
- Configure with `API_RATE_LIMIT` environment variable
- Rate limit headers included in responses

### 🔒 Security

- API key authentication for all endpoints
- JWT tokens for web interface
- Password hashing with bcrypt
- CORS enabled for cross-origin requests
- Input validation and sanitization

### 🚀 Complete API Examples

Here are comprehensive examples of how to use all the API endpoints:

#### Authentication Examples
```bash
# Register a new user
curl -X POST http://localhost:7000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword123"
  }'

# Login and get API key
curl -X POST http://localhost:7000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Get current user info
curl -H "X-API-Key: your-api-key" \
  http://localhost:7000/api/auth/me
```

#### Product Search Examples
```bash
# Get all products with pagination
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/products?page=1&per_page=20"

# Search for Arduino products
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/products/search?q=arduino&page=1"

# Filter by distributor and stock status
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/products?source=Communica&stock_status=In%20Stock"

# Filter by price range
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/products?min_price=50&max_price=200"

# Filter by category and brand
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/products?category=Microcontrollers&brand=Arduino"
```

#### Stock Information Examples
```bash
# Get stock info for a specific product
curl -H "X-API-Key: your-key" \
  http://localhost:7000/api/stock/ABC123

# Get stock info from specific distributor
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/stock/ABC123?source=Communica"

# Get stock history for last 7 days
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/stock/history/ABC123?days=7"

# Get stock history from specific distributor
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/stock/history/ABC123?source=Communica&days=30"
```

#### Distributor Examples
```bash
# Get all distributors
curl -H "X-API-Key: your-key" \
  http://localhost:7000/api/distributors

# Get products from Communica
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/distributors/Communica/products?page=1&per_page=50"

# Get in-stock products from MicroRobotics
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/distributors/MicroRobotics/products?stock_status=In%20Stock"

# Get Arduino products from Miro
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/distributors/Miro/products?brand=Arduino"
```

#### Statistics Examples
```bash
# Get overall statistics
curl -H "X-API-Key: your-key" \
  http://localhost:7000/api/stats

# Get statistics from web interface
curl http://localhost:7000/api/stats
```

#### Scraping Control Examples
```bash
# Check scraping status
curl -H "X-API-Key: your-key" \
  http://localhost:7000/api/scraping/status

# Start manual scraping (admin only)
curl -X POST http://localhost:7000/api/scraping/start \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "distributors": ["Communica", "MicroRobotics", "Miro"]
  }'

# Get scraping logs
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/scraping/logs?page=1&per_page=20"
```

#### Export Examples
```bash
# Export all products to CSV
curl -H "X-API-Key: your-key" \
  http://localhost:7000/api/export/csv \
  --output all_products.csv

# Export Communica products to CSV
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/export/csv?source=Communica" \
  --output communica_products.csv

# Export to JSON
curl -H "X-API-Key: your-key" \
  "http://localhost:7000/api/export/json?source=MicroRobotics" \
  --output microrobotics_products.json
```

#### Web Interface Examples (Legacy)
```bash
# Start scraping via web interface
curl -X POST http://localhost:7000/api/start_scraping \
  -H "Content-Type: application/json" \
  -d '{
    "distributors": ["Communica", "MicroRobotics", "Miro"]
  }'

# Get scraping status
curl http://localhost:7000/api/status

# Get products from web interface
curl "http://localhost:7000/api/products?page=1&per_page=50"

# Download CSV from web interface
curl http://localhost:7000/api/download_csv \
  --output web_products.csv

# Download JSON from web interface
curl http://localhost:7000/api/download_json \
  --output web_products.json
```

#### JavaScript/WebSocket Examples
```javascript
// Connect to WebSocket
const socket = io('http://localhost:7000');

// Join scraping room for real-time updates
socket.emit('join_room', { room: 'scraping' });

// Listen for scraping progress
socket.on('scraping_progress', (data) => {
  console.log('Progress:', data.progress + '%');
  console.log('Current distributor:', data.current_distributor);
  console.log('Products completed:', data.completed_products);
});

// Listen for distributor completion
socket.on('distributor_completed', (data) => {
  console.log(`${data.distributor} completed:`, {
    found: data.products_found,
    updated: data.products_updated,
    new: data.products_new
  });
});

// Listen for scraping completion
socket.on('scraping_completed', (data) => {
  console.log('All scraping completed:', {
    total: data.total_products,
    updated: data.total_updated,
    new: data.total_new
  });
});

// Listen for errors
socket.on('scraping_error', (data) => {
  console.error('Scraping error:', data.error);
});

// Make API calls with authentication
const apiKey = 'your-api-key-here';

// Fetch products
fetch('http://localhost:7000/api/products?page=1&per_page=20', {
  headers: {
    'X-API-Key': apiKey
  }
})
.then(response => response.json())
.then(data => {
  console.log('Products:', data.products);
  console.log('Pagination:', data.pagination);
});

// Search products
fetch('http://localhost:7000/api/products/search?q=arduino', {
  headers: {
    'X-API-Key': apiKey
  }
})
.then(response => response.json())
.then(data => {
  console.log('Search results:', data.products);
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