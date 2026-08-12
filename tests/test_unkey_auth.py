"""
Confirms the Unkey wiring on this engine: fails open (no auth required)
when UNKEY_ROOT_KEY isn't configured, and actually enforces once it is.
"""
import httpx
import pytest
import respx
from unkey_auth import middleware as unkey_middleware
from unkey_auth.client import UnkeyClient
from unkey_auth.config import Config


@pytest.fixture(autouse=True)
def reset_unkey_singleton(monkeypatch):
    monkeypatch.setattr(unkey_middleware, "_client", None)
    monkeypatch.setattr(unkey_middleware, "_warned_disabled", False)
    yield


async def test_routes_work_without_auth_header_when_unkey_not_configured(client, monkeypatch):
    # Not monkeypatch.delenv("UNKEY_ROOT_KEY") - this engine's real .env now
    # has a real key (2026-08-12), and Config.from_env() deliberately
    # reloads it fresh from disk via load_dotenv() every time it's called,
    # which would silently undo an env-var deletion. Construct a disabled
    # Config directly instead, same pattern the other tests in this file
    # already use for the enabled case.
    monkeypatch.setattr(
        unkey_middleware,
        "_client",
        UnkeyClient(Config(unkey_root_key="", unkey_base_url="https://api.unkey.com/v2")),
    )

    response = await client.get(f"/customers/{'0' * 32}")

    # 404 (not 401) proves the request reached the real handler unauthenticated
    assert response.status_code == 404


async def test_missing_key_rejected_once_unkey_is_configured(client, monkeypatch):
    monkeypatch.setattr(
        unkey_middleware,
        "_client",
        UnkeyClient(Config(unkey_root_key="root_test", unkey_base_url="https://api.unkey.com/v2")),
    )

    response = await client.get("/customers/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 401


@respx.mock
async def test_valid_key_passes_through_once_unkey_is_configured(client, monkeypatch):
    monkeypatch.setattr(
        unkey_middleware,
        "_client",
        UnkeyClient(Config(unkey_root_key="root_test", unkey_base_url="https://api.unkey.com/v2")),
    )
    respx.post("https://api.unkey.com/v2/keys.verifyKey").mock(
        return_value=httpx.Response(200, json={"meta": {}, "data": {"valid": True, "code": "VALID"}})
    )

    response = await client.get(
        "/customers/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": "Bearer unkey_live_test"},
    )

    assert response.status_code == 404  # reached the real handler, just no such customer


async def test_health_check_never_requires_auth(client, monkeypatch):
    monkeypatch.setattr(
        unkey_middleware,
        "_client",
        UnkeyClient(Config(unkey_root_key="root_test", unkey_base_url="https://api.unkey.com/v2")),
    )

    response = await client.get("/health")

    assert response.status_code == 200


async def test_webhooks_never_require_unkey_auth(client, monkeypatch):
    """Inbound provider webhooks are verified by signature, not Unkey."""
    monkeypatch.setattr(
        unkey_middleware,
        "_client",
        UnkeyClient(Config(unkey_root_key="root_test", unkey_base_url="https://api.unkey.com/v2")),
    )

    response = await client.post("/webhooks/stripe", content=b"{}", headers={"stripe-signature": "invalid"})

    # Whatever it does (likely a signature-verification failure), it must
    # not be gated by Unkey's 401 - webhooks aren't in the _auth dependency list.
    assert response.status_code != 401
