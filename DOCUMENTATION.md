# Product Importer - Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [Database Schema](#database-schema)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [Development Guide](#development-guide)

---

## Overview

The Product Importer is a scalable web application designed to handle large-scale CSV imports (up to 500,000 records) with real-time progress tracking, comprehensive product management, and webhook integration.

### Key Features

- **Large File Processing**: Handles CSV files up to 500MB with 500,000+ records
- **Real-time Progress**: WebSocket-based live progress updates
- **Asynchronous Processing**: Celery workers prevent HTTP timeouts
- **Memory Efficient**: Chunked processing prevents memory overflow
- **Full CRUD Operations**: Complete product lifecycle management
- **Webhook Integration**: Event-driven notifications
- **Production Ready**: Docker containerization and deployment guides

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | FastAPI (Python 3.11) |
| Task Queue | Celery 5.3.4 |
| Message Broker | Redis 7 |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy 2.0 |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Containerization | Docker & Docker Compose |

---

## Architecture

### System Architecture

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │ HTTP/WebSocket
       ▼
┌─────────────────┐
│   FastAPI App   │
│   (Port 8000)   │
└────┬───────┬────┘
     │       │
     │       └─────────┐
     │                 │
     ▼                 ▼
┌─────────┐      ┌──────────┐
│PostgreSQL│      │  Redis   │
│ (Port    │      │ (Port    │
│  5432)   │      │  6379)   │
└─────────┘      └────┬──────┘
                       │
                       ▼
                 ┌──────────┐
                 │  Celery   │
                 │  Worker  │
                 └──────────┘
```

### Component Overview

1. **FastAPI Application** (`app/main.py`)
   - RESTful API endpoints
   - WebSocket server for real-time updates
   - File upload handling
   - Request validation and error handling

2. **Celery Workers** (`app/tasks.py`)
   - Asynchronous CSV import processing
   - Bulk delete operations
   - Webhook triggering
   - Progress state management

3. **Database Layer** (`app/models.py`, `app/database.py`)
   - Product and Webhook models
   - Connection pooling
   - Transaction management

4. **Frontend** (`static/index.html`)
   - Single-page application
   - Real-time progress visualization
   - Product management interface
   - Webhook configuration UI

### Data Flow

#### CSV Import Process

```
1. User uploads CSV → FastAPI receives file
2. File saved to disk → Celery task queued
3. Celery worker processes CSV in chunks:
   - Parse CSV (pandas)
   - Validate records
   - Batch upsert to PostgreSQL
   - Update progress state in Redis
4. WebSocket sends progress to frontend
5. On completion: Trigger webhooks
```

#### Webhook Triggering

```
1. Product event occurs (create/update/delete)
2. Query enabled webhooks for event type
3. Celery task queues webhook delivery
4. HTTP POST to webhook URL
5. Log response (status code, time)
```

---

## Installation & Setup

### Prerequisites

- **Docker Desktop** (recommended) or
- **Python 3.11+**, **PostgreSQL 15**, **Redis 7**

### Quick Start with Docker

```bash
# 1. Navigate to project directory
cd assingment003

# 2. Start all services
docker-compose up --build

# 3. Access application
# Web UI: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Installation

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Setup PostgreSQL

```bash
# Create database
createdb productdb

# Or using psql
psql -U postgres
CREATE DATABASE productdb;
```

#### 3. Setup Redis

```bash
# Start Redis server
redis-server

# Verify it's running
redis-cli ping  # Should return "PONG"
```

#### 4. Configure Environment

Create `.env` file or set environment variables:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/productdb"
export REDIS_URL="redis://localhost:6379/0"
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
```

#### 5. Initialize Database

```bash
python -c "from app.database import init_db; init_db()"
```

#### 6. Start Services

**Terminal 1 - Celery Worker:**
```bash
celery -A app.celery_app worker --loglevel=info
```

**Terminal 2 - FastAPI Server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/productdb` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://localhost:6379/0` |
| `UPLOAD_DIR` | Directory for uploaded files | `uploads` |
| `MAX_UPLOAD_SIZE` | Maximum file size in bytes | `524288000` (500MB) |
| `CHUNK_SIZE` | Records processed per chunk | `1000` |

### Configuration File

Edit `app/config.py` to customize settings:

```python
class Settings(BaseSettings):
    CHUNK_SIZE: int = 1000  # Adjust for performance
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    # ... other settings
```

### Docker Compose Configuration

Edit `docker-compose.yml` to:
- Change port mappings
- Adjust resource limits
- Modify service configurations

---

## Usage Guide

### CSV Upload

#### CSV Format

Required columns:
- `name` (required): Product name
- `sku` (required): Stock Keeping Unit (unique, case-insensitive)
- `description` (optional): Product description

Example CSV:
```csv
name,sku,description
Product A,PROD-001,Description of Product A
Product B,PROD-002,Description of Product B
```

#### Upload Process

1. Navigate to **Upload CSV** tab
2. Click "Choose File" or drag & drop CSV file
3. Monitor real-time progress:
   - Progress bar shows percentage
   - Status messages indicate current stage
   - Error list shows validation errors (if any)

#### Progress Stages

1. **Parsing CSV** (0-10%): Reading and validating file structure
2. **Validating** (10%): Checking data integrity
3. **Importing** (10-90%): Processing records in chunks
4. **Complete** (100%): All records imported

### Product Management

#### Viewing Products

1. Go to **Products** tab
2. Use filters:
   - **SKU**: Search by stock keeping unit
   - **Name**: Search by product name
   - **Status**: Filter by Active/Inactive
   - **Description**: Search in descriptions
3. Navigate pages using pagination controls

#### Creating Products

1. Click **"+ Add Product"** button
2. Fill in form:
   - SKU (required, unique)
   - Name (required)
   - Description (optional)
   - Active status (default: Active)
3. Click **Save**

#### Editing Products

1. Click **Edit** button on product row
2. Modify fields (SKU cannot be changed)
3. Click **Save**

#### Deleting Products

- **Single Delete**: Click **Delete** button → Confirm
- **Bulk Delete**: Click **"🗑️ Delete All"** → Confirm → Monitor progress

### Webhook Management

#### Creating Webhooks

1. Go to **Webhooks** tab
2. Click **"+ Add Webhook"**
3. Configure:
   - **URL**: Webhook endpoint (must be valid HTTP/HTTPS URL)
   - **Event Type**: 
     - `product.created`
     - `product.updated`
     - `product.deleted`
   - **Enabled**: Toggle on/off
4. Click **Save**

#### Testing Webhooks

1. Click **Test** button on webhook card
2. View results:
   - Success status
   - HTTP status code
   - Response time (milliseconds)

#### Webhook Payload

When triggered, webhooks receive:

```json
{
  "event_type": "product.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "product_id": "uuid-here",
    "count": 1000
  }
}
```

#### Event Types

- **product.created**: Triggered when products are created (CSV import or manual)
- **product.updated**: Triggered when a product is updated
- **product.deleted**: Triggered when products are deleted (single or bulk)

---

## API Reference

### Base URL

- Local: `http://localhost:8000/api`
- Production: `https://your-domain.com/api`

### Authentication

Currently no authentication required. Add authentication middleware for production.

### Endpoints

#### CSV Upload

**POST** `/api/upload`
- Upload CSV file for import
- **Request**: `multipart/form-data` with `file` field
- **Response**: `{"task_id": "uuid", "message": "Upload started"}`
- **Example**:
  ```bash
  curl -X POST http://localhost:8000/api/upload \
    -F "file=@products.csv"
  ```

**GET** `/api/upload/progress/{task_id}`
- Get upload progress (polling endpoint)
- **Response**: Progress object with status, progress, message
- **Example**:
  ```bash
  curl http://localhost:8000/api/upload/progress/{task_id}
  ```

**WS** `/ws/progress/{task_id}`
- WebSocket endpoint for real-time progress
- **Message Format**: JSON with task_id, status, progress, message

#### Products

**GET** `/api/products`
- List products with pagination and filters
- **Query Parameters**:
  - `skip` (int): Number of records to skip (default: 0)
  - `limit` (int): Records per page (default: 50)
  - `sku` (string): Filter by SKU (case-insensitive partial match)
  - `name` (string): Filter by name (case-insensitive partial match)
  - `active` (boolean): Filter by active status
  - `description` (string): Filter by description (case-insensitive partial match)
- **Response**: Paginated product list
- **Example**:
  ```bash
  curl "http://localhost:8000/api/products?skip=0&limit=50&active=true"
  ```

**GET** `/api/products/{id}`
- Get single product by ID
- **Response**: Product object

**POST** `/api/products`
- Create new product
- **Request Body**:
  ```json
  {
    "sku": "PROD-001",
    "name": "Product Name",
    "description": "Product description",
    "active": true
  }
  ```
- **Response**: Created product object

**PUT** `/api/products/{id}`
- Update product
- **Request Body**: Partial product object (sku cannot be updated)
- **Response**: Updated product object

**DELETE** `/api/products/{id}`
- Delete single product
- **Response**: 204 No Content

**DELETE** `/api/products`
- Bulk delete all products
- **Response**: `{"task_id": "uuid", "message": "Bulk delete started"}`

**GET** `/api/products/bulk-delete/status/{task_id}`
- Get bulk delete progress
- **Response**: Task status object

#### Webhooks

**GET** `/api/webhooks`
- List all webhooks
- **Response**: Array of webhook objects

**GET** `/api/webhooks/{id}`
- Get single webhook by ID
- **Response**: Webhook object

**POST** `/api/webhooks`
- Create new webhook
- **Request Body**:
  ```json
  {
    "url": "https://example.com/webhook",
    "event_type": "product.created",
    "enabled": true
  }
  ```
- **Response**: Created webhook object

**PUT** `/api/webhooks/{id}`
- Update webhook
- **Request Body**: Partial webhook object
- **Response**: Updated webhook object

**DELETE** `/api/webhooks/{id}`
- Delete webhook
- **Response**: 204 No Content

**POST** `/api/webhooks/{id}/test`
- Test webhook by sending test event
- **Response**: Test result with status code and response time

### Response Formats

#### Success Response
```json
{
  "id": "uuid",
  "sku": "PROD-001",
  "name": "Product Name",
  "description": "Description",
  "active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Error Response
```json
{
  "detail": "Error message here"
}
```

#### Paginated Response
```json
{
  "items": [...],
  "total": 1000,
  "page": 1,
  "page_size": 50,
  "total_pages": 20
}
```

---

## Database Schema

### Products Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `sku` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Stock Keeping Unit (case-insensitive) |
| `name` | VARCHAR(500) | NOT NULL | Product name |
| `description` | TEXT | NULLABLE | Product description |
| `active` | BOOLEAN | NOT NULL, DEFAULT TRUE, INDEX | Active status |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

### Webhooks Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `url` | VARCHAR(500) | NOT NULL | Webhook URL endpoint |
| `event_type` | VARCHAR(100) | NOT NULL, INDEX | Event type |
| `enabled` | BOOLEAN | NOT NULL, DEFAULT TRUE, INDEX | Enabled status |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

### Indexes

- `products.sku`: Unique index for fast SKU lookups
- `products.active`: Index for filtering by status
- `webhooks.event_type`: Index for event-based queries
- `webhooks.enabled`: Index for filtering enabled webhooks

---

## Deployment

### Docker Compose (Recommended)

```bash
docker-compose up --build -d
```

### Heroku

See `DEPLOYMENT.md` for detailed Heroku deployment instructions.

### Render

See `DEPLOYMENT.md` for detailed Render deployment instructions.

### Production Considerations

1. **Environment Variables**: Use secure secret management
2. **Database**: Use managed PostgreSQL (RDS, Cloud SQL)
3. **Redis**: Use managed Redis (ElastiCache, Memorystore)
4. **SSL/TLS**: Enable HTTPS
5. **Authentication**: Add authentication middleware
6. **Monitoring**: Set up logging and error tracking
7. **Backups**: Configure database backups
8. **Scaling**: Use load balancer for multiple web instances

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Symptoms**: `OperationalError: could not connect to server`

**Solutions**:
- Verify PostgreSQL is running: `pg_isready`
- Check connection string in environment variables
- Ensure database exists: `psql -l | grep productdb`
- Check firewall/network settings

#### 2. Redis Connection Errors

**Symptoms**: `ConnectionError: Error connecting to Redis`

**Solutions**:
- Verify Redis is running: `redis-cli ping`
- Check Redis URL in environment variables
- Ensure Redis is accessible from application
- Check Redis logs for errors

#### 3. Celery Tasks Not Executing

**Symptoms**: Tasks stay in PENDING state

**Solutions**:
- Verify Celery worker is running: `celery -A app.celery_app inspect active`
- Check Redis connection
- Verify `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`
- Check Celery worker logs

#### 4. Upload Progress Not Updating

**Symptoms**: Progress bar stuck or not updating

**Solutions**:
- Check WebSocket connection in browser console
- Verify Celery task is processing
- Check Redis connection
- Try polling endpoint as fallback: `/api/upload/progress/{task_id}`

#### 5. Memory Issues

**Symptoms**: Out of memory errors during CSV import

**Solutions**:
- Reduce `CHUNK_SIZE` in config (default: 1000)
- Increase container/system memory
- Process smaller CSV files
- Monitor memory usage: `docker stats`

#### 6. Port Already in Use

**Symptoms**: `Address already in use` error

**Solutions**:
- Stop other services using ports 8000, 5432, 6379
- Change ports in `docker-compose.yml`
- Find and kill process: `lsof -i :8000` (Mac/Linux)

### Debugging

#### Enable Debug Logging

```python
# In app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### View Docker Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery
```

#### Database Queries

```bash
# Connect to database
docker-compose exec db psql -U postgres -d productdb

# Check table counts
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM webhooks;
```

---

## Development Guide

### Project Structure

```
assingment003/
├── app/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── celery_app.py        # Celery configuration
│   ├── config.py            # Settings
│   ├── database.py          # DB connection
│   ├── main.py              # FastAPI app
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   └── tasks.py             # Celery tasks
├── static/
│   └── index.html           # Frontend
├── uploads/                 # Upload directory
├── docker-compose.yml       # Docker services
├── Dockerfile              # Container definition
├── requirements.txt         # Dependencies
└── README.md               # Main documentation
```

### Adding New Features

#### 1. Add New API Endpoint

```python
# In app/main.py
@app.get("/api/new-endpoint")
async def new_endpoint():
    return {"message": "Hello"}
```

#### 2. Add New Database Model

```python
# In app/models.py
class NewModel(Base):
    __tablename__ = "new_table"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ... other columns
```

#### 3. Add New Celery Task

```python
# In app/tasks.py
@celery_app.task(name="new_task")
def new_task(param1, param2):
    # Task logic
    return result
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions/classes
- Keep functions focused and small
- Write meaningful variable names

### Testing

#### Manual Testing Checklist

- [ ] CSV upload with various file sizes
- [ ] Product CRUD operations
- [ ] Filtering and pagination
- [ ] Bulk delete
- [ ] Webhook creation and testing
- [ ] WebSocket progress updates
- [ ] Error handling

#### Running Tests (when implemented)

```bash
pytest tests/
```

### Performance Optimization

1. **Database**: Add indexes for frequently queried columns
2. **Caching**: Implement Redis caching for read-heavy operations
3. **Connection Pooling**: Tune SQLAlchemy pool settings
4. **Chunk Size**: Adjust `CHUNK_SIZE` based on system resources
5. **Worker Concurrency**: Scale Celery workers based on load

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Celery Documentation**: https://docs.celeryq.dev/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Docker Documentation**: https://docs.docker.com/

---

## Support

For issues, questions, or contributions:
1. Check this documentation
2. Review `README.md` and `QUICKSTART.md`
3. Check existing issues
4. Create a new issue with:
   - Description of problem
   - Steps to reproduce
   - Error messages/logs
   - Environment details

---

**Last Updated**: 2024
**Version**: 1.0.0


