# Product Importer - Scalable CSV Import System

A high-performance web application for importing and managing up to 500,000 product records from CSV files into a PostgreSQL database. Built with FastAPI, Celery, and modern web technologies.

## 🚀 Features

### Core Functionality

- **CSV Import**: Upload and import up to 500,000 product records
  - Real-time progress tracking via WebSocket
  - Automatic duplicate handling (case-insensitive SKU matching)
  - Memory-efficient chunked processing
  - Error reporting and validation

- **Product Management**: Full CRUD operations
  - List products with pagination (50 per page)
  - Filter by SKU, name, status, or description
  - Create, update, and delete products
  - Inline editing with modal forms
  - Active/Inactive status management

- **Bulk Operations**: 
  - Delete all products with confirmation
  - Asynchronous processing with progress tracking

- **Webhook Management**:
  - Configure multiple webhooks
  - Event types: `product.created`, `product.updated`, `product.deleted`
  - Enable/disable webhooks
  - Test webhooks with response time and status code
  - Asynchronous webhook triggering

### Technical Highlights

- **Asynchronous Processing**: Celery workers handle long-running tasks
- **Real-time Updates**: WebSocket support for live progress tracking
- **Scalable Architecture**: Designed to handle large datasets efficiently
- **Memory Efficient**: Chunked CSV processing prevents memory overflow
- **Production Ready**: Docker containerization for easy deployment

## 📋 Technology Stack

- **Backend Framework**: FastAPI (Python 3.11)
- **Task Queue**: Celery with Redis
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Containerization**: Docker & Docker Compose
- **WebSocket**: Native FastAPI WebSocket support

## 🛠️ Installation & Setup

### Prerequisites

- Docker and Docker Compose installed
- Git (for cloning the repository)

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd assingment003
   ```

2. **Create environment file** (optional, defaults are set):
   ```bash
   cp .env.example .env  # Edit if needed
   ```

3. **Start the application with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - Redis server (port 6379)
   - FastAPI web application (port 8000)
   - Celery worker for async tasks

4. **Access the application**:
   - Web UI: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

### Manual Setup (Without Docker)

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**:
   ```bash
   createdb productdb
   ```

3. **Set environment variables**:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/productdb"
   export REDIS_URL="redis://localhost:6379/0"
   export CELERY_BROKER_URL="redis://localhost:6379/0"
   export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
   ```

4. **Initialize the database**:
   ```bash
   python -c "from app.database import init_db; init_db()"
   ```

5. **Start Redis** (if not running):
   ```bash
   redis-server
   ```

6. **Start Celery worker** (in a separate terminal):
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

7. **Start the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📖 Usage Guide

### CSV Upload

1. Navigate to the **Upload CSV** tab
2. Click "Choose File" or drag and drop a CSV file
3. The CSV should have the following columns:
   - `name` (required): Product name
   - `sku` (required): Stock Keeping Unit (unique, case-insensitive)
   - `description` (optional): Product description

4. Monitor the upload progress in real-time:
   - Progress bar shows percentage complete
   - Status messages indicate current stage (Parsing → Validating → Importing → Complete)
   - Errors are displayed if any occur

### Product Management

1. Navigate to the **Products** tab
2. Use filters to search by:
   - SKU
   - Name
   - Status (Active/Inactive)
   - Description

3. **Create Product**: Click "+ Add Product" button
4. **Edit Product**: Click "Edit" button on any product row
5. **Delete Product**: Click "Delete" button (with confirmation)
6. **Bulk Delete**: Click "🗑️ Delete All" button (requires confirmation)

### Webhook Management

1. Navigate to the **Webhooks** tab
2. **Add Webhook**: Click "+ Add Webhook"
   - Enter webhook URL
   - Select event type (product.created, product.updated, product.deleted)
   - Enable/disable toggle

3. **Test Webhook**: Click "Test" to send a test event
   - View response status code and response time

4. **Edit/Delete**: Use respective buttons on each webhook card

## 🔌 API Endpoints

### CSV Upload
- `POST /api/upload` - Upload CSV file
- `GET /api/upload/progress/{task_id}` - Get upload progress
- `WS /ws/progress/{task_id}` - WebSocket for real-time progress

### Products
- `GET /api/products` - List products (with pagination and filters)
- `GET /api/products/{id}` - Get single product
- `POST /api/products` - Create product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- `DELETE /api/products` - Bulk delete all products
- `GET /api/products/bulk-delete/status/{task_id}` - Get bulk delete status

### Webhooks
- `GET /api/webhooks` - List all webhooks
- `GET /api/webhooks/{id}` - Get single webhook
- `POST /api/webhooks` - Create webhook
- `PUT /api/webhooks/{id}` - Update webhook
- `DELETE /api/webhooks/{id}` - Delete webhook
- `POST /api/webhooks/{id}/test` - Test webhook

## 🐳 Docker Configuration

### Services

- **web**: FastAPI application
- **celery**: Celery worker for async tasks
- **db**: PostgreSQL 15 database
- **redis**: Redis server for Celery broker/backend

### Volumes

- `postgres_data`: Persistent database storage
- `uploads`: Temporary file storage for CSV uploads

### Environment Variables

All services use environment variables for configuration. Defaults are set in `docker-compose.yml`:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `CELERY_BROKER_URL`: Celery broker URL
- `CELERY_RESULT_BACKEND`: Celery result backend URL

## 🚢 Deployment

### Heroku Deployment

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL addon**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Add Redis addon**:
   ```bash
   heroku addons:create heroku-redis:mini
   ```

5. **Set environment variables**:
   ```bash
   heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL)
   heroku config:set REDIS_URL=$(heroku config:get REDIS_URL)
   heroku config:set CELERY_BROKER_URL=$(heroku config:get REDIS_URL)
   heroku config:set CELERY_RESULT_BACKEND=$(heroku config:get REDIS_URL)
   ```

6. **Deploy**:
   ```bash
   git push heroku main
   ```

7. **Start Celery worker**:
   ```bash
   heroku ps:scale celery=1
   ```

### Render Deployment

1. Create a new **Web Service** on Render
2. Connect your Git repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `DATABASE_URL` (from Render PostgreSQL)
   - `REDIS_URL` (from Render Redis)
   - `CELERY_BROKER_URL`
   - `CELERY_RESULT_BACKEND`

6. Create a separate **Background Worker**:
   - Build command: `pip install -r requirements.txt`
   - Start command: `celery -A app.celery_app worker --loglevel=info`
   - Use same environment variables

### AWS/GCP Deployment

For AWS or GCP, use container services:
- **AWS**: ECS or EKS with RDS (PostgreSQL) and ElastiCache (Redis)
- **GCP**: Cloud Run with Cloud SQL (PostgreSQL) and Memorystore (Redis)

## 📊 Performance Optimizations

1. **Chunked Processing**: CSV files are processed in chunks of 1,000 records
2. **Batch Upserts**: PostgreSQL `ON CONFLICT` for efficient duplicate handling
3. **Connection Pooling**: SQLAlchemy connection pool (10 connections, 20 overflow)
4. **Async Tasks**: Long-running operations handled by Celery workers
5. **Memory Efficiency**: Streaming CSV parsing prevents memory overflow

## 🧪 Testing

### Manual Testing

1. **Upload Test**:
   - Use the provided `products.csv` file
   - Monitor progress in real-time
   - Verify products are imported correctly

2. **Product CRUD**:
   - Create, read, update, delete products
   - Test filtering and pagination

3. **Webhook Testing**:
   - Use a webhook testing service (e.g., webhook.site)
   - Configure webhook and trigger test
   - Verify events are sent on product operations

## 📝 CSV Format

The CSV file should have the following structure:

```csv
name,sku,description
Product Name,PROD-001,Product description here
Another Product,PROD-002,Another description
```

**Requirements**:
- Header row required: `name,sku,description`
- `name` and `sku` are required fields
- `description` is optional
- SKU is case-insensitive (duplicates will overwrite)
- Maximum file size: 500MB

## 🔒 Security Considerations

- Input validation on all endpoints
- SQL injection protection via SQLAlchemy ORM
- File size limits enforced
- CSRF protection recommended for production
- Environment variable management for secrets

## 🐛 Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Ensure PostgreSQL is running
   - Check `DATABASE_URL` environment variable
   - Verify database exists

2. **Celery tasks not executing**:
   - Check Redis is running
   - Verify Celery worker is started
   - Check `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`

3. **Upload progress not updating**:
   - Check WebSocket connection in browser console
   - Verify Celery task is running
   - Check Redis connection

4. **Memory issues with large files**:
   - Ensure chunked processing is working
   - Check available system memory
   - Reduce `CHUNK_SIZE` in config if needed

## 📄 License

This project is created for assignment purposes.

## 👥 Author

Built for Acme Inc. - Product Importer Assignment

## 🔗 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Note**: This application is optimized for handling large CSV imports (up to 500,000 records) with real-time progress tracking and asynchronous processing to avoid HTTP timeouts.

#   a s s i n g m e t - 0 0 3  
 #   a s s i n g m e t - 0 0 3  
 