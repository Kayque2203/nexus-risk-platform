def test_create_user_success(client, test_user_data):
    response = client.post("/api/users/", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert "password" not in data
    assert "hashed_password" not in data


def test_create_user_duplicate_email_fails(client, test_user_data, registered_user):
    response = client.post("/api/users/", json=test_user_data)
    assert response.status_code == 400
    assert "e-mail" in response.json()["detail"].lower()


def test_login_success(client, test_user_data, registered_user):
    response = client.post(
        "/api/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_fails(client, test_user_data, registered_user):
    response = client.post(
        "/api/auth/login",
        data={"username": test_user_data["email"], "password": "senha_errada"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user_fails(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "naoexiste@nexus.dev", "password": "qualquer"},
    )
    assert response.status_code == 401


def test_access_protected_route_without_token_fails(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_access_protected_route_with_token_succeeds(client, auth_headers, test_user_data):
    response = client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_user_data["email"]
