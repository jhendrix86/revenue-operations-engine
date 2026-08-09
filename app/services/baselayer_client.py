"""
Real client for baselayer's income_engine (revenue streams, subscriptions,
billing, payment providers) - authenticates as a service account via
baselayer's own JWT login flow rather than re-implementing billing logic
against Stripe/PayPal directly in this engine.

Revenue-operations-engine's "plan_id" is passed straight through as
baselayer's "stream_id" - each locally-defined SubscriptionPlan is expected
to correspond 1:1 with a revenue stream already created in baselayer.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from app.config import settings


@dataclass
class BaselayerResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaselayerClient:
    def __init__(self):
        self.base_url = settings.baselayer_url.rstrip("/")
        self.service_email = settings.baselayer_service_email
        self.service_password = settings.baselayer_service_password
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.service_email and self.service_password)

    async def _get_token(self) -> Optional[str]:
        if not self.configured:
            return None
        if self._token and self._token_expires_at and datetime.utcnow() < self._token_expires_at:
            return self._token

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"email": self.service_email, "password": self.service_password},
                )
        except httpx.HTTPError as exc:
            logger.error(f"baselayer login request failed: {exc}")
            return None

        if response.status_code != 200:
            logger.error(f"baselayer login failed: {response.status_code} {response.text[:200]}")
            return None

        data = response.json()
        self._token = data["access_token"]
        # refresh a little early rather than racing the real expiry
        expires_in = data.get("expires_in", 300)
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=max(expires_in - 30, 0))
        return self._token

    async def _request(self, method: str, path: str, **kwargs) -> BaselayerResult:
        if not self.configured:
            return BaselayerResult(success=False, error="baselayer is not configured (BASELAYER_URL/BASELAYER_SERVICE_EMAIL/BASELAYER_SERVICE_PASSWORD)")

        token = await self._get_token()
        if token is None:
            return BaselayerResult(success=False, error="baselayer authentication failed")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.request(
                    method, f"{self.base_url}{path}",
                    headers={"Authorization": f"Bearer {token}"},
                    **kwargs,
                )
        except httpx.HTTPError as exc:
            logger.error(f"baselayer request failed: {method} {path}: {exc}")
            return BaselayerResult(success=False, error=f"baselayer request failed: {exc}")

        if response.status_code >= 400:
            return BaselayerResult(success=False, error=f"baselayer returned {response.status_code}: {response.text[:300]}")

        return BaselayerResult(success=True, data=response.json())

    # --- Subscriptions -----------------------------------------------

    async def create_subscription(
        self, customer_id: str, plan_id: str, payment_method: str,
        billing_cycle: str = "monthly", trial_days: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BaselayerResult:
        return await self._request("POST", "/api/v1/subscriptions", json={
            "customer_id": customer_id,
            "stream_id": plan_id,
            "plan_tier": plan_id,
            "billing_cycle": billing_cycle,
            "payment_method": payment_method,
            "trial_days": trial_days,
            "metadata": metadata,
        })

    async def get_subscription(self, customer_id: str, plan_id: str) -> BaselayerResult:
        return await self._request("GET", f"/api/v1/subscriptions/{customer_id}/{plan_id}")

    async def list_customer_subscriptions(self, customer_id: str) -> BaselayerResult:
        return await self._request("GET", f"/api/v1/subscriptions/{customer_id}")

    async def cancel_subscription(
        self, customer_id: str, plan_id: str, reason: str = "Customer request",
        refund_pro_rated: bool = False,
    ) -> BaselayerResult:
        return await self._request("POST", f"/api/v1/subscriptions/{customer_id}/{plan_id}/cancel", json={
            "reason": reason,
            "refund_pro_rated": refund_pro_rated,
        })

    async def update_subscription_plan(self, customer_id: str, plan_id: str, new_plan_id: str) -> BaselayerResult:
        return await self._request("PUT", f"/api/v1/subscriptions/{customer_id}/{plan_id}", json={
            "new_plan_tier": new_plan_id,
        })

    # --- Payments ------------------------------------------------------

    async def process_payment(
        self, amount: float, currency: str, payment_method_token: str,
        customer_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
    ) -> BaselayerResult:
        return await self._request("POST", "/api/v1/providers/payments", json={
            "amount": amount,
            "currency": currency,
            "payment_method_token": payment_method_token,
            "customer_id": customer_id,
            "metadata": metadata,
        })

    async def refund_payment(
        self, transaction_id: str, amount: Optional[float] = None, reason: Optional[str] = None,
    ) -> BaselayerResult:
        return await self._request("POST", "/api/v1/providers/refunds", json={
            "transaction_id": transaction_id,
            "amount": amount,
            "reason": reason,
        })

    async def get_payment_status(self, transaction_id: str) -> BaselayerResult:
        return await self._request("GET", f"/api/v1/providers/payments/{transaction_id}")
