import pytest
from app.services.risk_engine import calculate_severity


def create_process(client, auth_headers):
    payload = {
        "name": "Processo para riscos",
        "status": "aberto",
        "priority": "media",
    }
    return client.post("/api/processes/", json=payload, headers=auth_headers).json()


def create_risk_payload(process_id, **overrides):
    payload = {
        "process_id": process_id,
        "description": "Risco de teste",
        "category": "Teste",
        "probability": "media",
        "impact": "media",
        "priority": "media",
        "status": "aberto",
    }
    payload.update(overrides)
    return payload


# ---------- Testes de CRUD ----------

def test_create_risk_requires_auth(client):
    response = client.post("/api/risks/", json=create_risk_payload("qualquer-id"))
    assert response.status_code == 401


def test_create_risk_success(client, auth_headers):
    process = create_process(client, auth_headers)
    response = client.post(
        "/api/risks/", json=create_risk_payload(process["id"]), headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["process_id"] == process["id"]
    assert data["severity"] is not None


def test_create_risk_with_nonexistent_process_fails(client, auth_headers):
    response = client.post(
        "/api/risks/",
        json=create_risk_payload("processo-que-nao-existe"),
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "processo" in response.json()["detail"].lower()


def test_delete_risk(client, auth_headers):
    process = create_process(client, auth_headers)
    created = client.post(
        "/api/risks/", json=create_risk_payload(process["id"]), headers=auth_headers
    ).json()

    delete_response = client.delete(f"/api/risks/{created['id']}", headers=auth_headers)
    assert delete_response.status_code == 204


# ---------- Testes do Risk Engine (unitarios, sem API) ----------
# Estes testam a funcao pura de calculo, isolada de banco/HTTP --
# rodam em milissegundos e cobrem a logica de negocio mais importante
# do sistema: a matriz de severidade.

@pytest.mark.parametrize(
    "probability,impact,expected_severity",
    [
        ("baixa", "baixa", "baixa"),
        ("media", "media", "media"),
        ("alta", "alta", "alta"),
        ("critica", "critica", "critica"),
        ("critica", "alta", "critica"),
        ("alta", "critica", "critica"),
        ("baixa", "critica", "media"),
        ("critica", "baixa", "media"),
    ],
)
def test_risk_engine_matrix(probability, impact, expected_severity):
    assert calculate_severity(probability, impact) == expected_severity


def test_risk_engine_raises_on_invalid_level():
    with pytest.raises(KeyError):
        calculate_severity("nivel_invalido", "alta")


# ---------- Teste de integracao: severidade recalculada no PATCH ----------

def test_severity_recalculated_on_update(client, auth_headers):
    process = create_process(client, auth_headers)
    created = client.post(
        "/api/risks/",
        json=create_risk_payload(process["id"], probability="alta", impact="alta"),
        headers=auth_headers,
    ).json()
    assert created["severity"] == "alta"

    updated = client.patch(
        f"/api/risks/{created['id']}",
        json={"probability": "critica"},
        headers=auth_headers,
    ).json()
    assert updated["severity"] == "critica"
