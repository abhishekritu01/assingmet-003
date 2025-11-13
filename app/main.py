"""
FastAPI main application.
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
import os
import uuid
import aiofiles
from pathlib import Path

from app.database import get_db, init_db
from app.models import Product, Webhook
from app.schemas import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    WebhookCreate, WebhookUpdate, WebhookResponse, WebhookTestResponse,
    UploadProgressResponse
)
from app.tasks import import_csv_task, trigger_webhook_task, bulk_delete_products_task
from app.config import settings
from app.celery_app import celery_app

# Create FastAPI app
app = FastAPI(
    title="Product Importer API",
    description="A scalable web application for importing and managing products from CSV files",
    version="1.0.0"
)

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_progress(self, task_id: str, data: dict):
        """Send progress update to all connected clients."""
        message = {
            "task_id": task_id,
            **data
        }
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    html_file = Path("static/index.html")
    if html_file.exists():
        return FileResponse(html_file)
    return HTMLResponse("<h1>Product Importer API</h1><p>Please create static/index.html</p>")


# ==================== CSV Upload Endpoints ====================

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and import CSV file.
    
    Returns task ID for progress tracking.
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.csv")
    
    # Save uploaded file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds maximum allowed size")
        await f.write(content)
    
    # Start Celery task
    task = import_csv_task.delay(file_path, file_id)
    
    return {"task_id": task.id, "message": "Upload started"}


@app.get("/api/upload/progress/{task_id}")
async def get_upload_progress(task_id: str):
    """
    Get upload progress for a task.
    
    Returns current progress status.
    """
    task = celery_app.AsyncResult(task_id)
    
    if task.state == "PENDING":
        response = {
            "task_id": task_id,
            "status": "pending",
            "progress": 0.0,
            "message": "Task is pending...",
        }
    elif task.state == "PROCESSING":
        response = {
            "task_id": task_id,
            "status": "processing",
            **task.info,
        }
    elif task.state == "SUCCESS":
        response = {
            "task_id": task_id,
            "status": "completed",
            **task.info,
        }
    elif task.state == "FAILURE":
        response = {
            "task_id": task_id,
            "status": "failed",
            "progress": 0.0,
            "message": str(task.info),
            "errors": [str(task.info)],
        }
    else:
        response = {
            "task_id": task_id,
            "status": task.state.lower(),
            "progress": 0.0,
            "message": f"Task state: {task.state}",
        }
    
    return response


@app.websocket("/ws/progress/{task_id}")
async def websocket_progress(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time progress updates.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Get task status
            task = celery_app.AsyncResult(task_id)
            
            if task.state == "PENDING":
                data = {
                    "status": "pending",
                    "progress": 0.0,
                    "message": "Task is pending...",
                }
            elif task.state == "PROCESSING":
                data = {
                    "status": "processing",
                    **task.info,
                }
            elif task.state == "SUCCESS":
                data = {
                    "status": "completed",
                    **task.info,
                }
                await websocket.send_json({"task_id": task_id, **data})
                break
            elif task.state == "FAILURE":
                data = {
                    "status": "failed",
                    "progress": 0.0,
                    "message": str(task.info),
                    "errors": [str(task.info)],
                }
                await websocket.send_json({"task_id": task_id, **data})
                break
            else:
                data = {
                    "status": task.state.lower(),
                    "progress": 0.0,
                    "message": f"Task state: {task.state}",
                }
            
            await websocket.send_json({"task_id": task_id, **data})
            
            # If completed or failed, close connection
            if task.state in ["SUCCESS", "FAILURE"]:
                break
            
            # Wait before next update
            import asyncio
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ==================== Product Endpoints ====================

@app.get("/api/products", response_model=ProductListResponse)
async def list_products(
    skip: int = 0,
    limit: int = 50,
    sku: Optional[str] = None,
    name: Optional[str] = None,
    active: Optional[bool] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List products with pagination and filtering.
    """
    query = db.query(Product)
    
    # Apply filters
    if sku:
        query = query.filter(Product.sku.ilike(f"%{sku}%"))
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if active is not None:
        query = query.filter(Product.active == active)
    if description:
        query = query.filter(Product.description.ilike(f"%{description}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    
    # Calculate total pages
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        total_pages=total_pages,
    )


@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get a single product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@app.post("/api/products", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    # Check if SKU already exists (case-insensitive)
    existing = db.query(Product).filter(func.lower(Product.sku) == product.sku.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product with this SKU already exists")
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Trigger webhooks
    from app.tasks import _trigger_webhooks
    _trigger_webhooks(db, "product.created", {"product_id": str(db_product.id)})
    
    return ProductResponse.from_orm(db_product)


@app.put("/api/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """Update a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    # Trigger webhooks
    from app.tasks import _trigger_webhooks
    _trigger_webhooks(db, "product.updated", {"product_id": str(product.id)})
    
    return ProductResponse.model_validate(product)


@app.delete("/api/products/{product_id}", status_code=204)
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    """Delete a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    
    # Trigger webhooks
    from app.tasks import _trigger_webhooks
    _trigger_webhooks(db, "product.deleted", {"product_id": str(product.id)})
    
    return None


@app.delete("/api/products", status_code=200)
async def bulk_delete_products(db: Session = Depends(get_db)):
    """
    Delete all products (bulk delete).
    Returns task ID for tracking.
    """
    task = bulk_delete_products_task.delay()
    return {"task_id": task.id, "message": "Bulk delete started"}


@app.get("/api/products/bulk-delete/status/{task_id}")
async def get_bulk_delete_status(task_id: str):
    """Get bulk delete task status."""
    task = celery_app.AsyncResult(task_id)
    
    if task.state == "PENDING":
        return {
            "task_id": task_id,
            "status": "pending",
            "progress": 0.0,
            "message": "Task is pending...",
        }
    elif task.state == "PROCESSING":
        return {
            "task_id": task_id,
            "status": "processing",
            **task.info,
        }
    elif task.state == "SUCCESS":
        return {
            "task_id": task_id,
            "status": "completed",
            **task.info,
        }
    elif task.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "failed",
            "progress": 0.0,
            "message": str(task.info),
        }
    else:
        return {
            "task_id": task_id,
            "status": task.state.lower(),
            "progress": 0.0,
            "message": f"Task state: {task.state}",
        }


# ==================== Webhook Endpoints ====================

@app.get("/api/webhooks", response_model=List[WebhookResponse])
async def list_webhooks(db: Session = Depends(get_db)):
    """List all webhooks."""
    webhooks = db.query(Webhook).order_by(Webhook.created_at.desc()).all()
    return [WebhookResponse.model_validate(w) for w in webhooks]


@app.get("/api/webhooks/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(webhook_id: str, db: Session = Depends(get_db)):
    """Get a single webhook by ID."""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return WebhookResponse.model_validate(webhook)


@app.post("/api/webhooks", response_model=WebhookResponse, status_code=201)
async def create_webhook(webhook: WebhookCreate, db: Session = Depends(get_db)):
    """Create a new webhook."""
    db_webhook = Webhook(**webhook.dict())
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return WebhookResponse.from_orm(db_webhook)


@app.put("/api/webhooks/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(webhook_id: str, webhook_update: WebhookUpdate, db: Session = Depends(get_db)):
    """Update a webhook."""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    update_data = webhook_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(webhook, field, value)
    
    db.commit()
    db.refresh(webhook)
    return WebhookResponse.model_validate(webhook)


@app.delete("/api/webhooks/{webhook_id}", status_code=204)
async def delete_webhook(webhook_id: str, db: Session = Depends(get_db)):
    """Delete a webhook."""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    db.delete(webhook)
    db.commit()
    return None


@app.post("/api/webhooks/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(webhook_id: str, db: Session = Depends(get_db)):
    """
    Test a webhook by sending a test event.
    Returns response code and response time.
    """
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if not webhook.enabled:
        return WebhookTestResponse(
            success=False,
            error="Webhook is disabled"
        )
    
    # Trigger webhook asynchronously and get result
    import httpx
    import time
    from datetime import datetime
    
    start_time = time.time()
    try:
        response = httpx.post(
            str(webhook.url),
            json={
                "event_type": "webhook.test",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"message": "Test webhook trigger"},
            },
            timeout=10.0,
        )
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return WebhookTestResponse(
            success=response.is_success,
            status_code=response.status_code,
            response_time_ms=response_time,
        )
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return WebhookTestResponse(
            success=False,
            response_time_ms=response_time,
            error=str(e),
        )

