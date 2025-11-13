# Quick Start Guide

## 🚀 Running the Application (Easiest Method - Docker)

### Step 1: Prerequisites
Make sure you have installed:
- **Docker Desktop** (includes Docker and Docker Compose)
  - Download from: https://www.docker.com/products/docker-desktop
  - Start Docker Desktop before proceeding

### Step 2: Open Terminal/Command Prompt
- **Windows**: Open PowerShell or Command Prompt
- **Mac/Linux**: Open Terminal

### Step 3: Navigate to Project Directory
```bash
cd "C:\Users\abhis\IdeaProjects\personal\assingment-\assingment003"
```

### Step 4: Start the Application
```bash
docker-compose up --build
```

**What this does:**
- Builds the Docker images
- Starts PostgreSQL database
- Starts Redis server
- Starts FastAPI web application
- Starts Celery worker for background tasks

**First time setup may take 2-5 minutes** (downloading images, installing dependencies)

### Step 5: Access the Application
Once you see messages like:
```
web-1    | INFO:     Uvicorn running on http://0.0.0.0:8000
```

Open your browser and go to:
- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Step 6: Stop the Application
Press `Ctrl + C` in the terminal, then run:
```bash
docker-compose down
```

---

## 📝 Alternative: Manual Setup (Without Docker)

If you prefer not to use Docker:

### Step 1: Install Python 3.11
Download from: https://www.python.org/downloads/

### Step 2: Install PostgreSQL
- Download from: https://www.postgresql.org/download/
- Create a database named `productdb`

### Step 3: Install Redis
- **Windows**: Download from: https://github.com/microsoftarchive/redis/releases
- **Mac**: `brew install redis`
- **Linux**: `sudo apt-get install redis-server`

### Step 4: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Set Environment Variables
**Windows (PowerShell):**
```powershell
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/productdb"
$env:REDIS_URL="redis://localhost:6379/0"
$env:CELERY_BROKER_URL="redis://localhost:6379/0"
$env:CELERY_RESULT_BACKEND="redis://localhost:6379/0"
```

**Mac/Linux:**
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/productdb"
export REDIS_URL="redis://localhost:6379/0"
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
```

### Step 6: Initialize Database
```bash
python -c "from app.database import init_db; init_db()"
```

### Step 7: Start Redis (in a separate terminal)
```bash
redis-server
```

### Step 8: Start Celery Worker (in a separate terminal)
```bash
celery -A app.celery_app worker --loglevel=info
```

### Step 9: Start the Web Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 10: Access the Application
Open browser: http://localhost:8000

---

## 🎯 Quick Test

1. **Upload a CSV file:**
   - Go to "Upload CSV" tab
   - Click "Choose File" or drag & drop a CSV file
   - Format: `name,sku,description` (header required)
   - Watch the progress bar update in real-time

2. **View Products:**
   - Go to "Products" tab
   - See imported products with pagination
   - Use filters to search

3. **Test Webhooks:**
   - Go to "Webhooks" tab
   - Add a webhook (use https://webhook.site for testing)
   - Click "Test" to verify it works

---

## ❓ Troubleshooting

### Docker Issues

**Problem**: `docker-compose: command not found`
- **Solution**: Make sure Docker Desktop is installed and running

**Problem**: Port already in use
- **Solution**: Stop other services using ports 8000, 5432, or 6379
- Or change ports in `docker-compose.yml`

**Problem**: Database connection errors
- **Solution**: Wait a few seconds for database to initialize, then restart:
  ```bash
  docker-compose down
  docker-compose up --build
  ```

### Manual Setup Issues

**Problem**: `ModuleNotFoundError`
- **Solution**: Make sure you installed requirements: `pip install -r requirements.txt`

**Problem**: Database connection failed
- **Solution**: 
  - Check PostgreSQL is running: `pg_isready`
  - Verify database exists: `psql -l | grep productdb`
  - Check connection string in environment variables

**Problem**: Redis connection failed
- **Solution**: 
  - Check Redis is running: `redis-cli ping` (should return "PONG")
  - Start Redis: `redis-server`

---

## 📚 More Information

- Full documentation: See `README.md`
- Deployment guide: See `DEPLOYMENT.md`
- Project summary: See `PROJECT_SUMMARY.md`

---

## 🎉 You're Ready!

The application is now running. Start by uploading a CSV file and exploring the features!

