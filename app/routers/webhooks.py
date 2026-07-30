"""
Webhook handlers for payment gateways
"""

from fastapi import APIRouter, Request, HTTPException, Header
from loguru import logger
import hmac
import hashlib

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """Handle Stripe webhooks"""
    try:
        logger.info("Received Stripe webhook")
        
        # In production, verify webhook signature
        # webhook_secret = settings.stripe_webhook_secret
        # payload = await request.body()
        # sig_header = stripe_signature
        # event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        
        # For now, just log the event
        payload = await request.json()
        event_type = payload.get("type", "unknown")
        logger.info(f"Stripe webhook event: {event_type}")
        
        # Handle different event types
        if event_type == "payment_intent.succeeded":
            await handle_payment_succeeded(payload)
        elif event_type == "payment_intent.payment_failed":
            await handle_payment_failed(payload)
        elif event_type == "customer.subscription.created":
            await handle_subscription_created(payload)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(payload)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(payload)
        elif event_type == "invoice.payment_succeeded":
            await handle_invoice_payment_succeeded(payload)
        elif event_type == "invoice.payment_failed":
            await handle_invoice_payment_failed(payload)
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Failed to process Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paypal")
async def paypal_webhook(
    request: Request,
    paypal_transmission_id: str = Header(None, alias="PAYPAL-TRANSMISSION-ID"),
    paypal_cert_url: str = Header(None, alias="PAYPAL-CERT-URL"),
    paypal_auth_algo: str = Header(None, alias="PAYPAL-AUTH-ALGO"),
    paypal_timestamp: str = Header(None, alias="PAYPAL-TIMESTAMP"),
    paypal_signature: str = Header(None, alias="PAYPAL-SIGNATURE")
):
    """Handle PayPal webhooks"""
    try:
        logger.info("Received PayPal webhook")
        
        # In production, verify webhook signature
        # For now, just log the event
        payload = await request.json()
        event_type = payload.get("event_type", "unknown")
        logger.info(f"PayPal webhook event: {event_type}")
        
        # Handle different event types
        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            await handle_paypal_payment_completed(payload)
        elif event_type == "PAYMENT.CAPTURE.DENIED":
            await handle_paypal_payment_denied(payload)
        elif event_type == "BILLING.SUBSCRIPTION.CREATED":
            await handle_paypal_subscription_created(payload)
        elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
            await handle_paypal_subscription_cancelled(payload)
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Failed to process PayPal webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Stripe webhook handlers
async def handle_payment_succeeded(payload: dict):
    """Handle successful payment"""
    logger.info(f"Payment succeeded: {payload.get('data', {}).get('object', {}).get('id')}")
    # In production, update database, emit events


async def handle_payment_failed(payload: dict):
    """Handle failed payment"""
    logger.warning(f"Payment failed: {payload.get('data', {}).get('object', {}).get('id')}")
    # In production, trigger dunning process


async def handle_subscription_created(payload: dict):
    """Handle subscription creation"""
    logger.info(f"Subscription created: {payload.get('data', {}).get('object', {}).get('id')}")
    # In production, update database, emit events


async def handle_subscription_updated(payload: dict):
    """Handle subscription update"""
    logger.info(f"Subscription updated: {payload.get('data', {}).get('object', {}).get('id')}")
    # In production, update database


async def handle_subscription_deleted(payload: dict):
    """Handle subscription deletion"""
    logger.info(f"Subscription deleted: {payload.get('data', {}).get('object', {}).get('id')}")
    # In production, update database, emit events


async def handle_invoice_payment_succeeded(payload: dict):
    """Handle successful invoice payment"""
    logger.info(f"Invoice payment succeeded: {payload.get('data', {}).get('object', {}).get('id')}")
    # In production, update invoice status, recognize revenue


async def handle_invoice_payment_failed(payload: dict):
    """Handle failed invoice payment"""
    logger.warning(f"Invoice payment failed: {payload.get('data', {}).get('object', {}).get('id')}")
    # In production, trigger dunning process


# PayPal webhook handlers
async def handle_paypal_payment_completed(payload: dict):
    """Handle PayPal payment completion"""
    logger.info(f"PayPal payment completed: {payload.get('resource', {}).get('id')}")
    # In production, update database, emit events


async def handle_paypal_payment_denied(payload: dict):
    """Handle PayPal payment denial"""
    logger.warning(f"PayPal payment denied: {payload.get('resource', {}).get('id')}")
    # In production, trigger dunning process


async def handle_paypal_subscription_created(payload: dict):
    """Handle PayPal subscription creation"""
    logger.info(f"PayPal subscription created: {payload.get('resource', {}).get('id')}")
    # In production, update database, emit events


async def handle_paypal_subscription_cancelled(payload: dict):
    """Handle PayPal subscription cancellation"""
    logger.info(f"PayPal subscription cancelled: {payload.get('resource', {}).get('id')}")
    # In production, update database, emit events
