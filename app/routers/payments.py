"""
Payment router

Calls baselayer's real income_engine payment provider manager rather than
Stripe/PayPal directly or a local mock. baselayer has no separate
"payment intent" concept (Stripe's two-step create-then-confirm flow) - it
processes payments in one call - so create_payment_intent processes the
payment immediately and confirm_payment simply re-fetches its current
status, rather than performing a second real action.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from app.services.baselayer_client import BaselayerClient

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


def _result_or_error(result):
    if result.success:
        return result.data
    status_code = 404 if "not found" in (result.error or "").lower() else 400
    raise HTTPException(status_code=status_code, detail=result.error)


@router.post("/create-intent")
async def create_payment_intent(request: CreatePaymentIntentRequest):
    """Process a payment via baselayer"""
    logger.info(f"Processing payment for customer {request.customer_id}")

    client = BaselayerClient()
    result = await client.process_payment(
        amount=request.amount,
        currency=request.currency,
        payment_method_token=request.payment_method_type,
        customer_id=request.customer_id,
        metadata={**(request.metadata or {}), "description": request.description},
    )
    return _result_or_error(result)


@router.post("/confirm")
async def confirm_payment(request: ConfirmPaymentRequest):
    """
    Re-check a payment's status.

    baselayer processes payments in a single call (no separate
    create-then-confirm step like Stripe's PaymentIntent flow), so this
    doesn't perform a second action - it reports the real current status of
    the payment created_payment_intent already processed.
    """
    client = BaselayerClient()
    result = await client.get_payment_status(request.payment_id)
    return _result_or_error(result)


@router.post("/refund")
async def process_refund(request: RefundRequest):
    """Process a refund via baselayer"""
    logger.info(f"Processing refund for payment {request.payment_id}")

    client = BaselayerClient()
    result = await client.refund_payment(
        transaction_id=request.payment_id,
        amount=request.amount,
        reason=request.reason,
    )
    return _result_or_error(result)


@router.get("/{payment_id}")
async def get_payment(payment_id: str):
    """Get payment status from baselayer"""
    client = BaselayerClient()
    result = await client.get_payment_status(payment_id)
    return _result_or_error(result)
