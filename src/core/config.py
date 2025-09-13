# privata/config.py

class Config:
    ingest = {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "persist_directory": "./db",
        "collection_name": "privata_knowledge_base"
    }

    chat = {
    "top_k": 15,                      # Increase retrieval depth
    "prompt_template": "...",
    "llm_model": "gemini-2.5-flash",
    "temperature": 0.3,               # Lower for factual accuracy
    "streaming": False,
    "hybrid_rag_enabled": True,
    "similarity_threshold": 0.05,     # Use for deciding augmentation
    "max_augmentation_tokens": 400    # Allow more tokens for completeness
}



    system = {
        "use_gpu": False,
        "log_level": "INFO",
        "language": "en",
        "retry_attempts": 3
    }
