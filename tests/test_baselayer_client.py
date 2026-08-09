import httpx
import pytest
import respx

from app.services.baselayer_client import BaselayerClient
from app.config import Settings


def make_client(monkeypatch, configured=True):
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "baselayer_url", "http://baselayer.test")
    monkeypatch.setattr(config_module.settings, "baselayer_service_email", "svc@example.com" if configured else "")
    monkeypatch.setattr(config_module.settings, "baselayer_service_password", "secret" if configured else "")
    return BaselayerClient()


class TestNotConfigured:
    @pytest.mark.asyncio
    async def test_reports_honest_failure_when_not_configured(self, monkeypatch):
        client = make_client(monkeypatch, configured=False)

        result = await client.get_subscription("cust_1", "plan_1")

        assert result.success is False
        assert "not configured" in result.error


class TestAuthentication:
    @pytest.mark.asyncio
    @respx.mock
    async def test_reports_honest_failure_when_login_fails(self, monkeypatch):
        client = make_client(monkeypatch)
        respx.post("http://baselayer.test/api/v1/auth/login").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid email or password"})
        )

        result = await client.get_subscription("cust_1", "plan_1")

        assert result.success is False
        assert "authentication failed" in result.error

    @pytest.mark.asyncio
    @respx.mock
    async def test_reuses_cached_token_across_calls(self, monkeypatch):
        client = make_client(monkeypatch)
        login_route = respx.post("http://baselayer.test/api/v1/auth/login").mock(
            return_value=httpx.Response(200, json={"access_token": "tok_abc", "expires_in": 3600})
        )
        respx.get("http://baselayer.test/api/v1/subscriptions/cust_1/plan_1").mock(
            return_value=httpx.Response(200, json={"customer_id": "cust_1"})
        )

        await client.get_subscription("cust_1", "plan_1")
        await client.get_subscription("cust_1", "plan_1")

        assert login_route.call_count == 1


class TestSubscriptions:
    @pytest.mark.asyncio
    @respx.mock
    async def test_create_subscription_success(self, monkeypatch):
        client = make_client(monkeypatch)
        respx.post("http://baselayer.test/api/v1/auth/login").mock(
            return_value=httpx.Response(200, json={"access_token": "tok_abc", "expires_in": 3600})
        )
        route = respx.post("http://baselayer.test/api/v1/subscriptions").mock(
            return_value=httpx.Response(200, json={"subscription_id": "sub_1", "status": "active"})
        )

        result = await client.create_subscription(
            customer_id="cust_1", plan_id="plan_pro", payment_method="pm_1",
        )

        assert result.success is True
        assert result.data["subscription_id"] == "sub_1"
        request = route.calls.last.request
        assert request.headers["Authorization"] == "Bearer tok_abc"

    @pytest.mark.asyncio
    @respx.mock
    async def test_create_subscription_reports_baselayer_validation_error(self, monkeypatch):
        client = make_client(monkeypatch)
        respx.post("http://baselayer.test/api/v1/auth/login").mock(
            return_value=httpx.Response(200, json={"access_token": "tok_abc", "expires_in": 3600})
        )
        respx.post("http://baselayer.test/api/v1/subscriptions").mock(
            return_value=httpx.Response(400, text='{"detail":"Customer already has an active subscription"}')
        )

        result = await client.create_subscription(
            customer_id="cust_1", plan_id="plan_pro", payment_method="pm_1",
        )

        assert result.success is False
        assert "400" in result.error


class TestPayments:
    @pytest.mark.asyncio
    @respx.mock
    async def test_process_payment_success(self, monkeypatch):
        client = make_client(monkeypatch)
        respx.post("http://baselayer.test/api/v1/auth/login").mock(
            return_value=httpx.Response(200, json={"access_token": "tok_abc", "expires_in": 3600})
        )
        respx.post("http://baselayer.test/api/v1/providers/payments").mock(
            return_value=httpx.Response(200, json={"transaction_id": "txn_1", "status": "completed"})
        )

        result = await client.process_payment(amount=29.99, currency="USD", payment_method_token="card")

        assert result.success is True
        assert result.data["transaction_id"] == "txn_1"

    @pytest.mark.asyncio
    @respx.mock
    async def test_refund_payment_success(self, monkeypatch):
        client = make_client(monkeypatch)
        respx.post("http://baselayer.test/api/v1/auth/login").mock(
            return_value=httpx.Response(200, json={"access_token": "tok_abc", "expires_in": 3600})
        )
        respx.post("http://baselayer.test/api/v1/providers/refunds").mock(
            return_value=httpx.Response(200, json={"refund_id": "re_1", "status": "succeeded"})
        )

        result = await client.refund_payment(transaction_id="txn_1", amount=10.0)

        assert result.success is True
        assert result.data["refund_id"] == "re_1"
