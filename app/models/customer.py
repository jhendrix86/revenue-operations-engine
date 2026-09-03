"""
Customer models
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.models.tenant_base import TenantBase


class Customer(TenantBase, Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Contact information
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(2), nullable=True)
    
    # Tax
    tax_id = Column(String(50), nullable=True)
    tax_exempt = Column(Boolean, default=False)
    
    # Gateway IDs
    stripe_customer_id = Column(String, unique=True, nullable=True)
    paypal_customer_id = Column(String, unique=True, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    extra_metadata = Column(String, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = relationship("Payment", back_populates="customer")
    payment_methods = relationship("CustomerPaymentMethod", back_populates="customer")
    subscriptions = relationship("Subscription", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer {self.id} - {self.email}>"
