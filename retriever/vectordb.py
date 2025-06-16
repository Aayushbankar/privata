# privata/retriever/vectordb.py

import os
from typing import List
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from config import Config
from retriever.embedder import _embedder



def get_vector_store() -> Chroma:
    """
    Initializes or loads the Chroma vector store.
    """
    persist_dir = Config.ingest["persist_directory"]
    collection = Config.ingest["collection_name"]

    return Chroma(
        collection_name=collection,
        embedding_function=_embedder,
        persist_directory=persist_dir
    )


def add_documents_to_store(store: Chroma, docs: List[Document]) -> None:
    """
    Adds documents to the Chroma vector store and persists them.
    """
    if not docs:
        print("[INFO] No documents to store.")
        return
    store.add_documents(docs)
    store.persist()


def retrieve_similar_docs(store: Chroma, query_vector: List[float], top_k: int) -> List[Document]:
    """
    Retrieves top-k most similar documents for a given query embedding.
    """
    return store.similarity_search_by_vector(query_vector, k=top_k)


def reset_vector_store():
    """
    Deletes the persisted Chroma DB for a clean reset.
    """
    persist_dir = Config.ingest["persist_directory"]
    if os.path.exists(persist_dir):
        for f in os.listdir(persist_dir):
            os.remove(os.path.join(persist_dir, f))
        print(f"[INFO] Vector store reset: {persist_dir}")
    else:
        print("[INFO] No vector store found to reset.")
