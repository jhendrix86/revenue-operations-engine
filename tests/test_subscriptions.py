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


async def test_create_subscription_without_baselayer_configured_is_honest(client):
    # conftest leaves BASELAYER_SERVICE_EMAIL unset by default
    r = await client.post("/subscriptions/create", json={
        "customer_id": "cust_1", "plan_id": "plan_pro", "payment_method_id": "pm_1",
    })

    assert r.status_code == 400
    assert "not configured" in r.json()["detail"]


@respx.mock
async def test_create_subscription_success(client, monkeypatch):
    _configure_baselayer(monkeypatch)
    _mock_login()
    respx.post("http://baselayer.test/api/v1/subscriptions").mock(
        return_value=httpx.Response(200, json={"subscription_id": "sub_1", "status": "active"})
    )

    r = await client.post("/subscriptions/create", json={
        "customer_id": "cust_1", "plan_id": "plan_pro", "payment_method_id": "pm_1",
    })

    assert r.status_code == 200
    assert r.json()["subscription_id"] == "sub_1"


@respx.mock
async def test_cancel_subscription_success(client, monkeypatch):
    _configure_baselayer(monkeypatch)
    _mock_login()
    respx.post("http://baselayer.test/api/v1/subscriptions/cust_1/plan_pro/cancel").mock(
        return_value=httpx.Response(200, json={"status": "cancelled"})
    )

    r = await client.post("/subscriptions/cust_1/plan_pro/cancel", params={"reason": "too expensive"})

    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"


@respx.mock
async def test_get_subscription_not_found_returns_404(client, monkeypatch):
    _configure_baselayer(monkeypatch)
    _mock_login()
    respx.get("http://baselayer.test/api/v1/subscriptions/cust_1/plan_pro").mock(
        return_value=httpx.Response(404, json={"detail": "Subscription not found"})
    )

    r = await client.get("/subscriptions/cust_1/plan_pro")

    assert r.status_code == 404


@respx.mock
async def test_change_subscription_plan_success(client, monkeypatch):
    _configure_baselayer(monkeypatch)
    _mock_login()
    respx.put("http://baselayer.test/api/v1/subscriptions/cust_1/plan_basic").mock(
        return_value=httpx.Response(200, json={"status": "active", "plan_tier": "plan_pro"})
    )

    r = await client.put("/subscriptions/cust_1/plan_basic", params={"new_plan_id": "plan_pro"})

    assert r.status_code == 200
    assert r.json()["plan_tier"] == "plan_pro"
