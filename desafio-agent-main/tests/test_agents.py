import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.db import Base, get_db
from app.models.agent import Agent
import json

# ----------------------
# Configuração banco de teste (SQLite in-memory compartilhado)
# ----------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

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
        "model": "gemma:2b-instruct",
        "temperature": 0.7,
        "owner_id": 1,
        "provider": "ollama",
        "base_url": "http://localhost:11434"
    }
    response = client.post("/api/v1/agents/", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Agente 1"
    assert data["model"] == "gemma:2b-instruct"


def test_list_agents():
    response = client.get("/api/v1/agents/")
    assert response.status_code == 200, response.text
    data = response.json()
    return data


def test_run_agent_stream(monkeypatch):
    db = next(override_get_db())
    agent = create_agent_in_db(db)

    # Dummy para simular o stream do ChatOllama
    class DummyStream:
        def __init__(self, content):
            self.content = content

    def fake_stream(prompt):
        yield DummyStream("Olá")
        yield DummyStream(" mundo!")

    class DummyChatOllama:
        def __init__(self, *args, **kwargs):
            pass

        def stream(self, prompt):
            return fake_stream(prompt)

    # mocka a classe inteira ChatOllama
    import langchain_ollama
    monkeypatch.setattr(langchain_ollama, "ChatOllama", DummyChatOllama)

    payload = {"input": "Diga olá"}
    response = client.post(f"/api/v1/agents/{agent.id}/run/stream", json=payload)

    assert response.status_code == 200, response.text
    lines = [line for line in response.iter_lines() if line]
    parsed = [json.loads(line) for line in lines]
    return

def test_list_agent_costs(monkeypatch):
    db = next(override_get_db())
    agent = create_agent_in_db(db, name="AgenteCustos")

    from app.models.execution_cost import ExecutionCost
    db.add(ExecutionCost(execution_id=1, agent_id=agent.id, cost=0.123))
    db.commit()

    response = client.get(f"/api/v1/agents/{agent.id}/costs")
    return response
