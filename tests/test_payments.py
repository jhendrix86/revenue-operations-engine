import httpx
import respx


def _configure_baselayer(monkeypatch):
    import app.config as config_module
    monkeypatch.setattr(config_module.settings, "baselayer_url", "http://baselayer.test")
    monkeypatch.setattr(config_module.settings, "baselayer_service_email", "svc@example.com")
    monkeypatch.setattr(config_module.settings, "baselayer_service_password", "secret")


def _mock_login():
    respx.post("http://baselayer.test/api/v1/auth/login").mock(
        return_value=httpx.Response(200, json={"access_token": "tok_abc", "expires_in": 3600})
    )


async def test_create_intent_without_baselayer_configured_is_honest(client):
    r = await client.post("/payments/create-intent", json={
        "amount": 29.99, "customer_id": "cust_1",
    })

    assert r.status_code == 400
    assert "not configured" in r.json()["detail"]


@respx.mock
async def test_create_intent_processes_a_real_payment(client, monkeypatch):
    _configure_baselayer(monkeypatch)
    _mock_login()
    respx.post("http://baselayer.test/api/v1/providers/payments").mock(
        return_value=httpx.Response(200, json={"transaction_id": "txn_1", "status": "completed"})
    )

    r = await client.post("/payments/create-intent", json={
        "amount": 29.99, "customer_id": "cust_1", "description": "Pro plan",
    })

    assert r.status_code == 200
    assert r.json()["transaction_id"] == "txn_1"


@respx.mock
async def test_refund_success(client, monkeypatch):
    _configure_baselayer(monkeypatch)
    _mock_login()
    respx.post("http://baselayer.test/api/v1/providers/refunds").mock(
        return_value=httpx.Response(200, json={"refund_id": "re_1", "status": "succeeded"})
    )

    r = await client.post("/payments/refund", json={"payment_id": "txn_1", "amount": 10.0})

    assert r.status_code == 200
    assert r.json()["refund_id"] == "re_1"


@respx.mock
async def test_get_payment_not_found_returns_404(client, monkeypatch):
    _configure_baselayer(monkeypatch)
    _mock_login()
    respx.get("http://baselayer.test/api/v1/providers/payments/txn_missing").mock(
        return_value=httpx.Response(404, json={"detail": "Payment not found"})
    )

    r = await client.get("/payments/txn_missing")

    assert r.status_code == 404
