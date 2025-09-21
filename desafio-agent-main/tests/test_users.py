import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.db import Base, get_db

# ----------------------
# Configuração do banco para testes
# ----------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# cria as tabelas no SQLite de teste
Base.metadata.create_all(bind=engine)


# override da dependência do banco
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ----------------------
# Testes de Users
# ----------------------

def test_create_user():
    payload = {"name": "João", "email": "joao@example.com", "password": "123456"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "João"
    assert data["email"] == "joao@example.com"
    assert "id" in data


def test_list_users():
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_user_by_id():
    # cria usuário
    payload = {"name": "Maria", "email": "maria@example.com", "password": "senha123"}
    created = client.post("/users/", json=payload).json()

    response = client.get(f"/users/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["email"] == "maria@example.com"


def test_update_user():
    # cria usuário
    payload = {"name": "Pedro", "email": "pedro@example.com", "password": "abc123"}
    created = client.post("/users/", json=payload).json()

    update_payload = {"name": "Pedro Atualizado"}
    response = client.put(f"/users/{created['id']}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["name"] == "Pedro Atualizado"


def test_delete_user():
    # cria usuário
    payload = {"name": "Carlos", "email": "carlos@example.com", "password": "abc123"}
    created = client.post("/users/", json=payload).json()

    response = client.delete(f"/users/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    assert "deletado com sucesso" in data["message"]

    # tentar buscar usuário deletado
    response = client.get(f"/users/{created['id']}")
    assert response.status_code == 404
