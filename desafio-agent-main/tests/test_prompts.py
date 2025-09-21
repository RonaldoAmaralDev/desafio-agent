import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.db import Base, get_db
from app.models.agent import Agent
from app.models.prompt import Prompt

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


# sobrescreve dependência e recria tabelas
app.dependency_overrides[get_db] = override_get_db
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


# ----------------------
# Helpers
# ----------------------
def create_agent(db, name="AgentePrompt"):
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


# ----------------------
# Tests
# ----------------------
def test_create_prompt():
    db = next(override_get_db())
    agent = create_agent(db)

    payload = {
        "name": "Prompt Teste",
        "description": "Descrição de teste",
        "content": "Conteúdo do prompt",
        "version": "1.0",
        "agent_id": agent.id,
    }

    response = client.post("/api/v1/prompts/", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Prompt Teste"
    assert data["agent_id"] == agent.id


def test_list_prompts():
    response = client.get("/api/v1/prompts/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_test_prompt(monkeypatch):
    db = next(override_get_db())
    agent = create_agent(db, name="AgentePromptTest")

    # cria prompt diretamente no banco
    prompt = Prompt(
        name="PromptParaTeste",
        description="Prompt criado para o endpoint de test",
        content="Conteúdo para execução",
        agent_id=agent.id,
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    # mockar execução para não chamar LLM real
    from app.services.execution_service import ExecutionService

    def fake_run(self, db, execution_in):
        class DummyExec:
            def __init__(self, agent_id, prompt_id):
                self.agent_id = agent_id
                self.prompt_id = prompt_id
                self.o
