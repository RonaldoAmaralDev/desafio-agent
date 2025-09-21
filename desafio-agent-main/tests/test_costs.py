import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.db import Base, get_db
from app.models.agent import Agent
from app.models.execution_cost import ExecutionCost

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
def create_agent(db, name="AgenteCustos"):
    agent = Agent(
        name=name,
        model="llama3",
        temperature=0.7,
        owner_id=1,
        provider="ollama",
        base_url="http://localhost:11434",
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def create_execution_cost(db, agent_id: int, cost: float = 0.123):
    execution_cost = ExecutionCost(execution_id=1, agent_id=agent_id, cost=cost)
    db.add(execution_cost)
    db.commit()
    return execution_cost


# ----------------------
# Tests
# ----------------------
def test_get_agent_costs_success():
    db = next(override_get_db())
    agent = create_agent(db)
    create_execution_cost(db, agent.id, cost=0.456)

    response = client.get(f"/costs/agent/{agent.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == agent.id
    assert data["total_cost"] > 0
    assert isinstance(data["executions"], list)
    assert len(data["executions"]) >= 1


def test_get_agent_costs_not_found():
    response = client.get("/costs/agent/999")
    assert response.status_code == 404
    data = response.json()
    assert "Nenhum custo encontrado" in data["detail"]
