"""Ingest documents into Chroma vector DB using OpenAI embeddings.
Usage: python ingest_documents.py --input ./knowledge_base --persist_dir ./chroma_db
"""
import argparse, os, glob
from pathlib import Path

def main(input_dir, persist_dir):
    try:
        from langchain.document_loaders import TextLoader, PyPDFLoader, UnstructuredFileLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import Chroma
    except Exception as e:
        print("Missing dependencies. Install langchain, chromadb, openai: pip install langchain chromadb openai")
        raise

    docs = []
    for p in Path(input_dir).rglob('*'):
        if p.suffix.lower() in ['.txt', '.md']:
            loader = TextLoader(str(p), encoding='utf-8')
        elif p.suffix.lower() in ['.pdf']:
            loader = PyPDFLoader(str(p))
        else:
            continue
        loaded = loader.load()
        docs.extend(loaded)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"Prepared {len(chunks)} chunks for ingestion")

    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
    vectordb.persist()
    print("Ingestion completed. Persisted to:", persist_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='./knowledge_base')
    parser.add_argument('--persist_dir', default='./chroma_db')
    args = parser.parse_args()
    main(args.input, args.persist_dir)