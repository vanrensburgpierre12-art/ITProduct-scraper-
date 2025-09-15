# Electronics Distributors API Documentation

A real-time database API for South African electronics distributors with live stock tracking, historical data, and WebSocket support.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- PostgreSQL 12+
- Chrome browser (for scraping)

### Installation

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

## 🔐 Authentication

The API uses two authentication methods:

### 1. API Key Authentication (Recommended)
Include your API key in the request header:
```bash
curl -H "X-API-Key: your-api-key-here" http://localhost:7000/api/products
```

### 2. JWT Token Authentication
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

## 📊 API Endpoints

### Authentication

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

### Products

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

### Stock Information

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

**Response**:
```json
{
  "sku": "ABC123",
  "source": "Communica",
  "history": [
    {
      "id": 1,
      "product_id": 1,
      "sku": "ABC123",
      "source": "Communica",
      "price_inc_vat": 150.00,
      "price_ex_vat": 130.43,
      "stock_status": "In Stock",
      "stock_quantity": 25,
      "recorded_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_records": 10
}
```

### Distributors

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

### Statistics

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

### Scraping Control

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

### Export

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

## 🔌 WebSocket Events

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

## 📈 Data Structure

### Product Object
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

### Stock History Object
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

## ⚙️ Configuration

### Environment Variables

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

## 🔄 Scheduled Updates

The API automatically scrapes all distributors every 25 minutes by default. You can:

- Change the interval by setting `SCRAPING_INTERVAL_MINUTES` in `.env`
- Disable scheduled scraping by setting `SCRAPING_ENABLED=false`
- Trigger manual scraping via the `/api/scraping/start` endpoint

## 🚨 Error Handling

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

## 📝 Rate Limiting

- Default: 1000 requests per hour per user
- Configure with `API_RATE_LIMIT` environment variable
- Rate limit headers included in responses

## 🔒 Security

- API key authentication for all endpoints
- JWT tokens for web interface
- Password hashing with bcrypt
- CORS enabled for cross-origin requests
- Input validation and sanitization

## 🐛 Troubleshooting

### Common Issues

1. **PostgreSQL Connection Failed**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Create database: `createdb electronics_db`

2. **Chrome Not Found**
   - Install Chrome browser
   - Ensure Chrome is in PATH

3. **Permission Errors**
   - Check file permissions for output directories
   - Ensure database user has proper permissions

4. **Memory Issues**
   - Reduce `MAX_PAGE_SIZE` in configuration
   - Add delays between scraping requests

### Logs

Check the following log files:
- `logs/scraper_*.log`: Scraping logs
- `logs/errors.log`: Error logs
- Console output: API server logs

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Check the GitHub issues
4. Contact the development team

## 📄 License

This project is provided as-is for educational and commercial purposes.