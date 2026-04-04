from fastapi.testclient import TestClient

BASE = "/api/v1/categories"
FRUITS_BASE = "/api/v1/fruits"

PAYLOAD = {"nome": "Tropical", "descricao": "Frutas tropicais"}


# ── CREATE
def test_create_category(client: TestClient):
    r = client.post(f"{BASE}/", json=PAYLOAD)
    assert r.status_code == 201
    body = r.json()
    assert body["nome"] == "Tropical"
    assert "id" in body


def test_create_category_duplicate(client: TestClient):
    client.post(f"{BASE}/", json=PAYLOAD)
    r = client.post(f"{BASE}/", json=PAYLOAD)
    assert r.status_code == 409


def test_create_category_nome_muito_curto(client: TestClient):
    r = client.post(f"{BASE}/", json={"nome": "A"})
    assert r.status_code == 422


# ── READ
def test_get_category(client: TestClient):
    created = client.post(f"{BASE}/", json=PAYLOAD).json()
    r = client.get(f"{BASE}/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_get_category_not_found(client: TestClient):
    r = client.get(f"{BASE}/nao-existe")
    assert r.status_code == 404


def test_list_categories_empty(client: TestClient):
    r = client.get(f"{BASE}/")
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_list_categories(client: TestClient):
    client.post(f"{BASE}/", json=PAYLOAD)
    client.post(f"{BASE}/", json={"nome": "Citrica"})
    r = client.get(f"{BASE}/")
    assert r.json()["total"] == 2


# ── UPDATE
def test_update_category(client: TestClient):
    created = client.post(f"{BASE}/", json=PAYLOAD).json()
    r = client.patch(f"{BASE}/{created['id']}", json={"descricao": "Nova descricao"})
    assert r.status_code == 200
    assert r.json()["descricao"] == "Nova descricao"


def test_update_category_not_found(client: TestClient):
    r = client.patch(f"{BASE}/nao-existe", json={"nome": "Outro"})
    assert r.status_code == 404


# ── DELETE
def test_delete_category(client: TestClient):
    created = client.post(f"{BASE}/", json=PAYLOAD).json()
    r = client.delete(f"{BASE}/{created['id']}")
    assert r.status_code == 204


def test_delete_category_not_found(client: TestClient):
    r = client.delete(f"{BASE}/nao-existe")
    assert r.status_code == 404


def test_delete_category_com_frutas_vinculadas(client: TestClient):
    cat = client.post(f"{BASE}/", json=PAYLOAD).json()
    client.post(
        f"{FRUITS_BASE}/",
        json={"nome": "Manga", "preco": "4.99", "quantidade_estoque": 10, "category_id": cat["id"]},
    )
    r = client.delete(f"{BASE}/{cat['id']}")
    assert r.status_code == 409


# ── FRUITS POR CATEGORIA
def test_list_category_fruits(client: TestClient):
    cat = client.post(f"{BASE}/", json=PAYLOAD).json()
    client.post(
        f"{FRUITS_BASE}/",
        json={"nome": "Manga", "preco": "4.99", "quantidade_estoque": 10, "category_id": cat["id"]},
    )
    r = client.get(f"{BASE}/{cat['id']}/fruits")
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_list_category_fruits_categoria_nao_existe(client: TestClient):
    r = client.get(f"{BASE}/nao-existe/fruits")
    assert r.status_code == 404
