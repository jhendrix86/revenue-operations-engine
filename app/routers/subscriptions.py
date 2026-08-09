"""
Subscription router

Calls baselayer's real income_engine subscription manager rather than
Stripe/PayPal directly or a local mock - baselayer is the system of record
here, so these endpoints are a thin, honest proxy: real success data or a
clear failure reason (baselayer unreachable/unconfigured, or a real
validation error from baselayer itself), never a fabricated response.
"local plan_id" is passed straight through as baselayer's revenue stream id.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from app.services.baselayer_client import BaselayerClient

router = APIRouter()


class CreateSubscriptionRequest(BaseModel):
    """Request to create subscription"""
    customer_id: str
    plan_id: str
    payment_method_id: str
    billing_cycle: str = "monthly"
    trial_days: Optional[int] = 0
    metadata: Optional[dict] = None


class UpdateSubscriptionRequest(BaseModel):
    """Request to update subscription"""
    plan_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    metadata: Optional[dict] = None


def _result_or_error(result, not_found_detail: Optional[str] = None):
    if result.success:
        return result.data
    status_code = 404 if not_found_detail and "not found" in (result.error or "").lower() else 400
    raise HTTPException(status_code=status_code, detail=result.error)


@router.post("/create")
async def create_subscription(request: CreateSubscriptionRequest):
    """Create a subscription via baselayer"""
    logger.info(f"Creating subscription for customer {request.customer_id}, plan {request.plan_id}")

    client = BaselayerClient()
    result = await client.create_subscription(
        customer_id=request.customer_id,
        plan_id=request.plan_id,
        payment_method=request.payment_method_id,
        billing_cycle=request.billing_cycle,
        trial_days=request.trial_days or 0,
        metadata=request.metadata,
    )
    return _result_or_error(result)


@router.post("/{customer_id}/{plan_id}/cancel")
async def cancel_subscription(
    customer_id: str,
    plan_id: str,
    reason: Optional[str] = None,
):
    """Cancel a subscription via baselayer"""
    logger.info(f"Cancelling subscription for customer {customer_id}, plan {plan_id}")

    client = BaselayerClient()
    result = await client.cancel_subscription(
        customer_id=customer_id,
        plan_id=plan_id,
        reason=reason or "Customer request",
    )
    return _result_or_error(result)


@router.put("/{customer_id}/{plan_id}")
async def change_subscription_plan(
    customer_id: str,
    plan_id: str,
    new_plan_id: str,
):
    """Upgrade or downgrade a subscription's plan via baselayer (proration handled by baselayer)"""
    logger.info(f"Changing subscription plan for customer {customer_id}: {plan_id} -> {new_plan_id}")

    client = BaselayerClient()
    result = await client.update_subscription_plan(
        customer_id=customer_id, plan_id=plan_id, new_plan_id=new_plan_id,
    )
    return _result_or_error(result)


@router.get("/{customer_id}/{plan_id}")
async def get_subscription(customer_id: str, plan_id: str):
    """Get subscription details from baselayer"""
    client = BaselayerClient()
    result = await client.get_subscription(customer_id, plan_id)
    return _result_or_error(result, not_found_detail="Subscription not found")


@router.get("/customer/{customer_id}")
async def get_customer_subscriptions(customer_id: str):
    """Get all subscriptions for a customer from baselayer"""
    client = BaselayerClient()
    result = await client.list_customer_subscriptions(customer_id)
    return _result_or_error(result)
