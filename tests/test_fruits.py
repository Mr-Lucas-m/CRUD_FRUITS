import pytest
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


def test_create_fruit_duplicate(client: TestClient):
    client.post(f"{BASE}/", json=PAYLOAD)
    r = client.post(f"{BASE}/", json=PAYLOAD)
    assert r.status_code == 409


def test_create_fruit_invalid_preco(client: TestClient):
    r = client.post(f"{BASE}/", json={**PAYLOAD, "preco": -1})
    assert r.status_code == 422


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


# ── DELETE
def test_delete_fruit(client: TestClient):
    created = client.post(f"{BASE}/", json=PAYLOAD).json()
    r = client.delete(f"{BASE}/{created['id']}")
    assert r.status_code == 204
    assert client.get(f"{BASE}/{created['id']}").status_code == 404


def test_delete_fruit_not_found(client: TestClient):
    r = client.delete(f"{BASE}/nao-existe")
    assert r.status_code == 404
