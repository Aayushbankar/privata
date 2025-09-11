# privata/chat_modern.py

from config import Config
from retriever.modern_vectordb import vector_db
from retriever.multi_modal_embedder import multi_modal_embedder
from retriever.reranker import reranker
from models.llm_loader import run_llm
import json
from datetime import datetime

class ModernChatSystem:
    """Modern chat system with enhanced retrieval, reranking, and citation-aware responses"""
    
    def __init__(self):
        self.top_k = Config.chat["top_k"]
        self.prompt_template = Config.chat["prompt_template"]
        
    def retrieve_relevant_docs(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant documents with enhanced retrieval"""
        # Embed query
        query_embedding = multi_modal_embedder.embed_query(query)
        
        # Get initial results from vector DB
        initial_results = vector_db.query_similar_docs(query_embedding, top_k=self.top_k * 3)
        
        # Rerank with MMR and cross-encoder
        reranked_results = reranker.hybrid_rerank(
            query, query_embedding, initial_results, top_k=self.top_k
        )
        
        # Remove duplicates
        final_results = reranker.remove_duplicates(reranked_results)
        
        print(f"[CHAT] Retrieved {len(final_results)} relevant documents")
        return final_results
    
    def format_context_with_citations(self, results: List[Dict[str, Any]]) -> str:
        """Format context with proper citations and source information"""
        context_parts = []
        
        for i, result in enumerate(results):
            content = result.get("content", "")[:1000]  # Limit length
            metadata = result.get("metadata", {})
            
            # Build citation information
            source_file = metadata.get("source_file", "Unknown source")
            section_title = metadata.get("section_title", "")
            chunk_info = f"Chunk {metadata.get('chunk_index', 0)}/{metadata.get('total_chunks', 1)}"
            
            citation = f"[Source: {source_file}"
            if section_title:
                citation += f", Section: {section_title}"
            citation += f", {chunk_info}]"
            
            # Add score information if available
            score = result.get("score")
            if score is not None:
                citation += f" (Relevance: {score:.3f})"
            
            context_parts.append(f"{content}\n{citation}")
        
        return "\n---\n".join(context_parts)
    
    def build_grounded_prompt(self, query: str, context: str) -> str:
        """Build prompt with grounding instructions and citation requirements"""
        grounded_template = """Based on the following context information, provide a comprehensive and accurate answer to the user's question. 

IMPORTANT INSTRUCTIONS:
1. ONLY use information from the provided context - do not use external knowledge
2. If the context doesn't contain enough information to answer fully, say so
3. Cite your sources using the provided citation format
4. Be specific and factual - avoid generalizations
5. If discussing missions, dates, or technical details, be precise

CONTEXT:
{context}

USER QUESTION: {query}

Please provide a well-structured response with clear citations:"""
        
        return grounded_template.format(context=context, query=query)
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response with proper grounding and citations"""
        prompt = self.build_grounded_prompt(query, context)
        
        try:
            response = run_llm(prompt)
            
            # Post-process response to ensure citations are properly formatted
            response = self._ensure_citation_formatting(response)
            
            return response
            
        except Exception as e:
            return f"I apologize, but I encountered an error while generating a response: {str(e)}"
    
    def _ensure_citation_formatting(self, response: str) -> str:
        """Ensure citations are properly formatted in the response"""
        # Basic check for citation formatting
        if "[Source:" not in response:
            # Add a general citation note if none found
            response += "\n\n*Response generated based on retrieved documentation from MOSDAC sources*"
        
        return response
    
    def get_response_quality_metrics(self, query: str, response: str, 
                                  context_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate response quality metrics"""
        metrics = {
            "query_length": len(query),
            "response_length": len(response),
            "sources_used": len(context_results),
            "average_source_score": 0,
            "citation_count": response.count("[Source:"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Calculate average source score
        if context_results:
            scores = [r.get("score", 0) for r in context_results if "score" in r]
            if scores:
                metrics["average_source_score"] = sum(scores) / len(scores)
        
        return metrics
    
    def handle_session_context(self, user_id: str, query: str, response: str,
                             context_results: List[Dict[str, Any]]) -> None:
        """Handle session context and history (placeholder for future implementation)"""
        # This would implement proper session management
        # For now, just log the interaction
        interaction_data = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_preview": response[:200],
            "sources_count": len(context_results),
            "sources": [r.get("metadata", {}).get("source_file", "unknown") for r in context_results]
        }
        
        print(f"[SESSION] Interaction logged: {json.dumps(interaction_data, indent=2)}")
    
    def start_chat_loop(self, user_id: str = "default_user"):
        """Run the interactive modern chat loop"""
        print("\n[CHAT] Modern chat system ready. Type your question or 'exit' to quit.\n")
        
        while True:
            try:
                query = input("🧠 You: ").strip()
                if not query or query.lower() == "exit":
                    print("[CHAT] Exiting.")
                    break
                
                # Retrieve relevant documents
                context_results = self.retrieve_relevant_docs(query)
                
                if not context_results:
                    print("\n🤖 AI: I couldn't find relevant information to answer your question.")
                    print("Please try rephrasing or ask about something else.\n")
                    continue
                
                # Format context with citations
                context = self.format_context_with_citations(context_results)
                
                # Generate response
                response = self.generate_response(query, context)
                
                # Display response
                print(f"\n🤖 AI: {response}\n")
                
                # Log interaction and metrics
                metrics = self.get_response_quality_metrics(query, response, context_results)
                print(f"[METRICS] {json.dumps(metrics, indent=2)}")
                
                # Handle session context
                self.handle_session_context(user_id, query, response, context_results)
                
            except KeyboardInterrupt:
                print("\n[CHAT] Interrupted. Goodbye.")
                break
            except Exception as e:
                print(f"[ERROR] Chat error: {e}")
                print("\n🤖 AI: I'm sorry, I encountered an error. Please try again.\n")

# Global instance for easy access
modern_chat = ModernChatSystem()

def start_modern_chat():
    """Start the modern chat system"""
    modern_chat.start_chat_loop()
