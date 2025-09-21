import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.db import Base, get_db
from app.models.agent import Agent
from app.models.execution_cost import ExecutionCost

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

    response = client.get(f"/api/v1/agents/{agent.id}/costs")
    return response


def test_get_agent_costs_not_found():
    response = client.get("/api/v1/agents/999/costs")
    assert response.status_code == 404, response.text
    data = response.json()
    assert "Nenhum custo encontrado" in data["detail"]