from httpx import AsyncClient

BASE = "/api/v1/auth"

USER_PAYLOAD = {"email": "user@example.com", "password": "senha123"}


# ── REGISTER
async def test_register(client: AsyncClient):
    r = await client.post(f"{BASE}/register", json=USER_PAYLOAD)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == USER_PAYLOAD["email"]
    assert body["is_active"] is True
    assert "id" in body
    assert "hashed_password" not in body


async def test_register_duplicate_email(client: AsyncClient):
    await client.post(f"{BASE}/register", json=USER_PAYLOAD)
    r = await client.post(f"{BASE}/register", json=USER_PAYLOAD)
    assert r.status_code == 409


async def test_register_senha_curta(client: AsyncClient):
    r = await client.post(f"{BASE}/register", json={"email": "x@x.com", "password": "123"})
    assert r.status_code == 422


async def test_register_email_invalido(client: AsyncClient):
    r = await client.post(f"{BASE}/register", json={"email": "nao-e-email", "password": "senha123"})
    assert r.status_code == 422


# ── LOGIN
async def test_login(client: AsyncClient):
    await client.post(f"{BASE}/register", json=USER_PAYLOAD)
    r = await client.post(f"{BASE}/login", json=USER_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_senha_errada(client: AsyncClient):
    await client.post(f"{BASE}/register", json=USER_PAYLOAD)
    r = await client.post(f"{BASE}/login", json={**USER_PAYLOAD, "password": "senha_errada"})
    assert r.status_code == 401


async def test_login_email_nao_cadastrado(client: AsyncClient):
    r = await client.post(f"{BASE}/login", json=USER_PAYLOAD)
    assert r.status_code == 401


# ── REFRESH
async def test_refresh_token(client: AsyncClient):
    await client.post(f"{BASE}/register", json=USER_PAYLOAD)
    tokens = (await client.post(f"{BASE}/login", json=USER_PAYLOAD)).json()
    r = await client.post(f"{BASE}/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body


async def test_refresh_token_invalido(client: AsyncClient):
    r = await client.post(f"{BASE}/refresh", json={"refresh_token": "token-invalido"})
    assert r.status_code == 401
