"""
Payment models
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration"""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"


class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    
    # Gateway-specific fields
    stripe_payment_intent_id = Column(String, unique=True, nullable=True)
    paypal_order_id = Column(String, unique=True, nullable=True)
    
    # Metadata
    description = Column(String, nullable=True)
    extra_metadata = Column(String, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment {self.id} - {self.status} - {self.amount} {self.currency}>"


class CustomerPaymentMethod(Base):
    """Customer payment method model"""
    __tablename__ = "payment_methods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    type = Column(Enum(PaymentMethod), nullable=False)
    
    # Card details (encrypted)
    card_last4 = Column(String(4), nullable=True)
    card_brand = Column(String(20), nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)
    
    # Gateway tokens
    stripe_payment_method_id = Column(String, unique=True, nullable=True)
    paypal_payment_method_id = Column(String, unique=True, nullable=True)
    
    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="payment_methods")
    
    def __repr__(self):
        return f"<CustomerPaymentMethod {self.id} - {self.type}>"
