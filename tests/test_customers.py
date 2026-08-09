import uuid


async def test_create_customer_persists_a_real_row(client):
    r = await client.post("/customers/", json={"email": "a@example.com", "name": "Alice"})

    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "a@example.com"
    assert body["name"] == "Alice"

    fetched = await client.get(f"/customers/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["email"] == "a@example.com"


async def test_create_customer_rejects_duplicate_email(client):
    await client.post("/customers/", json={"email": "dup@example.com"})

    r = await client.post("/customers/", json={"email": "dup@example.com"})

    assert r.status_code == 400


async def test_get_nonexistent_customer_returns_404(client):
    r = await client.get(f"/customers/{uuid.uuid4()}")
    assert r.status_code == 404
