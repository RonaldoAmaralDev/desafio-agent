from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "API" in data["message"]