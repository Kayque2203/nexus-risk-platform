import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.base_class import Base
from app.db.session import get_db

# Banco de dados isolado para testes -- SQLite em arquivo separado,
# nunca toca no nexus.db usado no desenvolvimento manual.
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Recria o schema do zero antes de CADA teste -- garante que um
    teste nunca depende de dados deixados por outro (isolamento total)."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user_data():
    return {
        "name": "Usuário de Teste",
        "email": "pytest@nexus.dev",
        "role": "admin",
        "department": "QA",
        "password": "senha123",
    }


@pytest.fixture
def registered_user(client, test_user_data):
    response = client.post("/api/users/", json=test_user_data)
    return response.json()


@pytest.fixture
def auth_headers(client, test_user_data, registered_user):
    """Loga o usuário de teste e retorna o header de Authorization
    pronto para usar em qualquer requisição que exija autenticação."""
    response = client.post(
        "/api/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
