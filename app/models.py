"""
Database models for Product and Webhook.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Product(Base):
    """
    Product model representing a product in the system.
    
    Attributes:
        id: Primary key (UUID)
        sku: Stock Keeping Unit (unique, case-insensitive)
        name: Product name
        description: Product description
        active: Whether the product is active (default: True)
        created_at: Timestamp when product was created
        updated_at: Timestamp when product was last updated
    """
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Product(sku='{self.sku}', name='{self.name}', active={self.active})>"
    
    def to_dict(self):
        """Convert product to dictionary."""
        return {
            "id": str(self.id),
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Webhook(Base):
    """
    Webhook model for configuring webhook endpoints.
    
    Attributes:
        id: Primary key (UUID)
        url: Webhook URL endpoint
        event_type: Type of event that triggers the webhook
        enabled: Whether the webhook is enabled (default: True)
        created_at: Timestamp when webhook was created
        updated_at: Timestamp when webhook was last updated
    """
    __tablename__ = "webhooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String(500), nullable=False)
    event_type = Column(String(100), nullable=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Webhook(url='{self.url}', event_type='{self.event_type}', enabled={self.enabled})>"
    
    def to_dict(self):
        """Convert webhook to dictionary."""
        return {
            "id": str(self.id),
            "url": self.url,
            "event_type": self.event_type,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

