# privata/ingest.py

from config import Config
from utils.doc_loader import load_documents
from retriever.embedder import embed_texts
from retriever.vectordb import get_vector_store, add_documents_to_store
from langchain.text_splitter import RecursiveCharacterTextSplitter



def chunk_documents(documents):
    """
    Splits documents into chunks using LangChain's recursive splitter.
    """
    if not documents:
        print("[INFO] No documents found to chunk.")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.ingest["chunk_size"],
        chunk_overlap=Config.ingest["chunk_overlap"]
    )

    chunks = splitter.split_documents(documents)
    print(f"[INFO] Chunked {len(documents)} docs into {len(chunks)} chunks.")
    return chunks


def embed_chunks(chunks):
    """
    Extracts text content from chunks and generates embeddings.
    """
    texts = [doc.page_content for doc in chunks]
    return embed_texts(texts)


def attach_embeddings_to_chunks(chunks, embeddings):
    """
    Rebuilds Document objects with associated embeddings (metadata only).
    """
    for i in range(len(chunks)):
        chunks[i].metadata["embedding"] = embeddings[i]
    return chunks


def run_ingestion(path: str):
    """
    Full ingestion pipeline: load → chunk → embed → store.
    """
    print(f"[INGEST] Starting ingestion for: {path}")
    docs = load_documents(path)
    chunks = chunk_documents(docs)
    embeddings = embed_chunks(chunks)
    store = get_vector_store()
    add_documents_to_store(store, chunks)
    print("[INGEST] Ingestion complete.")
