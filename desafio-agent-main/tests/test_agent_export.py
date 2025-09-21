import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.db import Base, get_db
from app.models import agent, prompt, user, execution, execution_cost  # garante que as tabelas sejam registradas
from app.models.agent import Agent
from app.models.prompt import Prompt

# ----------------------
# Configuração do banco de teste (SQLite in-memory compartilhado)
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
def create_agent_with_prompt(db, name="AgenteExport"):
    agent_obj = Agent(
        name=name,
        model="llama3",
        temperature=0.7,
        owner_id=1,
        provider="ollama",
        base_url="http://localhost:11434",
    )
    db.add(agent_obj)
    db.commit()
    db.refresh(agent_obj)

    prompt_obj = Prompt(
        name="Prompt Teste",
        description="Descrição teste",
        content="Conteúdo de prompt",
        agent_id=agent_obj.id,
    )
    db.add(prompt_obj)
    db.commit()
    db.refresh(prompt_obj)

    return agent_obj


# ----------------------
# Tests
# ----------------------
def test_export_all_agents():
    db = next(override_get_db())
    create_agent_with_prompt(db)

    response = client.get("/api/v1/agents/export")
    return response


def test_export_one_agent():
    db = next(override_get_db())
    agent = create_agent_with_prompt(db, name="AgenteÚnico")

    response = client.get(f"/api/v1/agents/{agent.id}/export")
    return response


def test_import_agents():
    payload = {
        "agents": [
            {
                "name": "AgenteImportado",
                "description": "Import test",
                "model": "llama3",
                "temperature": 0.5,
                "owner_id": 1,
                "provider": "ollama",
                "base_url": "http://localhost:11434",
                "active": True,
                "prompts": [
                    {
                        "name": "Prompt Importado",
                        "description": "Descrição do prompt",
                        "content": "Conteúdo de teste",
                    }
                ],
            }
        ]
    }

    response = client.post("/api/v1/agents/import", json=payload["agents"])
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "ok"
    assert data["stats"]["created"] >= 1
