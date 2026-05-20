from httpx import AsyncClient

BASE = "/api/v1/categories"
FRUITS_BASE = "/api/v1/fruits"

PAYLOAD = {"nome": "Tropical", "descricao": "Frutas tropicais"}


# ── CREATE
async def test_create_category(client: AsyncClient):
    r = await client.post(f"{BASE}/", json=PAYLOAD)
    assert r.status_code == 201
    body = r.json()
    assert body["nome"] == "Tropical"
    assert "id" in body


async def test_create_category_duplicate(client: AsyncClient):
    await client.post(f"{BASE}/", json=PAYLOAD)
    r = await client.post(f"{BASE}/", json=PAYLOAD)
    assert r.status_code == 409


async def test_create_category_nome_muito_curto(client: AsyncClient):
    r = await client.post(f"{BASE}/", json={"nome": "A"})
    assert r.status_code == 422


# ── READ
async def test_get_category(client: AsyncClient):
    created = (await client.post(f"{BASE}/", json=PAYLOAD)).json()
    r = await client.get(f"{BASE}/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


async def test_get_category_not_found(client: AsyncClient):
    r = await client.get(f"{BASE}/nao-existe")
    assert r.status_code == 404


async def test_list_categories_empty(client: AsyncClient):
    r = await client.get(f"{BASE}/")
    assert r.status_code == 200
    assert r.json()["total"] == 0


async def test_list_categories(client: AsyncClient):
    await client.post(f"{BASE}/", json=PAYLOAD)
    await client.post(f"{BASE}/", json={"nome": "Citrica"})
    r = await client.get(f"{BASE}/")
    assert r.json()["total"] == 2


# ── UPDATE
async def test_update_category(client: AsyncClient):
    created = (await client.post(f"{BASE}/", json=PAYLOAD)).json()
    r = await client.patch(f"{BASE}/{created['id']}", json={"descricao": "Nova descricao"})
    assert r.status_code == 200
    assert r.json()["descricao"] == "Nova descricao"


async def test_update_category_not_found(client: AsyncClient):
    r = await client.patch(f"{BASE}/nao-existe", json={"nome": "Outro"})
    assert r.status_code == 404


# ── DELETE
async def test_delete_category(client: AsyncClient):
    created = (await client.post(f"{BASE}/", json=PAYLOAD)).json()
    r = await client.delete(f"{BASE}/{created['id']}")
    assert r.status_code == 204


async def test_delete_category_not_found(client: AsyncClient):
    r = await client.delete(f"{BASE}/nao-existe")
    assert r.status_code == 404


async def test_delete_category_com_frutas_vinculadas(client: AsyncClient):
    cat = (await client.post(f"{BASE}/", json=PAYLOAD)).json()
    await client.post(
        f"{FRUITS_BASE}/",
        json={"nome": "Manga", "preco": "4.99", "quantidade_estoque": 10, "category_id": cat["id"]},
    )
    r = await client.delete(f"{BASE}/{cat['id']}")
    assert r.status_code == 409


# ── FRUITS POR CATEGORIA
async def test_list_category_fruits(client: AsyncClient):
    cat = (await client.post(f"{BASE}/", json=PAYLOAD)).json()
    await client.post(
        f"{FRUITS_BASE}/",
        json={"nome": "Manga", "preco": "4.99", "quantidade_estoque": 10, "category_id": cat["id"]},
    )
    r = await client.get(f"{BASE}/{cat['id']}/fruits")
    assert r.status_code == 200
    assert r.json()["total"] == 1


async def test_list_category_fruits_categoria_nao_existe(client: AsyncClient):
    r = await client.get(f"{BASE}/nao-existe/fruits")
    assert r.status_code == 404
