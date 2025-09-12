# privata/retriever/reranker.py

from typing import List, Dict, Any
import numpy as np
from sentence_transformers import CrossEncoder
from retriever.multi_modal_embedder import multi_modal_embedder
from typing import Any , List, Dict
class Reranker:
    """Reranking system with MMR and cross-encoder capabilities"""
    
    def __init__(self):
        self.cross_encoder = None
        self._initialize_cross_encoder()
    
    def _initialize_cross_encoder(self):
        """Initialize cross-encoder model for reranking"""
        try:
            # Using a small, efficient cross-encoder model
            self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            print("[INFO] Cross-encoder model initialized")
        except Exception as e:
            print(f"[WARNING] Failed to initialize cross-encoder: {e}")
            print("[INFO] Using similarity-based reranking only")
    
    def mmr_rerank(self, query_embedding: List[float], results: List[Dict[str, Any]], 
                  lambda_param: float = 0.7, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Maximal Marginal Relevance reranking
        Balances relevance and diversity
        """
        if not results:
            return []
        
        # Calculate similarity to query
        for result in results:
            result["similarity_to_query"] = multi_modal_embedder.calculate_similarity(
                query_embedding, result.get("embedding", [])
            )
        
        selected = []
        remaining = results.copy()
        
        # First, select the most relevant document
        if remaining:
            most_relevant = max(remaining, key=lambda x: x["similarity_to_query"])
            selected.append(most_relevant)
            remaining.remove(most_relevant)
        
        # Continue selecting documents with MMR
        while remaining and len(selected) < top_k:
            mmr_scores = []
            
            for doc in remaining:
                # Relevance score
                relevance = doc["similarity_to_query"]
                
                # Max similarity to already selected documents
                max_similarity = 0
                if selected:
                    for sel_doc in selected:
                        similarity = multi_modal_embedder.calculate_similarity(
                            doc.get("embedding", []),
                            sel_doc.get("embedding", [])
                        )
                        max_similarity = max(max_similarity, similarity)
                
                # MMR score
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_similarity
                mmr_scores.append((mmr_score, doc))
            
            # Select document with highest MMR score
            if mmr_scores:
                best_score, best_doc = max(mmr_scores, key=lambda x: x[0])
                selected.append(best_doc)
                remaining.remove(best_doc)
        
        return selected
    
    def cross_encoder_rerank(self, query: str, results: List[Dict[str, Any]], 
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """Rerank using cross-encoder for better precision"""
        if not self.cross_encoder or not results:
            return results[:top_k]
        
        # Prepare pairs for cross-encoder
        pairs = []
        for result in results:
            content = result.get("content", "")[:512]  # Limit length for cross-encoder
            pairs.append((query, content))
        
        try:
            # Get cross-encoder scores
            scores = self.cross_encoder.predict(pairs)
            
            # Update results with cross-encoder scores
            for i, result in enumerate(results):
                result["cross_encoder_score"] = float(scores[i])
            
            # Sort by cross-encoder score
            reranked = sorted(results, key=lambda x: x.get("cross_encoder_score", 0), reverse=True)
            return reranked[:top_k]
            
        except Exception as e:
            print(f"[ERROR] Cross-encoder reranking failed: {e}")
            return results[:top_k]
    
    def hybrid_rerank(self, query: str, query_embedding: List[float], 
                    results: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Hybrid reranking combining MMR and cross-encoder"""
        if not results:
            return []
        
        # First pass: MMR for diversity
        mmr_results = self.mmr_rerank(query_embedding, results, top_k=top_k * 2)
        
        # Second pass: Cross-encoder for precision
        if self.cross_encoder:
            final_results = self.cross_encoder_rerank(query, mmr_results, top_k=top_k)
        else:
            final_results = mmr_results[:top_k]
        
        return final_results
    
    def remove_duplicates(self, results: List[Dict[str, Any]], 
                         similarity_threshold: float = 0.95) -> List[Dict[str, Any]]:
        """Remove near-duplicate results based on content similarity"""
        unique_results = []
        seen_embeddings = []
        
        for result in results:
            embedding = result.get("embedding", [])
            
            # Check if this is similar to any seen result
            is_duplicate = False
            for seen_embedding in seen_embeddings:
                similarity = multi_modal_embedder.calculate_similarity(embedding, seen_embedding)
                if similarity > similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_results.append(result)
                seen_embeddings.append(embedding)
        
        return unique_results
    
    def rerank_with_filters(self, results: List[Dict[str, Any]], 
                          filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Rerank results with optional filters"""
        if not filters or not results:
            return results
        
        filtered_results = []
        
        for result in results:
            metadata = result.get("metadata", {})
            matches_all = True
            
            for key, value in filters.items():
                if key in metadata:
                    if isinstance(value, list):
                        if metadata[key] not in value:
                            matches_all = False
                            break
                    else:
                        if metadata[key] != value:
                            matches_all = False
                            break
                else:
                    matches_all = False
                    break
            
            if matches_all:
                filtered_results.append(result)
        
        return filtered_results
    
    def get_reranking_stats(self, original_results: List[Dict[str, Any]], 
                          reranked_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the reranking process"""
        if not original_results:
            return {}
        
        return {
            "original_count": len(original_results),
            "reranked_count": len(reranked_results),
            "top_original_score": max((r.get("score", 0) for r in original_results), default=0),
            "top_reranked_score": max((r.get("score", 0) for r in reranked_results), default=0),
            "average_original_score": np.mean([r.get("score", 0) for r in original_results]),
            "average_reranked_score": np.mean([r.get("score", 0) for r in reranked_results]),
            "duplicates_removed": len(original_results) - len(self.remove_duplicates(original_results))
        }

# Global instance for easy access
reranker = Reranker()
