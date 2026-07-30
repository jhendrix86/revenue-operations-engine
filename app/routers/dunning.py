"""
Dunning management router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from loguru import logger

from app.database import get_db

router = APIRouter()


@router.get("/failed-payments")
async def get_failed_payments(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get failed payments"""
    try:
        logger.info("Getting failed payments")
        
        # In production, this would query from database
        # For now, return a mock response
        failed_payments = [
            {
                "payment_id": "pay_failed_001",
                "customer_id": "cust_123",
                "subscription_id": "sub_123",
                "amount": 97.0,
                "currency": "USD",
                "failed_at": datetime.utcnow().isoformat(),
                "retry_count": 2,
                "last_retry_at": (datetime.utcnow() - timedelta(days=3)).isoformat(),
                "next_retry_at": (datetime.utcnow() + timedelta(days=4)).isoformat()
            },
            {
                "payment_id": "pay_failed_002",
                "customer_id": "cust_456",
                "subscription_id": "sub_456",
                "amount": 147.0,
                "currency": "USD",
                "failed_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "retry_count": 1,
                "last_retry_at": None,
                "next_retry_at": (datetime.utcnow() + timedelta(days=2)).isoformat()
            }
        ]
        
        return {
            "total": len(failed_payments),
            "failed_payments": failed_payments,
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get failed payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retry/{payment_id}")
async def retry_payment(
    payment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed payment"""
    try:
        logger.info(f"Retrying payment {payment_id}")
        
        # In production, this would retry with Stripe/PayPal
        # For now, return a mock response
        result = {
            "payment_id": payment_id,
            "status": "processing",
            "retry_count": 3,
            "retried_at": datetime.utcnow().isoformat(),
            "next_retry_at": (datetime.utcnow() + timedelta(days=7)).isoformat() if False else None
        }
        
        logger.info(f"Payment retry initiated: {payment_id}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to retry payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/escalate/{customer_id}")
async def escalate_dunning(
    customer_id: str,
    reason: str,
    db: AsyncSession = Depends(get_db)
):
    """Escalate dunning process for manual review"""
    try:
        logger.info(f"Escalating dunning for customer {customer_id}")
        
        # In production, this would create a support ticket
        # For now, return a mock response
        escalation = {
            "customer_id": customer_id,
            "escalation_id": "esc_123",
            "status": "pending_review",
            "reason": reason,
            "escalated_at": datetime.utcnow().isoformat(),
            "assigned_to": "finance-team",
            "priority": "high"
        }
        
        logger.info(f"Dunning escalated for customer {customer_id}")
        return escalation
        
    except Exception as e:
        logger.error(f"Failed to escalate dunning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_dunning_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get dunning statistics"""
    try:
        logger.info("Getting dunning statistics")
        
        # In production, this would calculate from database
        # For now, return a mock response
        stats = {
            "total_failed_payments": 15,
            "pending_retry": 8,
            "escalated": 3,
            "recovered": 4,
            "lost": 5,
            "recovery_rate": 26.7,  # percentage
            "average_recovery_time": 5.2,  # days
            "revenue_at_risk": 1455.0,
            "by_retry_count": {
                "1": 8,
                "2": 5,
                "3": 2
            },
            "by_reason": {
                "insufficient_funds": 7,
                "card_declined": 5,
                "expired_card": 3
            }
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get dunning stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
