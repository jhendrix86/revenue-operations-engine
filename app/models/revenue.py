"""
Revenue recognition models
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class RevenueType(str, enum.Enum):
    """Revenue type enumeration"""
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class RevenueRecord(Base):
    """Revenue record model"""
    __tablename__ = "revenue_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)
    
    # Revenue details
    revenue_type = Column(Enum(RevenueType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    
    # Recognition
    recognized_amount = Column(Float, nullable=False, default=0.0)
    recognized_date = Column(DateTime, nullable=True)
    
    # Period
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    
    # Status
    is_fully_recognized = Column(Boolean, default=False)
    
    # Metadata
    metadata = Column(String, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RevenueRecord {self.id} - {self.revenue_type} - {self.amount} {self.currency}>"


class RevenueRecognition(Base):
    """Revenue recognition schedule model"""
    __tablename__ = "revenue_recognition"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revenue_record_id = Column(UUID(as_uuid=True), ForeignKey("revenue_records.id"), nullable=False)
    
    # Recognition details
    amount = Column(Float, nullable=False)
    recognition_date = Column(DateTime, nullable=False)
    
    # Status
    is_recognized = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RevenueRecognition {self.id} - {self.amount} on {self.recognition_date}>"
