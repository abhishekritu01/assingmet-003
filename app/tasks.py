"""
Celery tasks for asynchronous operations.
"""
import csv
import os
import time
from typing import Dict, List
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.celery_app import celery_app
from app.models import Product, Webhook
from app.config import settings
from app.database import SessionLocal
import httpx
import asyncio
from datetime import datetime




# Create database engine for tasks
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
TaskSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_task_db():
    """Get database session for tasks."""
    db = TaskSessionLocal()
    try:
        yield db
    finally:
        db.close()


@celery_app.task(bind=True, name="import_csv")
def import_csv_task(self, file_path: str, task_id: str):
    """
    Import products from CSV file asynchronously.
    
    Args:
        file_path: Path to the uploaded CSV file
        task_id: Unique task identifier for progress tracking
    
    Returns:
        dict: Import result with statistics
    """
    db = TaskSessionLocal()
    try:
        # Update progress: Parsing CSV
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "processing",
                "progress": 0.0,
                "message": "Parsing CSV file...",
                "total_records": 0,
                "processed_records": 0,
            }
        )
        
        # Read CSV file in chunks for memory efficiency
        chunk_size = settings.CHUNK_SIZE
        total_records = 0
        processed_records = 0
        errors = []
        
        # Count total lines first (approximate)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                total_records = sum(1 for _ in f) - 1  # Subtract header
        except Exception as e:
            errors.append(f"Error counting records: {str(e)}")
            total_records = 0
        
        # Update progress: Validating
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "processing",
                "progress": 0.1,
                "message": "Validating data...",
                "total_records": total_records,
                "processed_records": 0,
            }
        )
        
        # Process CSV in chunks
        chunk_num = 0
        products_to_upsert = []
        
        try:
            # Use pandas for efficient CSV reading
            for chunk in pd.read_csv(
                file_path,
                chunksize=chunk_size,
                dtype=str,
                na_values=['', 'nan', 'None'],
                keep_default_na=False
            ):
                chunk_num += 1
                
                for _, row in chunk.iterrows():
                    try:
                        # Validate required fields
                        sku = str(row.get('sku', '')).strip().lower()
                        name = str(row.get('name', '')).strip()
                        description = str(row.get('description', '')).strip() if pd.notna(row.get('description')) else None
                        
                        if not sku or not name:
                            errors.append(f"Row {processed_records + 1}: Missing required field (SKU or name)")
                            continue
                        
                        # Create or update product
                        product = Product(
                            sku=sku,
                            name=name,
                            description=description if description else None,
                            active=True
                        )
                        products_to_upsert.append(product)
                        
                        # Batch insert/update every chunk_size
                        if len(products_to_upsert) >= chunk_size:
                            _batch_upsert_products(db, products_to_upsert)
                            products_to_upsert = []
                        
                        processed_records += 1
                        
                        # Update progress every 1000 records
                        if processed_records % 1000 == 0:
                            progress = min(0.1 + (processed_records / max(total_records, 1)) * 0.8, 0.9)
                            self.update_state(
                                state="PROCESSING",
                                meta={
                                    "status": "processing",
                                    "progress": progress,
                                    "message": f"Importing products... ({processed_records}/{total_records})",
                                    "total_records": total_records,
                                    "processed_records": processed_records,
                                    "errors": errors[-10:] if errors else None,  # Last 10 errors
                                }
                            )
                    
                    except Exception as e:
                        errors.append(f"Row {processed_records + 1}: {str(e)}")
                        continue
                
                # Commit after each chunk
                db.commit()
        
        except Exception as e:
            errors.append(f"Error reading CSV: {str(e)}")
            db.rollback()
        
        # Insert remaining products
        if products_to_upsert:
            _batch_upsert_products(db, products_to_upsert)
            db.commit()
        
        # Trigger webhooks for product.created event
        _trigger_webhooks(db, "product.created", {"count": processed_records})
        
        # Update progress: Complete
        result = {
            "status": "completed",
            "progress": 1.0,
            "message": f"Import completed successfully! Processed {processed_records} products.",
            "total_records": total_records,
            "processed_records": processed_records,
            "errors": errors if errors else None,
        }
        
        self.update_state(state="SUCCESS", meta=result)
        
        # Clean up uploaded file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
        
        return result
    
    except Exception as e:
        db.rollback()
        error_msg = f"Import failed: {str(e)}"
        self.update_state(
            state="FAILURE",
            meta={
                "status": "failed",
                "progress": 0.0,
                "message": error_msg,
                "errors": [error_msg],
            }
        )
        return {"status": "failed", "message": error_msg, "errors": [error_msg]}
    
    finally:
        db.close()


def _batch_upsert_products(db: Session, products: List[Product]):
    """
    Batch upsert products (insert or update on conflict).
    Uses PostgreSQL's ON CONFLICT for efficient upserts.
    """
    if not products:
        return
    
    try:
        # Use SQLAlchemy's bulk operations with PostgreSQL ON CONFLICT
        from sqlalchemy.dialects.postgresql import insert
        
        values = [
            {
                "sku": p.sku.lower(),
                "name": p.name,
                "description": p.description,
                "active": p.active,
                "updated_at": datetime.utcnow(),
            }
            for p in products
        ]
        
        stmt = insert(Product).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=['sku'],
            set_={
                'name': stmt.excluded.name,
                'description': stmt.excluded.description,
                'active': stmt.excluded.active,
                'updated_at': stmt.excluded.updated_at,
            }
        )
        
        db.execute(stmt)
        db.commit()
    
    except Exception as e:
        db.rollback()
        # Fallback to individual upserts
        for product in products:
            try:
                existing = db.query(Product).filter(func.lower(Product.sku) == product.sku.lower()).first()
                if existing:
                    existing.name = product.name
                    existing.description = product.description
                    existing.active = product.active
                else:
                    db.add(product)
                db.commit()
            except Exception as e2:
                db.rollback()
                continue


def _trigger_webhooks(db: Session, event_type: str, payload: Dict):
    """
    Trigger webhooks for a given event type.
    
    Args:
        db: Database session
        event_type: Type of event
        payload: Data to send to webhooks
    """
    webhooks = db.query(Webhook).filter(
        Webhook.event_type == event_type,
        Webhook.enabled == True
    ).all()
    
    if not webhooks:
        return
    
    # Trigger webhooks asynchronously (fire and forget)
    for webhook in webhooks:
        trigger_webhook_task.delay(str(webhook.id), event_type, payload)


@celery_app.task(name="trigger_webhook")
def trigger_webhook_task(webhook_id: str, event_type: str, payload: Dict):
    """
    Trigger a single webhook asynchronously.
    
    Args:
        webhook_id: Webhook ID
        event_type: Event type
        payload: Payload to send
    """
    db = TaskSessionLocal()
    try:
        from app.models import Webhook
        webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
        
        if not webhook or not webhook.enabled:
            return
        
        start_time = time.time()
        try:
            response = httpx.post(
                str(webhook.url),
                json={
                    "event_type": event_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": payload,
                },
                timeout=10.0,
            )
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Store result (could be saved to a webhook_logs table)
            print(f"Webhook {webhook_id} triggered: {response.status_code} ({response_time:.2f}ms)")
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            print(f"Webhook {webhook_id} failed: {str(e)} ({response_time:.2f}ms)")
    
    finally:
        db.close()


@celery_app.task(name="bulk_delete_products")
def bulk_delete_products_task(self):
    """
    Delete all products from the database.
    
    Returns:
        dict: Deletion result
    """
    db = TaskSessionLocal()
    try:
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "processing",
                "progress": 0.0,
                "message": "Deleting products...",
            }
        )
        
        count = db.query(Product).count()
        db.query(Product).delete()
        db.commit()
        
        # Trigger webhooks
        _trigger_webhooks(db, "product.deleted", {"count": count})
        
        result = {
            "status": "completed",
            "progress": 1.0,
            "message": f"Deleted {count} products successfully.",
            "deleted_count": count,
        }
        
        self.update_state(state="SUCCESS", meta=result)
        return result
    
    except Exception as e:
        db.rollback()
        error_msg = f"Bulk delete failed: {str(e)}"
        self.update_state(
            state="FAILURE",
            meta={
                "status": "failed",
                "progress": 0.0,
                "message": error_msg,
            }
        )
        return {"status": "failed", "message": error_msg}
    
    finally:
        db.close()

