"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProductBase(BaseModel):
    """Base product schema."""
    sku: str = Field(..., min_length=1, max_length=255, description="Stock Keeping Unit")
    name: str = Field(..., min_length=1, max_length=500, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    active: bool = Field(True, description="Whether the product is active")


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class WebhookBase(BaseModel):
    """Base webhook schema."""
    url: HttpUrl = Field(..., description="Webhook URL endpoint")
    event_type: str = Field(..., min_length=1, max_length=100, description="Event type")
    enabled: bool = Field(True, description="Whether the webhook is enabled")


class WebhookCreate(WebhookBase):
    """Schema for creating a webhook."""
    pass


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook."""
    url: Optional[HttpUrl] = None
    event_type: Optional[str] = Field(None, min_length=1, max_length=100)
    enabled: Optional[bool] = None


class WebhookResponse(WebhookBase):
    """Schema for webhook response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WebhookTestResponse(BaseModel):
    """Schema for webhook test response."""
    success: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


class UploadProgressResponse(BaseModel):
    """Schema for upload progress response."""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: float  # 0.0 to 1.0
    message: str
    total_records: Optional[int] = None
    processed_records: Optional[int] = None
    errors: Optional[list[str]] = None

