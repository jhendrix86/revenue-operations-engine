"""
Verifies the automatic tenant query filtering added to app/database.py
actually isolates data between tenants, not just that it no-ops safely
when no tenant context is set (the rest of the suite already covers that
implicitly - every other test runs with no X-Tenant-ID header at all).

This engine's /customers router only has create + get-by-id (no list
endpoint), so isolation is proven via get-by-id rather than a listing
count like the equivalent test in content-engine/marketing-automation-engine.
"""

import uuid

TENANT_A = str(uuid.uuid4())
TENANT_B = str(uuid.uuid4())


async def _create_customer(client, tenant_id, email):
    resp = await client.post(
        "/customers/",
        json={"email": email},
        headers={"X-Tenant-ID": tenant_id},
    )
    assert resp.status_code == 200
    return resp.json()["id"]


async def test_tenant_cannot_read_another_tenants_customer(client):
    customer_id = await _create_customer(client, TENANT_A, "a@tenant-a.example")

    same_tenant = await client.get(f"/customers/{customer_id}", headers={"X-Tenant-ID": TENANT_A})
    assert same_tenant.status_code == 200

    other_tenant = await client.get(f"/customers/{customer_id}", headers={"X-Tenant-ID": TENANT_B})
    assert other_tenant.status_code == 404


async def test_no_tenant_header_can_still_read_any_customer(client):
    """Fail-open posture: no X-Tenant-ID means no filtering is applied."""
    customer_id = await _create_customer(client, TENANT_A, "a@tenant-a.example")

    unscoped = await client.get(f"/customers/{customer_id}")
    assert unscoped.status_code == 200
