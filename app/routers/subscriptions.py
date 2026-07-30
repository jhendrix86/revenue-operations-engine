"""
Subscription router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from loguru import logger

from app.database import get_db
from app.models.subscription import Subscription, SubscriptionStatus

router = APIRouter()


class CreateSubscriptionRequest(BaseModel):
    """Request to create subscription"""
    customer_id: str
    plan_id: str
    payment_method_id: str
    trial_days: Optional[int] = 0
    metadata: Optional[dict] = None


class UpdateSubscriptionRequest(BaseModel):
    """Request to update subscription"""
    plan_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    metadata: Optional[dict] = None


@router.post("/create")
async def create_subscription(
    request: CreateSubscriptionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a subscription"""
    try:
        logger.info(f"Creating subscription for customer {request.customer_id}")
        
        # Calculate dates
        now = datetime.utcnow()
        current_period_end = now + timedelta(days=30)
        
        if request.trial_days > 0:
            trial_end = now + timedelta(days=request.trial_days)
            status = SubscriptionStatus.TRIALING
        else:
            trial_end = None
            status = SubscriptionStatus.ACTIVE
        
        # In production, this would integrate with Stripe/PayPal
        # For now, return a mock response
        subscription = {
            "id": "sub_mock_123",
            "customer_id": request.customer_id,
            "plan_id": request.plan_id,
            "status": status.value,
            "current_period_start": now.isoformat(),
            "current_period_end": current_period_end.isoformat(),
            "trial_start": now.isoformat() if request.trial_days > 0 else None,
            "trial_end": trial_end.isoformat() if trial_end else None,
            "created_at": now.isoformat()
        }
        
        logger.info(f"Subscription created: {subscription['id']}")
        return subscription
        
    except Exception as e:
        logger.error(f"Failed to create subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    cancel_at_period_end: bool = True,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a subscription"""
    try:
        logger.info(f"Cancelling subscription {subscription_id}")
        
        # In production, this would cancel with Stripe/PayPal
        # For now, return a mock response
        subscription = {
            "id": subscription_id,
            "status": "cancelled" if not cancel_at_period_end else "active",
            "cancel_at_period_end": cancel_at_period_end,
            "cancelled_at": datetime.utcnow().isoformat() if not cancel_at_period_end else None,
            "cancellation_reason": reason
        }
        
        logger.info(f"Subscription cancelled: {subscription_id}")
        return subscription
        
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{subscription_id}/upgrade")
async def upgrade_subscription(
    subscription_id: str,
    plan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Upgrade subscription plan"""
    try:
        logger.info(f"Upgrading subscription {subscription_id} to plan {plan_id}")
        
        # In production, this would upgrade with Stripe/PayPal
        # For now, return a mock response
        subscription = {
            "id": subscription_id,
            "plan_id": plan_id,
            "status": "active",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Subscription upgraded: {subscription_id}")
        return subscription
        
    except Exception as e:
        logger.error(f"Failed to upgrade subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{subscription_id}/downgrade")
async def downgrade_subscription(
    subscription_id: str,
    plan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Downgrade subscription plan"""
    try:
        logger.info(f"Downgrading subscription {subscription_id} to plan {plan_id}")
        
        # In production, this would downgrade with Stripe/PayPal
        # For now, return a mock response
        subscription = {
            "id": subscription_id,
            "plan_id": plan_id,
            "status": "active",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Subscription downgraded: {subscription_id}")
        return subscription
        
    except Exception as e:
        logger.error(f"Failed to downgrade subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{subscription_id}")
async def get_subscription(
    subscription_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get subscription details"""
    try:
        logger.info(f"Getting subscription details for {subscription_id}")
        
        # In production, this would query from database
        # For now, return a mock response
        subscription = {
            "id": subscription_id,
            "customer_id": "cust_123",
            "plan_id": "standard",
            "status": "active",
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        return subscription
        
    except Exception as e:
        logger.error(f"Failed to get subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer/{customer_id}")
async def get_customer_subscriptions(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all subscriptions for a customer"""
    try:
        logger.info(f"Getting subscriptions for customer {customer_id}")
        
        # In production, this would query from database
        # For now, return a mock response
        subscriptions = [
            {
                "id": "sub_mock_123",
                "customer_id": customer_id,
                "plan_id": "standard",
                "status": "active"
            }
        ]
        
        return subscriptions
        
    except Exception as e:
        logger.error(f"Failed to get customer subscriptions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
