# 🐳 Docker Deployment Guide

Complete guide for deploying the Electronics Distributors API using Docker and Docker Compose.

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Git

### 1. Clone and Setup
```bash
git clone <your-repo>
cd electronics-distributors-api
```

### 2. Start with Docker
```bash
# Make scripts executable
chmod +x docker-start.sh docker-test.sh

# Start all services
./docker-start.sh
```

That's it! The API will be available at `http://localhost:7000`

## 📋 Docker Services

The Docker setup includes:

- **PostgreSQL Database**: Stores all product and stock data
- **Redis**: Caching and session storage
- **API Application**: Main Flask application with scraping
- **Nginx** (optional): Reverse proxy for production

## 🔧 Configuration

### Environment Variables

Copy the Docker environment template:
```bash
cp .env.docker .env
```

Edit `.env` for your configuration:
```env
# Database
POSTGRES_PASSWORD=your-secure-password
DATABASE_URL=postgresql://electronics_user:your-secure-password@postgres:5432/electronics_db

# Security
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# API Settings
API_RATE_LIMIT=1000
SCRAPING_INTERVAL_MINUTES=25
```

## 🎯 Deployment Options

### Development Mode
```bash
# Start with development configuration
docker-compose -f docker-compose.dev.yml up --build

# With live code reloading
docker-compose -f docker-compose.dev.yml up --build
```

### Production Mode
```bash
# Start with production configuration
docker-compose -f docker-compose.prod.yml up --build -d

# With Nginx reverse proxy
docker-compose -f docker-compose.prod.yml --profile production up --build -d
```

### Basic Mode (Default)
```bash
# Start with basic configuration
docker-compose up --build -d
```

## 🧪 Testing

### Run Tests
```bash
# Test the API
./docker-test.sh

# Or manually test
curl -H "X-API-Key: your-api-key" http://localhost:7000/api/products
```

### Get API Key
```bash
# Get admin API key
docker-compose exec postgres psql -U electronics_user -d electronics_db -c "SELECT api_key FROM users WHERE username = 'admin';"
```

## 📊 Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Check Status
```bash
# Service status
docker-compose ps

# Resource usage
docker stats
```

### Health Checks
```bash
# API health
curl http://localhost:7000/api/auth/me

# Database health
docker-compose exec postgres pg_isready -U electronics_user -d electronics_db

# Redis health
docker-compose exec redis redis-cli ping
```

## 🔄 Management Commands

### Start/Stop Services
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up --build -d
```

### Database Operations
```bash
# Access database
docker-compose exec postgres psql -U electronics_user -d electronics_db

# Create backup
docker-compose exec postgres pg_dump -U electronics_user electronics_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U electronics_user -d electronics_db < backup.sql
```

### Application Operations
```bash
# Access API container
docker-compose exec api bash

# Run Python commands
docker-compose exec api python -c "from database import db; print('Database connected')"

# Initialize database
docker-compose exec api python init_db.py
```

## 🗄️ Data Persistence

### Volumes
- `postgres_data`: Database files
- `redis_data`: Redis data
- `./output`: Scraped data exports
- `./logs`: Application logs

### Backup Strategy
```bash
# Enable backup service (production)
docker-compose -f docker-compose.prod.yml --profile backup up -d

# Manual backup
docker-compose exec postgres pg_dump -U electronics_user electronics_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

## 🔒 Security

### Production Security
1. **Change default passwords** in `.env`
2. **Use strong secrets** for JWT and Flask
3. **Enable HTTPS** with SSL certificates
4. **Configure firewall** rules
5. **Regular updates** of base images

### SSL/HTTPS Setup
```bash
# Place SSL certificates in ./ssl/
mkdir ssl
# Add your cert.pem and key.pem files

# Start with Nginx
docker-compose -f docker-compose.prod.yml --profile production up -d
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# In docker-compose.yml
api:
  deploy:
    replicas: 3
    resources:
      limits:
        memory: 1G
```

### Load Balancing
```yaml
# Add to docker-compose.yml
nginx:
  # Configure load balancing in nginx.conf
  upstream api {
    server api_1:7000;
    server api_2:7000;
    server api_3:7000;
  }
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :7000
   
   # Change ports in docker-compose.yml
   ports:
     - "8000:7000"  # Use port 8000 instead
   ```

2. **Database connection issues**
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Test connection
   docker-compose exec api python -c "from database import db; print('Connected')"
   ```

3. **Memory issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits
   deploy:
     resources:
       limits:
         memory: 2G
   ```

4. **Permission issues**
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER output logs
   chmod 755 output logs
   ```

### Debug Mode
```bash
# Start with debug logging
FLASK_ENV=development docker-compose up

# Access container for debugging
docker-compose exec api bash
```

## 📚 Advanced Configuration

### Custom Nginx Configuration
Edit `nginx.conf` for custom routing, SSL, or load balancing.

### Custom Dockerfile
Modify `Dockerfile` for additional system packages or configurations.

### Environment-specific Configs
- `docker-compose.dev.yml`: Development with live reloading
- `docker-compose.prod.yml`: Production with optimizations
- `docker-compose.yml`: Basic configuration

## 🔄 Updates

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up --build -d
```

### Update Dependencies
```bash
# Update requirements.txt
pip freeze > requirements.txt

# Rebuild image
docker-compose build --no-cache api
docker-compose up -d
```

## 📞 Support

For Docker-related issues:
1. Check the troubleshooting section
2. Review Docker logs: `docker-compose logs`
3. Check resource usage: `docker stats`
4. Verify configuration: `docker-compose config`

## 🎉 Success!

Your Electronics Distributors API is now running in Docker! 

- **API**: http://localhost:7000
- **Database**: localhost:5432
- **Redis**: localhost:6379

Start scraping and building your applications! 🚀