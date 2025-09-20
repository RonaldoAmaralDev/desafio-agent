from fastapi import FastAPI
from pydantic import BaseModel
from services import rag
import uvicorn

app = FastAPI(title="RAG Assistant API")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/api/assistant/query", response_model=QueryResponse)
def assistant_query(payload: QueryRequest):
    try:
        result = rag.query_rag(payload.question)
        return {"answer": result}
    except Exception as e:
        return {"answer": f"Erro ao processar a query: {e}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
