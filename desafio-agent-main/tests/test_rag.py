import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ----------------------
# Tests de RAG
# ----------------------
def test_rag_query(monkeypatch):
    # mock do serviço RAG
    monkeypatch.setattr("app.services.rag.query_rag", lambda q: "Resposta simulada")

    payload = {"question": "Quem descobriu o Brasil?"}
    response = client.post("/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Resposta simulada"


def test_rag_upload(monkeypatch, tmp_path):
    # mock do serviço de indexação
    def fake_index(file):
        return {"status": "success", "indexed_file": file.filename}

    monkeypatch.setattr("app.services.rag_index.index_document", fake_index)

    file_content = "Conteúdo teste".encode("utf-8")
    test_file = tmp_path / "teste.txt"
    test_file.write_bytes(file_content)

    with open(test_file, "rb") as f:
        response = client.post("/rag/upload", files={"file": ("teste.txt", f, "text/plain")})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["indexed_file"] == "teste.txt"
