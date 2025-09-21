import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.db import Base, get_db
from app.models.agent import Agent

# ----------------------
# Configuração banco de teste (SQLite in-memory)
# ----------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ----------------------
# Helpers
# ----------------------
def create_agent(db, name="AgenteTeste"):
    agent = Agent(name=name, email="teste@exemplo.com", model="gpt-4o", owner_id=1)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


# ----------------------
# Tests
# ----------------------
def test_create_and_list_executions():
    # cria agente primeiro
    db = next(override_get_db())
    agent = create_agent(db)

    payload = {"agent_id": agent.id, "input": "Qual é a capital da França?"}
    response = client.post("/executions/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == agent.id
    assert data["input"] == "Qual é a capital da França?"

    # listar execuções
    response = client.get("/executions/")
    assert response.status_code == 200
    executions = response.json()
    assert isinstance(executions, list)
    assert len(executions) >= 1
