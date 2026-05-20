from httpx import AsyncClient

BASE = "/api/v1/fruits"
FRUITS_PAYLOAD = {"nome": "Manga", "preco": "4.99", "quantidade_estoque": 50}


async def _create_fruit(client: AsyncClient) -> dict:
    return (await client.post(f"{BASE}/", json=FRUITS_PAYLOAD)).json()


# ── ENTRADA
async def test_stock_entrada(client: AsyncClient):
    fruit = await _create_fruit(client)
    r = await client.post(f"{BASE}/{fruit['id']}/stock/entrada", json={"quantidade": 20})
    assert r.status_code == 201
    body = r.json()
    assert body["tipo"] == "entrada"
    assert body["quantidade"] == 20
    updated = (await client.get(f"{BASE}/{fruit['id']}")).json()
    assert updated["quantidade_estoque"] == 70


async def test_stock_entrada_quantidade_zero(client: AsyncClient):
    fruit = await _create_fruit(client)
    r = await client.post(f"{BASE}/{fruit['id']}/stock/entrada", json={"quantidade": 0})
    assert r.status_code == 422


async def test_stock_entrada_fruta_nao_existe(client: AsyncClient):
    r = await client.post(f"{BASE}/nao-existe/stock/entrada", json={"quantidade": 5})
    assert r.status_code == 404


# ── SAIDA
async def test_stock_saida(client: AsyncClient):
    fruit = await _create_fruit(client)
    r = await client.post(f"{BASE}/{fruit['id']}/stock/saida", json={"quantidade": 10})
    assert r.status_code == 201
    body = r.json()
    assert body["tipo"] == "saida"
    assert body["quantidade"] == 10
    updated = (await client.get(f"{BASE}/{fruit['id']}")).json()
    assert updated["quantidade_estoque"] == 40


async def test_stock_saida_estoque_insuficiente(client: AsyncClient):
    fruit = await _create_fruit(client)
    r = await client.post(f"{BASE}/{fruit['id']}/stock/saida", json={"quantidade": 999})
    assert r.status_code == 422


async def test_stock_saida_fruta_nao_existe(client: AsyncClient):
    r = await client.post(f"{BASE}/nao-existe/stock/saida", json={"quantidade": 5})
    assert r.status_code == 404


# ── HISTÓRICO
async def test_stock_historico(client: AsyncClient):
    fruit = await _create_fruit(client)
    await client.post(f"{BASE}/{fruit['id']}/stock/entrada", json={"quantidade": 10})
    await client.post(f"{BASE}/{fruit['id']}/stock/saida", json={"quantidade": 5})
    r = await client.get(f"{BASE}/{fruit['id']}/stock/historico")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    tipos = {m["tipo"] for m in body["items"]}
    assert tipos == {"entrada", "saida"}


async def test_stock_historico_fruta_nao_existe(client: AsyncClient):
    r = await client.get(f"{BASE}/nao-existe/stock/historico")
    assert r.status_code == 404


# ── SALDO
async def test_stock_saldo(client: AsyncClient):
    fruit = await _create_fruit(client)
    await client.post(
        f"{BASE}/{fruit['id']}/stock/entrada",
        json={"quantidade": 10, "motivo": "reposição"},
    )
    r = await client.get(f"{BASE}/{fruit['id']}/stock/saldo")
    assert r.status_code == 200
    body = r.json()
    assert body["quantidade_estoque"] == 60
    assert body["ultimo_movimento"] is not None
    assert body["ultimo_movimento"]["motivo"] == "reposição"


async def test_stock_saldo_sem_movimentos(client: AsyncClient):
    fruit = await _create_fruit(client)
    r = await client.get(f"{BASE}/{fruit['id']}/stock/saldo")
    assert r.status_code == 200
    body = r.json()
    assert body["quantidade_estoque"] == 50
    assert body["ultimo_movimento"] is None
