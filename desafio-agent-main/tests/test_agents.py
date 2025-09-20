import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from app.main import app
from app.db.session import get_db, engine
from app.models import Base, User, Agent

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def db_session():
    db = next(get_db())
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
        owner=create_user
    )
    db_session.add(agent)
    db_session.commit()
    db_session.refresh(agent)
    return agent

def test_list_agents(db_session, create_agent):
    response = client.get("/api/v1/agents/")
    assert response.status_code == 200
    data = response.json()
    assert any(a["id"] == create_agent.id for a in data)