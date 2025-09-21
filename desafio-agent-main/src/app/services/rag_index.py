import os
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.docstore.document import Document
from fastapi import UploadFile
from pypdf import PdfReader
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

def process_file(file: UploadFile) -> str:
    """Extrai texto de PDF, TXT ou Markdown."""
    content = ""
    if file.filename.endswith(".pdf"):
        pdf = PdfReader(file.file)
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            content += page_text
            logger.debug(f"Página {page_num} extraída ({len(page_text)} chars)")
    elif file.filename.endswith((".txt", ".md")):
        content = file.file.read().decode("utf-8")
    else:
        logger.error(f"Formato de arquivo não suportado: {file.filename}")
        raise ValueError("Formato de arquivo não suportado")
    return content


def index_document(file: UploadFile, persist_dir: str = None):
    ollama_url = settings.OLLAMA_BASE_URL
    persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR

    embeddings = OllamaEmbeddings(
        model=settings.OLLAMA_EMBED_MODEL,
        base_url=ollama_url
    )

    db = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )

    text = process_file(file)
    doc = Document(
        page_content=text,
        metadata={"filename": file.filename}
    )

    db.add_documents([doc])
    db.persist()

    logger.info(f"Documento indexado: {file.filename} ({len(text)} chars)")
    return {"status": "success", "indexed_file": file.filename}
