import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.app.main import app
from uuid import uuid4
from app.models import Base, User, Prompt
from app.db.session import get_db, engine, SessionLocal

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

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
def create_prompt(db_session):
    prompt = Prompt(
        name="Teste de prompt",
        content="Teste de prompt"
    )
    db_session.add(prompt)
    db_session.commit()
    return prompt

def test_list_prompts(db_session, create_prompt):
    response = client.get("/api/v1/prompts/")
    assert response.status_code == 200
    data = response.json()
    assert any(p["id"] == create_prompt.id for p in data)