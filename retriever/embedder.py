# privata/retriever/embedder.py



from typing import List
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from config import Config


# Initialize embedder once at module level
_embedder = HuggingFaceEmbeddings(
    model_name=Config.ingest["embedding_model"]
)

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embeds a list of text chunks and returns their vector representations.
    """
    return _embedder.embed_documents(texts)

def embed_query(query: str) -> List[float]:
    """
    Embeds a single user query.
    """
    return _embedder.embed_query(query)
# ks="AIzaSyAAE2yhNVeOBZiZW3D0XslLPJbJZMF2F3o" 