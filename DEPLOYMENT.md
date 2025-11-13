# Deployment Guide

This document provides detailed instructions for deploying the Product Importer application to various platforms.

## Table of Contents

1. [Heroku Deployment](#heroku-deployment)
2. [Render Deployment](#render-deployment)
3. [AWS Deployment](#aws-deployment)
4. [GCP Deployment](#gcp-deployment)
5. [Docker Production](#docker-production)

## Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Heroku account
- Git repository

### Steps

1. **Login to Heroku**:
   ```bash
   heroku login
   ```

2. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL Addon**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Add Redis Addon**:
   ```bash
   heroku addons:create heroku-redis:mini
   ```

5. **Set Environment Variables**:
   ```bash
   heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL)
   heroku config:set REDIS_URL=$(heroku config:get REDIS_URL)
   heroku config:set CELERY_BROKER_URL=$(heroku config:get REDIS_URL)
   heroku config:set CELERY_RESULT_BACKEND=$(heroku config:get REDIS_URL)
   heroku config:set UPLOAD_DIR=uploads
   heroku config:set MAX_UPLOAD_SIZE=524288000
   heroku config:set CHUNK_SIZE=1000
   ```

6. **Create Procfile**:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   worker: celery -A app.celery_app worker --loglevel=info
   ```

7. **Deploy**:
   ```bash
   git push heroku main
   ```

8. **Scale Workers**:
   ```bash
   heroku ps:scale worker=1
   ```

## Render Deployment

### Prerequisites
- Render account
- Git repository

### Steps

1. **Create Web Service**:
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Configure:
     - **Name**: product-importer
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Add PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Note the connection string

3. **Add Redis Instance**:
   - Click "New +" → "Redis"
   - Note the connection string

4. **Configure Environment Variables**:
   - In Web Service settings, add:
     - `DATABASE_URL`: From PostgreSQL service
     - `REDIS_URL`: From Redis service
     - `CELERY_BROKER_URL`: Same as REDIS_URL
     - `CELERY_RESULT_BACKEND`: Same as REDIS_URL
     - `UPLOAD_DIR`: uploads
     - `MAX_UPLOAD_SIZE`: 524288000
     - `CHUNK_SIZE`: 1000

5. **Create Background Worker**:
   - Click "New +" → "Background Worker"
   - Connect same repository
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `celery -A app.celery_app worker --loglevel=info`
   - Add same environment variables

6. **Deploy**:
   - Render will automatically deploy on git push

## AWS Deployment

### Option 1: ECS (Elastic Container Service)

1. **Build Docker Image**:
   ```bash
   docker build -t product-importer .
   ```

2. **Push to ECR**:
   ```bash
   aws ecr create-repository --repository-name product-importer
   docker tag product-importer:latest <account-id>.dkr.ecr.<region>.amazonaws.com/product-importer:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/product-importer:latest
   ```

3. **Create ECS Task Definition**:
   - Use the pushed image
   - Set environment variables
   - Configure ports (8000)

4. **Create RDS PostgreSQL Instance**:
   - Use RDS PostgreSQL
   - Note connection string

5. **Create ElastiCache Redis Instance**:
   - Use ElastiCache Redis
   - Note connection string

6. **Create ECS Service**:
   - Use task definition
   - Configure load balancer
   - Set environment variables

### Option 2: Elastic Beanstalk

1. **Install EB CLI**:
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**:
   ```bash
   eb init -p python-3.11 product-importer
   ```

3. **Create Environment**:
   ```bash
   eb create product-importer-env
   ```

4. **Configure Environment Variables**:
   ```bash
   eb setenv DATABASE_URL=<rds-url> REDIS_URL=<elasticache-url>
   ```

## GCP Deployment

### Option 1: Cloud Run

1. **Build Container**:
   ```bash
   gcloud builds submit --tag gcr.io/<project-id>/product-importer
   ```

2. **Deploy Web Service**:
   ```bash
   gcloud run deploy product-importer-web \
     --image gcr.io/<project-id>/product-importer \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DATABASE_URL=<cloud-sql-url>,REDIS_URL=<memorystore-url>
   ```

3. **Deploy Worker Service**:
   ```bash
   gcloud run jobs create product-importer-worker \
     --image gcr.io/<project-id>/product-importer \
     --command celery \
     --args "-A,app.celery_app,worker,--loglevel=info"
   ```

4. **Create Cloud SQL PostgreSQL**:
   - Use Cloud SQL
   - Note connection string

5. **Create Memorystore Redis**:
   - Use Memorystore
   - Note connection string

## Docker Production

### Using Docker Compose

1. **Update docker-compose.yml for production**:
   ```yaml
   version: '3.8'
   
   services:
     web:
       build: .
       command: uvicorn app.main:app --host 0.0.0.0 --port 8000
       environment:
         - DATABASE_URL=${DATABASE_URL}
         - REDIS_URL=${REDIS_URL}
       restart: always
   
     celery:
       build: .
       command: celery -A app.celery_app worker --loglevel=info
       environment:
         - DATABASE_URL=${DATABASE_URL}
         - REDIS_URL=${REDIS_URL}
       restart: always
   ```

2. **Deploy**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/productdb` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://localhost:6379/0` |
| `UPLOAD_DIR` | Directory for uploads | `uploads` |
| `MAX_UPLOAD_SIZE` | Maximum upload size in bytes | `524288000` (500MB) |
| `CHUNK_SIZE` | Records per chunk | `1000` |

## Post-Deployment Checklist

- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Celery worker running
- [ ] Web service accessible
- [ ] Health check endpoint responding
- [ ] File uploads working
- [ ] Webhooks configured and tested
- [ ] Monitoring/logging set up

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify DATABASE_URL is correct
   - Check database is accessible
   - Verify network security groups

2. **Celery Not Processing Tasks**:
   - Verify worker is running
   - Check Redis connection
   - Verify CELERY_BROKER_URL

3. **Upload Timeouts**:
   - Ensure Celery worker is running
   - Check task is being queued
   - Verify Redis connection

4. **Memory Issues**:
   - Increase container memory
   - Reduce CHUNK_SIZE
   - Monitor resource usage

