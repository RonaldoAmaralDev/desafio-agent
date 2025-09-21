import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.db import Base, get_db
from app.models.agent import Agent
from app.models.prompt import Prompt

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

    response = client.post("/prompts/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Prompt Teste"
    assert data["agent_id"] == agent.id


def test_list_prompts():
    response = client.get("/prompts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_test_prompt():
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

    response = client.post(f"/prompts/test/{agent.id}/{prompt.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == agent.id
    assert data["prompt_id"] == prompt.id
    assert "processando" in data["output"]
