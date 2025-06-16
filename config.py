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
        "top_k": 5,
        "prompt_template": (
            "[CONTEXT START]\n{context}\n[CONTEXT END]\n\n"
            "Question: {query}\nAnswer:"
        ),
        "llm_model": "llama3",
        "temperature": 0.7,
        "streaming": False
    }

    system = {
        "use_gpu": False,
        "log_level": "INFO",
        "language": "en",
        "retry_attempts": 3
    }
