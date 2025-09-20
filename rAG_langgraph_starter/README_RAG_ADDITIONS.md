## RAG + LangGraph quickstart (added files)
- `rAG_langgraph_starter/scripts/ingest_documents.py` : ingest docs into Chroma using OpenAI embeddings
- `rAG_langgraph_starter/services/rag.py` : simple query_rag function using LangChain/OpenAI/Chroma
- `rAG_langgraph_starter/langgraph_flow.yaml` : conceptual LangGraph flow to orchestrate retriever + LLM
- Docker Compose snippet to run Chroma locally (add to your `docker-compose.yml`)

Steps:
1. Install dependencies: `pip install langchain chromadb openai tiktoken`
2. Set `OPENAI_API_KEY` environment variable.
3. Put documents into `knowledge_base/` and run:
   `python rAG_langgraph_starter/scripts/ingest_documents.py --input knowledge_base --persist_dir chroma_db`
4. Start your app and call the RAG endpoint which will import `rAG_langgraph_starter/services/rag.py` and use `query_rag`.