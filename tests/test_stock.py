from fastapi.testclient import TestClient

BASE = "/api/v1/fruits"
FRUITS_PAYLOAD = {"nome": "Manga", "preco": "4.99", "quantidade_estoque": 50}


def _create_fruit(client: TestClient) -> dict:
    return client.post(f"{BASE}/", json=FRUITS_PAYLOAD).json()


# ── ENTRADA
def test_stock_entrada(client: TestClient):
    fruit = _create_fruit(client)
    r = client.post(f"{BASE}/{fruit['id']}/stock/entrada", json={"quantidade": 20})
    assert r.status_code == 201
    body = r.json()
    assert body["tipo"] == "entrada"
    assert body["quantidade"] == 20
    # Verifica que o estoque foi atualizado
    updated = client.get(f"{BASE}/{fruit['id']}").json()
    assert updated["quantidade_estoque"] == 70


def test_stock_entrada_quantidade_zero(client: TestClient):
    fruit = _create_fruit(client)
    r = client.post(f"{BASE}/{fruit['id']}/stock/entrada", json={"quantidade": 0})
    assert r.status_code == 422


def test_stock_entrada_fruta_nao_existe(client: TestClient):
    r = client.post(f"{BASE}/nao-existe/stock/entrada", json={"quantidade": 5})
    assert r.status_code == 404


# ── SAIDA
def test_stock_saida(client: TestClient):
    fruit = _create_fruit(client)
    r = client.post(f"{BASE}/{fruit['id']}/stock/saida", json={"quantidade": 10})
    assert r.status_code == 201
    body = r.json()
    assert body["tipo"] == "saida"
    assert body["quantidade"] == 10
    updated = client.get(f"{BASE}/{fruit['id']}").json()
    assert updated["quantidade_estoque"] == 40


def test_stock_saida_estoque_insuficiente(client: TestClient):
    fruit = _create_fruit(client)
    r = client.post(f"{BASE}/{fruit['id']}/stock/saida", json={"quantidade": 999})
    assert r.status_code == 422


def test_stock_saida_fruta_nao_existe(client: TestClient):
    r = client.post(f"{BASE}/nao-existe/stock/saida", json={"quantidade": 5})
    assert r.status_code == 404


# ── HISTÓRICO
def test_stock_historico(client: TestClient):
    fruit = _create_fruit(client)
    client.post(f"{BASE}/{fruit['id']}/stock/entrada", json={"quantidade": 10})
    client.post(f"{BASE}/{fruit['id']}/stock/saida", json={"quantidade": 5})
    r = client.get(f"{BASE}/{fruit['id']}/stock/historico")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    tipos = {m["tipo"] for m in body["items"]}
    assert tipos == {"entrada", "saida"}


def test_stock_historico_fruta_nao_existe(client: TestClient):
    r = client.get(f"{BASE}/nao-existe/stock/historico")
    assert r.status_code == 404


# ── SALDO
def test_stock_saldo(client: TestClient):
    fruit = _create_fruit(client)
    client.post(f"{BASE}/{fruit['id']}/stock/entrada", json={"quantidade": 10, "motivo": "reposição"})
    r = client.get(f"{BASE}/{fruit['id']}/stock/saldo")
    assert r.status_code == 200
    body = r.json()
    assert body["quantidade_estoque"] == 60
    assert body["ultimo_movimento"] is not None
    assert body["ultimo_movimento"]["motivo"] == "reposição"


def test_stock_saldo_sem_movimentos(client: TestClient):
    fruit = _create_fruit(client)
    r = client.get(f"{BASE}/{fruit['id']}/stock/saldo")
    assert r.status_code == 200
    body = r.json()
    assert body["quantidade_estoque"] == 50
    assert body["ultimo_movimento"] is None
