# privata/retriever/embedder.py



from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
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
