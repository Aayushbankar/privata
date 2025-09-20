# privata/retriever/modern_vectordb.py

import os
import chromadb
from typing import List, Dict, Any
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import sys
sys.path.append('src/core')
from config import Config
import uuid
from datetime import datetime
from typing import Any , List, Dict
class ModernVectorDB:
    """Modern vector database implementation using ChromaDB directly"""
    
    def __init__(self):
        self.persist_dir = Config.ingest["persist_directory"]
        self.collection_name = Config.ingest["collection_name"]
        self.embedding_model = Config.ingest["embedding_model"]
        
        # Create Chroma client with proper settings
        # self.client = chromadb.Client(
        #     Settings(
        #         persist_directory=self.persist_dir,
        #         chroma_db_impl="duckdb+parquet",
        #         anonymized_telemetry=False
        #     )
        # )
        # NEW
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print(f"[INFO] Loaded existing collection: {self.collection_name}")
            return collection
        except Exception:
            collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"created": datetime.now().isoformat()}
            )
            print(f"[INFO] Created new collection: {self.collection_name}")
            return collection
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store with enhanced metadata"""
        if not documents:
            print("[INFO] No documents to add")
            return

        ids, embeddings, metadatas, contents = [], [], [], []

        for doc in documents:
            doc_id = str(uuid.uuid4())
            ids.append(doc_id)
            contents.append(doc["content"])
            embeddings.append(doc["embedding"])
            metadata = doc.get("metadata", {}).copy()
            metadata.update({
                "ingestion_id": doc_id,
                "ingestion_timestamp": datetime.now().isoformat(),
                "content_length": len(doc["content"]),
                "chunk_index": metadata.get("chunk_index", 0),
                "total_chunks": metadata.get("total_chunks", 1)
            })
            metadatas.append(metadata)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=contents
        )

        print(f"[INFO] Added {len(documents)} documents to collection")

    
    def query_similar_docs(self, query_embedding: List[float], top_k: int = 5, 
                          filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query similar documents with filtering capabilities"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters,
                include=["metadatas", "documents", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                # Clamp score within [0,1] for API compatibility
                raw_distance = results["distances"][0][i]
                try:
                    similarity = 1 - float(raw_distance)
                    if similarity < 0.0:
                        similarity = 0.0
                    if similarity > 1.0:
                        similarity = 1.0
                except Exception:
                    similarity = 0.0

                result = {
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": raw_distance,
                    "score": similarity
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"[ERROR] Query failed: {e}")
            return []
    
    def hybrid_search(self, query_embedding: List[float], query_text: str, 
                     top_k: int = 5, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """Hybrid search combining semantic and keyword search"""
        # Semantic search
        semantic_results = self.query_similar_docs(query_embedding, top_k * 2)
        
        # Simple keyword search (could be enhanced with proper keyword search)
        keyword_matches = []
        all_docs = self.collection.get(include=["metadatas", "documents"])
        
        for i, content in enumerate(all_docs["documents"]):
            if query_text.lower() in content.lower():
                keyword_matches.append({
                    "id": all_docs["ids"][i],
                    "content": content,
                    "metadata": all_docs["metadatas"][i],
                    "score": 1.0  # Max score for exact match
                })
        
        # Combine and rerank results
        combined_results = {}
        
        # Add semantic results with weighted scores
        for result in semantic_results:
            combined_results[result["id"]] = {
                **result,
                "combined_score": result["score"] * alpha
            }
        
        # Add keyword results with weighted scores
        for result in keyword_matches:
            if result["id"] in combined_results:
                # Boost existing result
                combined_results[result["id"]]["combined_score"] += (1 - alpha)
            else:
                combined_results[result["id"]] = {
                    **result,
                    "combined_score": (1 - alpha)
                }
        
        # Sort by combined score and return top_k
        sorted_results = sorted(
            combined_results.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )[:top_k]
        
        return sorted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            metadata = self.collection.metadata or {}
            
            return {
                "document_count": count,
                "collection_name": self.collection_name,
                "created": metadata.get("created", "unknown"),
                "embedding_model": self.embedding_model,
                "persist_directory": self.persist_dir
            }
        except Exception as e:
            print(f"[ERROR] Failed to get collection stats: {e}")
            return {}
    
    def reset_collection(self) -> None:
        """Reset the collection (delete all data)"""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"[INFO] Deleted collection: {self.collection_name}")
            
            # Recreate collection
            self.collection = self._get_or_create_collection()
            print(f"[INFO] Recreated collection: {self.collection_name}")
            
        except Exception as e:
            print(f"[ERROR] Failed to reset collection: {e}")
    
    def close(self) -> None:
        """Close the client connection"""
        print("[INFO] Vector database connection closed")


# Global instance for easy access
vector_db = ModernVectorDB()


def get_vector_db_stats() -> Dict[str, Any]:
    """Return API-friendly stats about the vector database.

    Keys:
    - collection_exists: bool
    - document_count: int
    - chunk_count: int (alias of document_count for compatibility)
    - last_ingested: str | None (ISO timestamp)
    """
    try:
        # Verify collection exists by calling count
        count = 0
        last_ingested = None

        try:
            count = vector_db.collection.count()
        except Exception:
            # Collection does not exist or is unavailable
            return {
                "collection_exists": False,
                "document_count": 0,
                "chunk_count": 0,
                "last_ingested": None,
            }

        # Attempt to compute last_ingested by scanning metadata in small batches
        try:
            # Get all metadatas (may be large; chroma get without where/limit may be heavy)
            # Use an incremental approach with pagination if supported; otherwise fall back to single get
            data = vector_db.collection.get(include=["metadatas"], limit=count or 1000)
            metadatas = data.get("metadatas", []) or []
            # Flatten possible nested structure
            if metadatas and isinstance(metadatas[0], list):
                flat = []
                for row in metadatas:
                    flat.extend(row)
                metadatas = flat
            timestamps = []
            for md in metadatas:
                ts = md.get("ingestion_timestamp") if isinstance(md, dict) else None
                if ts:
                    timestamps.append(ts)
            if timestamps:
                last_ingested = max(timestamps)
        except Exception:
            last_ingested = None

        return {
            "collection_exists": True,
            "document_count": int(count or 0),
            "chunk_count": int(count or 0),
            "last_ingested": last_ingested,
        }
    except Exception:
        return {
            "collection_exists": False,
            "document_count": 0,
            "chunk_count": 0,
            "last_ingested": None,
        }
