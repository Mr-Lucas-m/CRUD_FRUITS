from fastapi.testclient import TestClient

BASE = "/api/v1/fruits"

PAYLOAD = {"nome": "Manga", "preco": "4.99", "quantidade_estoque": 100}


# ── CREATE
def test_create_fruit(client: TestClient):
    r = client.post(f"{BASE}/", json=PAYLOAD)
    assert r.status_code == 201
    body = r.json()
    assert body["nome"] == "Manga"
    assert body["preco"] == "4.99"
    assert "id" in body
    assert body["estoque_baixo"] is False
    assert body["unidade_medida"] == "unidade"


def test_create_fruit_duplicate(client: TestClient):
    client.post(f"{BASE}/", json=PAYLOAD)
    r = client.post(f"{BASE}/", json=PAYLOAD)
    assert r.status_code == 409


def test_create_fruit_invalid_preco(client: TestClient):
    r = client.post(f"{BASE}/", json={**PAYLOAD, "preco": -1})
    assert r.status_code == 422


def test_create_fruit_preco_custo_maior_que_preco(client: TestClient):
    r = client.post(f"{BASE}/", json={**PAYLOAD, "preco_custo": "10.00"})
    assert r.status_code == 422


def test_create_fruit_preco_custo_valido(client: TestClient):
    r = client.post(f"{BASE}/", json={**PAYLOAD, "preco_custo": "2.00"})
    assert r.status_code == 201
    assert r.json()["preco_custo"] == "2.00"


# ── READ
def test_get_fruit(client: TestClient):
    created = client.post(f"{BASE}/", json=PAYLOAD).json()
    r = client.get(f"{BASE}/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_get_fruit_not_found(client: TestClient):
    r = client.get(f"{BASE}/nao-existe")
    assert r.status_code == 404


def test_list_fruits_empty(client: TestClient):
    r = client.get(f"{BASE}/")
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_list_fruits_with_filter(client: TestClient):
    client.post(f"{BASE}/", json=PAYLOAD)
    client.post(f"{BASE}/", json={**PAYLOAD, "nome": "Abacaxi"})
    r = client.get(f"{BASE}/?nome=Manga")
    assert r.status_code == 200
    assert r.json()["total"] == 1


# ── UPDATE
def test_update_fruit(client: TestClient):
    created = client.post(f"{BASE}/", json=PAYLOAD).json()
    r = client.patch(f"{BASE}/{created['id']}", json={"preco": "7.50"})
    assert r.status_code == 200
    assert r.json()["preco"] == "7.50"


def test_update_fruit_not_found(client: TestClient):
    r = client.patch(f"{BASE}/nao-existe", json={"preco": "1.00"})
    assert r.status_code == 404


# ── DELETE (soft delete)
def test_delete_fruit(client: TestClient):
    created = client.post(f"{BASE}/", json=PAYLOAD).json()
    r = client.delete(f"{BASE}/{created['id']}")
    assert r.status_code == 204
    # Fruit deve estar inacessível via GET normal
    assert client.get(f"{BASE}/{created['id']}").status_code == 404


def test_delete_fruit_not_found(client: TestClient):
    r = client.delete(f"{BASE}/nao-existe")
    assert r.status_code == 404


def test_deleted_fruit_nao_aparece_na_listagem(client: TestClient):
    created = client.post(f"{BASE}/", json=PAYLOAD).json()
    client.delete(f"{BASE}/{created['id']}")
    r = client.get(f"{BASE}/")
    assert r.json()["total"] == 0


# ── SOFT DELETE endpoints
def test_list_deleted_fruits(client: TestClient):
    created = client.post(f"{BASE}/", json=PAYLOAD).json()
    client.delete(f"{BASE}/{created['id']}")
    r = client.get(f"{BASE}/deleted")
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_restore_fruit(client: TestClient):
    created = client.post(f"{BASE}/", json=PAYLOAD).json()
    client.delete(f"{BASE}/{created['id']}")
    r = client.post(f"{BASE}/{created['id']}/restore")
    assert r.status_code == 200
    assert r.json()["deleted_at"] is None
    # Deve aparecer na listagem normal novamente
    assert client.get(f"{BASE}/").json()["total"] == 1


# ── ESTOQUE_BAIXO
def test_estoque_baixo_flag(client: TestClient):
    r = client.post(f"{BASE}/", json={**PAYLOAD, "quantidade_estoque": 5, "estoque_minimo": 10})
    assert r.status_code == 201
    assert r.json()["estoque_baixo"] is True
