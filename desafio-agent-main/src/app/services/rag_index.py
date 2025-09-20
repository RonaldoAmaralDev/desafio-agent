import os
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.docstore.document import Document
from fastapi import UploadFile
from pypdf import PdfReader


def process_file(file: UploadFile) -> str:
    """Extrai texto de PDF, TXT ou Markdown."""
    content = ""
    if file.filename.endswith(".pdf"):
        pdf = PdfReader(file.file)
        for page in pdf.pages:
            content += page.extract_text() or ""
    elif file.filename.endswith(".txt") or file.filename.endswith(".md"):
        content = file.file.read().decode("utf-8")
    else:
        raise ValueError("Formato de arquivo não suportado")
    return content


def index_document(file: UploadFile, persist_dir: str = "./chroma_db"):
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

    # Embeddings
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)

    # Banco vetorial
    db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    # Extrair conteúdo
    text = process_file(file)
    doc = Document(page_content=text, metadata={"filename": file.filename})

    # Indexar no Chroma
    db.add_documents([doc])
    db.persist()

    return {"status": "success", "indexed_file": file.filename}