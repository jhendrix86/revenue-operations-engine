"""
Invoice router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from loguru import logger

from app.database import get_db
from app.models.invoice import Invoice, InvoiceStatus

router = APIRouter()


class CreateInvoiceRequest(BaseModel):
    """Request to create invoice"""
    customer_id: str
    subscription_id: Optional[str] = None
    items: List[dict]
    due_date: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None


class InvoiceItem(BaseModel):
    """Invoice item"""
    description: str
    quantity: int = 1
    unit_price: float
    tax_rate: float = 0.0


@router.post("/create")
async def create_invoice(
    request: CreateInvoiceRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create an invoice"""
    try:
        logger.info(f"Creating invoice for customer {request.customer_id}")
        
        # Calculate totals
        subtotal = sum(item['quantity'] * item['unit_price'] for item in request.items)
        tax = sum(item['quantity'] * item['unit_price'] * item.get('tax_rate', 0.0) for item in request.items)
        total = subtotal + tax
        
        # Generate invoice number
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{hash(request.customer_id) % 10000:04d}"
        
        # Set due date
        due_date = request.due_date or (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        # In production, this would save to database
        # For now, return a mock response
        invoice = {
            "id": "inv_mock_123",
            "invoice_number": invoice_number,
            "customer_id": request.customer_id,
            "subscription_id": request.subscription_id,
            "status": InvoiceStatus.DRAFT.value,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "currency": "USD",
            "due_date": due_date,
            "items": request.items,
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Invoice created: {invoice_number}")
        return invoice
        
    except Exception as e:
        logger.error(f"Failed to create invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{invoice_id}/send")
async def send_invoice(
    invoice_id: str,
    email: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Send invoice to customer"""
    try:
        logger.info(f"Sending invoice {invoice_id}")
        
        # In production, this would send via email
        # For now, return a mock response
        invoice = {
            "id": invoice_id,
            "status": "pending",
            "sent_at": datetime.utcnow().isoformat(),
            "email": email
        }
        
        logger.info(f"Invoice sent: {invoice_id}")
        return invoice
        
    except Exception as e:
        logger.error(f"Failed to send invoice: {e}")
        raise HTTPException(status_code=500, detail(str(e))


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get invoice details"""
    try:
        logger.info(f"Getting invoice details for {invoice_id}")
        
        # In production, this would query from database
        # For now, return a mock response
        invoice = {
            "id": invoice_id,
            "invoice_number": "INV-20240120-1234",
            "customer_id": "cust_123",
            "status": "pending",
            "subtotal": 97.0,
            "tax": 0.0,
            "total": 97.0,
            "currency": "USD",
            "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return invoice
        
    except Exception as e:
        logger.error(f"Failed to get invoice: {e}")
        raise HTTPException(status_code=500, detail(str(e))


@router.get("/customer/{customer_id}")
async def get_customer_invoices(
    customer_id: str,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all invoices for a customer"""
    try:
        logger.info(f"Getting invoices for customer {customer_id}")
        
        # In production, this would query from database
        # For now, return a mock response
        invoices = [
            {
                "id": "inv_mock_123",
                "invoice_number": "INV-20240120-1234",
                "customer_id": customer_id,
                "status": "paid",
                "total": 97.0,
                "currency": "USD"
            }
        ]
        
        return invoices
        
    except Exception as e:
        logger.error(f"Failed to get customer invoices: {e}")
        raise HTTPException(status_code=500, detail(str(e))


@router.post("/{invoice_id}/mark-paid")
async def mark_invoice_paid(
    invoice_id: str,
    payment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Mark invoice as paid"""
    try:
        logger.info(f"Marking invoice {invoice_id} as paid")
        
        # In production, this would update database
        # For now, return a mock response
        invoice = {
            "id": invoice_id,
            "status": "paid",
            "paid_at": datetime.utcnow().isoformat(),
            "payment_id": payment_id
        }
        
        logger.info(f"Invoice marked as paid: {invoice_id}")
        return invoice
        
    except Exception as e:
        logger.error(f"Failed to mark invoice as paid: {e}")
        raise HTTPException(status_code=500, detail(str(e))
