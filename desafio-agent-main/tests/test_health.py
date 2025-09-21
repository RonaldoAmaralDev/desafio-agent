import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.services.health_service import HealthService

client = TestClient(app)


class DummyDB:
    """Simula uma conexão de banco de dados."""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def execute(self, query):
        if self.should_fail:
            raise Exception("DB falhou")
        return 1


class DummyRedis:
    """Simula o Redis client."""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def ping(self):
        if self.should_fail:
            raise Exception("Redis falhou")
        return True


class DummyOpenAI:
    """Simula a API da OpenAI."""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def list_models(self):
        if self.should_fail:
            raise Exception("OpenAI falhou")
        return ["gpt-4o"]


@pytest.fixture
def health_service(monkeypatch):
    service = HealthService()

    # mock do Redis
    monkeypatch.setattr("app.services.health_service.redis_client", DummyRedis())

    # mock da OpenAI
    monkeypatch.setattr("openai.models.list", lambda: ["gpt-4o"])

    return service


def test_health_ok(monkeypatch, health_service):
    # DB OK
    db = DummyDB()
    status = health_service.check(db)

    assert status["status"] == "ok"
    assert status["database"] == "ok"
    assert status["redis"] == "ok"
    assert status["openai"] == "ok"


def test_health_db_fail(monkeypatch, health_service):
    db = DummyDB(should_fail=True)
    status = health_service.check(db)

    assert status["status"] == "error"
    assert status["database"] == "Indisponível"


def test_health_redis_fail(monkeypatch):
    service = HealthService()
    monkeypatch.setattr("app.services.health_service.redis_client", DummyRedis(should_fail=True))
    monkeypatch.setattr("openai.models.list", lambda: ["gpt-4o"])

    db = DummyDB()
    status = service.check(db)

    assert status["status"] == "error"
    assert status["redis"] == "Indisponível"


def test_health_openai_fail(monkeypatch):
    service = HealthService()
    monkeypatch.setattr("app.services.health_service.redis_client", DummyRedis())
    monkeypatch.setattr("openai.models.list", lambda: (_ for _ in ()).throw(Exception("OpenAI falhou")))

    db = DummyDB()
    status = service.check(db)

    assert status["status"] == "error"
    assert status["openai"] == "Indisponível"
