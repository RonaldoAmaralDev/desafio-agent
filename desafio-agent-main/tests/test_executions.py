import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.app.models.execution import Execution
from src.app.models.agent import Agent
from src.app.models.user import User
from app.db.session import get_db, engine
from src.app.main import app
from uuid import uuid4

client = TestClient(app)

@pytest.fixture
def db_session():
    db: Session = next(get_db())
    yield db
    db.rollback()

@pytest.fixture
def create_user(db_session):
    user = User(
        name="Test User",
        email=f"user_{uuid4()}@example.com",
        password="123"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def create_agent(db_session, create_user):
    agent = Agent(
        name="Agent Test",
        model="gpt-3.5-turbo",
        temperature=0.5,
        owner_id=create_user.id
    )
    db_session.add(agent)
    db_session.commit()
    return agent

@pytest.fixture
def create_execution(db_session, create_agent):
    execution = Execution(
        agent_id=create_agent.id,
        input="Test input",
        output="Test output"
    )
    db_session.add(execution)
    db_session.commit()
    db_session.refresh(execution)
    return execution

def test_create_execution(db_session, create_execution):
    response = client.get("/api/v1/executions/")
    assert response.status_code == 200
    data = response.json()
    assert any(a["id"] == create_execution.id for a in data)