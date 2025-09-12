# privata/retriever/multi_modal_embedder.py

from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from config import Config
from typing import Any , List, Dict
class MultiModalEmbedder:
    """Multi-modal embedding system with specialized embeddings for different content types"""
    
    def __init__(self):
        self.embedding_models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize different embedding models for different content types"""
        base_model = Config.ingest["embedding_model"]
        
        # Base model for general content
        self.embedding_models["content"] = SentenceTransformer(base_model)
        
        # Specialized models (could be optimized for different content types)
        # For now using the same model but with different preprocessing
        self.embedding_models["title"] = SentenceTransformer(base_model)
        self.embedding_models["metadata"] = SentenceTransformer(base_model)
        self.embedding_models["table"] = SentenceTransformer(base_model)
        
        print(f"[INFO] Initialized multi-modal embedder with base model: {base_model}")
    
    def _preprocess_content(self, content: str, content_type: str) -> str:
        """Preprocess content based on its type for better embeddings"""
        if content_type == "title":
            # For titles, keep concise and clean
            return content.strip().replace('\n', ' ').replace('\t', ' ')[:200]
        
        elif content_type == "metadata":
            # For metadata, create a structured representation
            if isinstance(content, dict):
                # Convert dict to key-value string
                return " ".join([f"{k}:{v}" for k, v in content.items() if v])
            return str(content).strip()
        
        elif content_type == "table":
            # For tables, create a flattened representation
            if isinstance(content, list):
                # Flatten table rows
                return " | ".join([" ".join(map(str, row)) for row in content])
            return content.strip()
        
        else:  # content_type == "content"
            # For general content, clean and normalize
            return content.strip().replace('\n', ' ').replace('\t', ' ')[:1000]
    
    def embed_content(self, content: Any, content_type: str = "content") -> List[float]:
        """Embed content with type-specific processing"""
        processed_content = self._preprocess_content(content, content_type)
        
        if content_type in self.embedding_models:
            embedding = self.embedding_models[content_type].encode(
                processed_content, 
                convert_to_tensor=False
            )
            return embedding.tolist()
        else:
            # Fallback to content model
            embedding = self.embedding_models["content"].encode(
                processed_content,
                convert_to_tensor=False
            )
            return embedding.tolist()
    
    def embed_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Create multiple embeddings for different parts of a document"""
        embeddings = {}
        
        # Embed main content
        if "content" in document:
            embeddings["content"] = self.embed_content(
                document["content"], "content"
            )
        
        # Embed title if available
        if document.get("metadata", {}).get("title"):
            embeddings["title"] = self.embed_content(
                document["metadata"]["title"], "title"
            )
        
        # Embed metadata
        if "metadata" in document:
            embeddings["metadata"] = self.embed_content(
                document["metadata"], "metadata"
            )
        
        # Embed tables if available
        if document.get("metadata", {}).get("parsed_tables"):
            table_content = document["metadata"]["parsed_tables"]
            embeddings["table"] = self.embed_content(
                table_content, "table"
            )
        
        # Set primary embedding (content as default)
        document["embedding"] = embeddings.get("content", [])
        document["embeddings"] = embeddings
        
        return document
    
    def embed_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Embed multiple documents with multi-modal approach"""
        embedded_docs = []
        
        for doc in documents:
            try:
                embedded_doc = self.embed_document(doc)
                embedded_docs.append(embedded_doc)
            except Exception as e:
                print(f"[ERROR] Failed to embed document: {e}")
                # Fallback: use content-only embedding
                if "content" in doc:
                    try:
                        doc["embedding"] = self.embed_content(doc["content"], "content")
                        embedded_docs.append(doc)
                    except Exception as fallback_error:
                        print(f"[ERROR] Fallback embedding also failed: {fallback_error}")
        
        print(f"[INFO] Embedded {len(embedded_docs)} documents with multi-modal approach")
        return embedded_docs
    
    def embed_query(self, query: str, query_type: str = None) -> List[float]:
        """Embed a query with optional type-specific processing"""
        if query_type and query_type in self.embedding_models:
            return self.embed_content(query, query_type)
        else:
            # Auto-detect query type
            if len(query.split()) <= 3:  # Short query, likely title/metadata
                return self.embed_content(query, "title")
            elif any(keyword in query.lower() for keyword in ["table", "chart", "data"]):
                return self.embed_content(query, "table")
            else:
                return self.embed_content(query, "content")
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Normalize vectors
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (norm1 * norm2)
        return float(similarity)
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding models"""
        stats = {
            "available_models": list(self.embedding_models.keys()),
            "base_model": Config.ingest["embedding_model"],
            "embedding_dimensions": {}
        }
        
        for model_name, model in self.embedding_models.items():
            try:
                # Get embedding dimension from model
                test_embedding = model.encode("test", convert_to_tensor=False)
                stats["embedding_dimensions"][model_name] = len(test_embedding)
            except Exception:
                stats["embedding_dimensions"][model_name] = "unknown"
        
        return stats

# Global instance for easy access
multi_modal_embedder = MultiModalEmbedder()
