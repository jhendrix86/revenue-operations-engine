"""
Invoice models
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base
from app.models.tenant_base import TenantBase


class InvoiceStatus(str, enum.Enum):
    """Invoice status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class Invoice(TenantBase, Base):
    """Invoice model"""
    __tablename__ = "invoices"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(Uuid(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    subscription_id = Column(Uuid(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    
    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Amounts
    subtotal = Column(Float, nullable=False, default=0.0)
    tax = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    currency = Column(String(3), nullable=False, default="USD")
    
    # Due date
    due_date = Column(DateTime, nullable=True)
    
    # Payment
    paid_at = Column(DateTime, nullable=True)
    payment_id = Column(Uuid(as_uuid=True), ForeignKey("payments.id"), nullable=True)
    
    # Gateway IDs
    stripe_invoice_id = Column(String, unique=True, nullable=True)
    paypal_invoice_id = Column(String, unique=True, nullable=True)
    
    # Email
    sent_at = Column(DateTime, nullable=True)
    email = Column(String(255), nullable=True)
    
    # Notes
    notes = Column(String(1000), nullable=True)
    
    # Metadata
    extra_metadata = Column(String, nullable=True)  # JSON string

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")
    payment = relationship("Payment")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.status} - {self.total} {self.currency}>"


class InvoiceItem(TenantBase, Base):
    """Invoice item model"""
    __tablename__ = "invoice_items"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(Uuid(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    
    # Item details
    description = Column(String(500), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    
    # Tax
    tax_amount = Column(Float, nullable=False, default=0.0)
    tax_rate = Column(Float, nullable=False, default=0.0)
    
    # Metadata
    extra_metadata = Column(String, nullable=True)  # JSON string

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    
    def __repr__(self):
        return f"<InvoiceItem {self.description} - {self.amount}>"
