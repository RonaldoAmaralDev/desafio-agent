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
def create_agent_in_db(db, name="AgenteTeste", provider="ollama", model="llama3"):
    agent = Agent(
        name=name,
        model=model,
        temperature=0.5,
        owner_id=1,
        provider=provider,
        base_url="http://localhost:11434",
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


# ----------------------
# Tests
# ----------------------
def test_create_agent():
    payload = {
        "name": "Agente 1",
        "model": "llama3",
        "temperature": 0.7,
        "owner_id": 1,
        "provider": "ollama",
        "base_url": "http://localhost:11434"
    }
    response = client.post("/agents/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Agente 1"
    assert data["model"] == "llama3"


def test_list_agents():
    response = client.get("/agents/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_run_agent_stream(monkeypatch):
    db = next(override_get_db())
    agent = create_agent_in_db(db)

    # mock do ChatOllama stream
    class DummyStream:
        def __init__(self, content):
            self.content = content

    def fake_stream(prompt):
        yield DummyStream("Olá")
        yield DummyStream(" mundo!")

    monkeypatch.setattr("app.api.v1.agents.ChatOllama.stream", fake_stream)

    payload = {"input": "Diga olá"}
    response = client.post(f"/agents/{agent.id}/run/stream", json=payload)

    assert response.status_code == 200
    # streaming retorna NDJSON → juntar chunks
    lines = [line for line in response.iter_lines() if line]
    assert any(b"Ol\xc3\xa1" in l for l in lines)

def test_list_agent_costs(monkeypatch):
    db = next(override_get_db())
    agent = create_agent_in_db(db, name="AgenteCustos")

    # mock: não deixar erro se não houver custos
    from app.models.execution_cost import ExecutionCost
    db.add(ExecutionCost(execution_id=1, agent_id=agent.id, cost=0.123))
    db.commit()

    response = client.get(f"/agents/{agent.id}/costs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["cost"] == 0.123
