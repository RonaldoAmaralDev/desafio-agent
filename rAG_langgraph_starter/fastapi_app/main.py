from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from services import rag, rag_index  # novo módulo que criaremos
import uvicorn

app = FastAPI(title="RAG Assistant API")

# ---- MODELS ----
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

class UploadResponse(BaseModel):
    status: str
    indexed_file: str | None = None
    detail: str | None = None


# ---- ENDPOINTS ----
@app.post("/api/assistant/query", response_model=QueryResponse)
def assistant_query(payload: QueryRequest):
    try:
        result = rag.query_rag(payload.question)
        return {"answer": result}
    except Exception as e:
        return {"answer": f"Erro ao processar a query: {e}"}


@app.post("/api/assistant/upload", response_model=UploadResponse)
async def assistant_upload(file: UploadFile = File(...)):
    """
    Endpoint para receber um documento (PDF, TXT, Markdown),
    extrair o conteúdo e indexar no ChromaDB.
    """
    try:
        result = rag_index.index_document(file)
        return result
    except Exception as e:
        return {"status": "error", "detail": str(e), "indexed_file": None}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
