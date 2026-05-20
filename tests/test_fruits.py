from httpx import AsyncClient

BASE = "/api/v1/fruits"

PAYLOAD = {"nome": "Manga", "preco": "4.99", "quantidade_estoque": 100}


# ── CREATE
async def test_create_fruit(client: AsyncClient):
    r = await client.post(f"{BASE}/", json=PAYLOAD)
    assert r.status_code == 201
    body = r.json()
    assert body["nome"] == "Manga"
    assert body["preco"] == "4.99"
    assert "id" in body
    assert body["estoque_baixo"] is False
    assert body["unidade_medida"] == "unidade"


async def test_create_fruit_duplicate(client: AsyncClient):
    await client.post(f"{BASE}/", json=PAYLOAD)
    r = await client.post(f"{BASE}/", json=PAYLOAD)
    assert r.status_code == 409


async def test_create_fruit_invalid_preco(client: AsyncClient):
    r = await client.post(f"{BASE}/", json={**PAYLOAD, "preco": -1})
    assert r.status_code == 422


async def test_create_fruit_preco_custo_maior_que_preco(client: AsyncClient):
    r = await client.post(f"{BASE}/", json={**PAYLOAD, "preco_custo": "10.00"})
    assert r.status_code == 422


async def test_create_fruit_preco_custo_valido(client: AsyncClient):
    r = await client.post(f"{BASE}/", json={**PAYLOAD, "preco_custo": "2.00"})
    assert r.status_code == 201
    assert r.json()["preco_custo"] == "2.00"


# ── READ
async def test_get_fruit(client: AsyncClient):
    created = (await client.post(f"{BASE}/", json=PAYLOAD)).json()
    r = await client.get(f"{BASE}/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


async def test_get_fruit_not_found(client: AsyncClient):
    r = await client.get(f"{BASE}/nao-existe")
    assert r.status_code == 404


async def test_list_fruits_empty(client: AsyncClient):
    r = await client.get(f"{BASE}/")
    assert r.status_code == 200
    assert r.json()["total"] == 0


async def test_list_fruits_with_filter(client: AsyncClient):
    await client.post(f"{BASE}/", json=PAYLOAD)
    await client.post(f"{BASE}/", json={**PAYLOAD, "nome": "Abacaxi"})
    r = await client.get(f"{BASE}/?nome=Manga")
    assert r.status_code == 200
    assert r.json()["total"] == 1


# ── UPDATE
async def test_update_fruit(client: AsyncClient):
    created = (await client.post(f"{BASE}/", json=PAYLOAD)).json()
    r = await client.patch(f"{BASE}/{created['id']}", json={"preco": "7.50"})
    assert r.status_code == 200
    assert r.json()["preco"] == "7.50"


async def test_update_fruit_not_found(client: AsyncClient):
    r = await client.patch(f"{BASE}/nao-existe", json={"preco": "1.00"})
    assert r.status_code == 404


# ── DELETE (soft delete)
async def test_delete_fruit(client: AsyncClient):
    created = (await client.post(f"{BASE}/", json=PAYLOAD)).json()
    r = await client.delete(f"{BASE}/{created['id']}")
    assert r.status_code == 204
    assert (await client.get(f"{BASE}/{created['id']}")).status_code == 404


async def test_delete_fruit_not_found(client: AsyncClient):
    r = await client.delete(f"{BASE}/nao-existe")
    assert r.status_code == 404


async def test_deleted_fruit_nao_aparece_na_listagem(client: AsyncClient):
    created = (await client.post(f"{BASE}/", json=PAYLOAD)).json()
    await client.delete(f"{BASE}/{created['id']}")
    r = await client.get(f"{BASE}/")
    assert r.json()["total"] == 0


# ── SOFT DELETE endpoints
async def test_list_deleted_fruits(client: AsyncClient):
    created = (await client.post(f"{BASE}/", json=PAYLOAD)).json()
    await client.delete(f"{BASE}/{created['id']}")
    r = await client.get(f"{BASE}/deleted")
    assert r.status_code == 200
    assert r.json()["total"] == 1


async def test_restore_fruit(client: AsyncClient):
    created = (await client.post(f"{BASE}/", json=PAYLOAD)).json()
    await client.delete(f"{BASE}/{created['id']}")
    r = await client.post(f"{BASE}/{created['id']}/restore")
    assert r.status_code == 200
    assert r.json()["deleted_at"] is None
    assert (await client.get(f"{BASE}/")).json()["total"] == 1


# ── ESTOQUE_BAIXO
async def test_estoque_baixo_flag(client: AsyncClient):
    r = await client.post(
        f"{BASE}/", json={**PAYLOAD, "quantidade_estoque": 5, "estoque_minimo": 10}
    )
    assert r.status_code == 201
    assert r.json()["estoque_baixo"] is True
