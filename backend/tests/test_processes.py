def create_process_payload(**overrides):
    payload = {
        "name": "Processo de teste",
        "description": "Descrição de teste",
        "category": "Teste",
        "department": "QA",
        "status": "aberto",
        "priority": "media",
    }
    payload.update(overrides)
    return payload


def test_create_process_requires_auth(client):
    response = client.post("/api/processes/", json=create_process_payload())
    assert response.status_code == 401


def test_create_process_success(client, auth_headers):
    response = client.post("/api/processes/", json=create_process_payload(), headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Processo de teste"
    assert data["status"] == "aberto"
    assert "id" in data


def test_create_process_invalid_status_fails(client, auth_headers):
    response = client.post(
        "/api/processes/",
        json=create_process_payload(status="status_invalido"),
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_list_processes(client, auth_headers):
    client.post("/api/processes/", json=create_process_payload(), headers=auth_headers)
    client.post("/api/processes/", json=create_process_payload(name="Segundo processo"), headers=auth_headers)

    response = client.get("/api/processes/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_process_by_id(client, auth_headers):
    created = client.post("/api/processes/", json=create_process_payload(), headers=auth_headers).json()

    response = client.get(f"/api/processes/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_nonexistent_process_returns_404(client, auth_headers):
    response = client.get("/api/processes/id-que-nao-existe", headers=auth_headers)
    assert response.status_code == 404


def test_update_process_partial(client, auth_headers):
    created = client.post("/api/processes/", json=create_process_payload(), headers=auth_headers).json()

    response = client.patch(
        f"/api/processes/{created['id']}",
        json={"status": "em_andamento"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "em_andamento"
    # Campos nao enviados no PATCH devem permanecer intactos.
    assert data["name"] == "Processo de teste"


def test_delete_process(client, auth_headers):
    created = client.post("/api/processes/", json=create_process_payload(), headers=auth_headers).json()

    delete_response = client.delete(f"/api/processes/{created['id']}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/processes/{created['id']}", headers=auth_headers)
    assert get_response.status_code == 404
