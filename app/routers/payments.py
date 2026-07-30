"""
Payment router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from loguru import logger

from app.database import get_db
from app.models.payment import Payment, PaymentStatus, PaymentMethod

router = APIRouter()


class CreatePaymentIntentRequest(BaseModel):
    """Request to create payment intent"""
    amount: float
    currency: str = "USD"
    customer_id: str
    description: Optional[str] = None
    payment_method_type: str = "card"
    metadata: Optional[dict] = None


class ConfirmPaymentRequest(BaseModel):
    """Request to confirm payment"""
    payment_id: str
    payment_method_id: str


class RefundRequest(BaseModel):
    """Request to process refund"""
    payment_id: str
    amount: Optional[float] = None
    reason: Optional[str] = None


@router.post("/create-intent")
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a payment intent"""
    try:
        logger.info(f"Creating payment intent for customer {request.customer_id}")
        
        # In production, this would integrate with Stripe/PayPal
        # For now, return a mock response
        payment_intent = {
            "id": "pi_mock_123",
            "amount": int(request.amount * 100),  # Convert to cents
            "currency": request.currency,
            "status": "requires_payment_method",
            "client_secret": "pi_mock_123_secret_xyz",
            "customer_id": request.customer_id
        }
        
        logger.info(f"Payment intent created: {payment_intent['id']}")
        return payment_intent
        
    except Exception as e:
        logger.error(f"Failed to create payment intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm")
async def confirm_payment(
    request: ConfirmPaymentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Confirm a payment"""
    try:
        logger.info(f"Confirming payment {request.payment_id}")
        
        # In production, this would confirm with Stripe/PayPal
        # For now, return a mock response
        payment = {
            "id": request.payment_id,
            "status": "succeeded",
            "amount": 9700,
            "currency": "USD"
        }
        
        logger.info(f"Payment confirmed: {payment['id']}")
        return payment
        
    except Exception as e:
        logger.error(f"Failed to confirm payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refund")
async def process_refund(
    request: RefundRequest,
    db: AsyncSession = Depends(get_db)
):
    """Process a refund"""
    try:
        logger.info(f"Processing refund for payment {request.payment_id}")
        
        # In production, this would process refund with Stripe/PayPal
        # For now, return a mock response
        refund = {
            "id": "re_mock_123",
            "payment_id": request.payment_id,
            "amount": request.amount,
            "status": "succeeded",
            "reason": request.reason
        }
        
        logger.info(f"Refund processed: {refund['id']}")
        return refund
        
    except Exception as e:
        logger.error(f"Failed to process refund: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{payment_id}")
async def get_payment(
    payment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get payment details"""
    try:
        logger.info(f"Getting payment details for {payment_id}")
        
        # In production, this would query from database
        # For now, return a mock response
        payment = {
            "id": payment_id,
            "amount": 9700,
            "currency": "USD",
            "status": "succeeded",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return payment
        
    except Exception as e:
        logger.error(f"Failed to get payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))
