# privata/chat_modern.py

import sys
sys.path.append('src/core')
sys.path.append('src/retrieval')
sys.path.append('src/models')

from config import Config
from modern_vectordb import vector_db
from multi_modal_embedder import multi_modal_embedder
from reranker import reranker
from llm_loader import run_llm
import json
from datetime import datetime
from typing import Any, List, Dict

class ModernChatSystem:
    """Hybrid RAG + Augmented LLM chat system"""

    def __init__(self):
        self.top_k = 15  # increase retrieval depth
        self.chunk_max_length = 3000
        self.augmentation_threshold = 0.05
        self.max_extra_tokens = 400
        self.prompt_template = Config.chat["prompt_template"]

        self.session_memory: Dict[str, List[Dict[str, str]]] = {}

    def retrieve_relevant_docs(self, query: str) -> List[Dict[str, Any]]:
        query_embedding = multi_modal_embedder.embed_query(query)
        initial_results = vector_db.query_similar_docs(query_embedding, top_k=self.top_k * 3)
        reranked_results = reranker.hybrid_rerank(query, query_embedding, initial_results, top_k=self.top_k)
        final_results = reranker.remove_duplicates(reranked_results)
        print(f"[CHAT] Retrieved {len(final_results)} relevant documents")
        return final_results

    def format_context_with_citations(self, results: List[Dict[str, Any]]) -> str:
        context_parts = []
        for i, result in enumerate(results):
            content = result.get("content", "")[:self.chunk_max_length]
            metadata = result.get("metadata", {})
            source_file = metadata.get("source_file", "Unknown source")
            section_title = metadata.get("section_title", "")
            chunk_info = f"Chunk {metadata.get('chunk_index', 0)}/{metadata.get('total_chunks', 1)}"
            citation = f"[Source: {source_file}"
            if section_title:
                citation += f", Section: {section_title}"
            citation += f", {chunk_info}]"
            score = result.get("score")
            if score is not None:
                citation += f" (Relevance: {score:.3f})"
            context_parts.append(f"{content}\n{citation}")
        return "\n---\n".join(context_parts)

    def _should_augment(self, results: List[Dict[str, Any]]) -> bool:
        if not results:
            return False
        avg_score = sum(r.get("score", 0) for r in results) / len(results)
        return avg_score >= self.augmentation_threshold

    def build_grounded_prompt(self, query: str, context: str, augment: bool = False) -> str:
        instructions = """Based on the provided context, provide a detailed answer.
IMPORTANT:
1. Use information from context primarily.
2. Cite all sources as shown.
3. If context is insufficient, indicate it clearly.
4. Provide factual, precise answers.
"""
        if augment:
            instructions += f"\n5. You may supplement the answer with general knowledge only if necessary, but limit extra content to {self.max_extra_tokens} tokens."

        template = f"""{instructions}

CONTEXT:
{context}

USER QUESTION: {query}

Please respond with clear citations:"""
        return template

    def generate_response(self, query: str, context: str, augment: bool) -> str:
        prompt = self.build_grounded_prompt(query, context, augment)
        try:
            response = run_llm(prompt)
            if "[Source:" not in response:
                response += "\n\n*Response generated based on retrieved MOSDAC documentation*"
            return response
        except Exception as e:
            return f"I encountered an error while generating a response: {str(e)}"

    def handle_session(self, user_id: str, query: str, response: str, context_results: List[Dict[str, Any]]) -> None:
        if user_id not in self.session_memory:
            self.session_memory[user_id] = []
        self.session_memory[user_id].append({
            "query": query,
            "response": response,
            "sources": [r.get("metadata", {}).get("source_file", "unknown") for r in context_results]
        })
        interaction_data = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_preview": response[:200],
            "sources_count": len(context_results),
            "sources": [r.get("metadata", {}).get("source_file", "unknown") for r in context_results]
        }
        print(f"[SESSION] Interaction logged: {json.dumps(interaction_data, indent=2)}")

    def get_response_quality_metrics(self, query: str, response: str, context_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        metrics = {
            "query_length": len(query),
            "response_length": len(response),
            "sources_used": len(context_results),
            "average_source_score": 0,
            "citation_count": response.count("[Source:"),
            "timestamp": datetime.now().isoformat()
        }
        if context_results:
            scores = [r.get("score", 0) for r in context_results if "score" in r]
            if scores:
                metrics["average_source_score"] = sum(scores) / len(scores)
        return metrics

    def start_chat_loop(self, user_id: str = "default_user"):
        print("\n[CHAT] Modern chat system ready. Type your question or 'exit' to quit.\n")
        while True:
            try:
                query = input("🧠 You: ").strip()
                if not query or query.lower() == "exit":
                    print("[CHAT] Exiting.")
                    break

                context_results = self.retrieve_relevant_docs(query)
                if not context_results:
                    print("\n🤖 AI: No relevant information found.")
                    continue

                context = self.format_context_with_citations(context_results)
                augment = self._should_augment(context_results)
                response = self.generate_response(query, context, augment)

                print(f"\n🤖 AI: {response}\n")
                metrics = self.get_response_quality_metrics(query, response, context_results)
                print(f"[METRICS] {json.dumps(metrics, indent=2)}")
                self.handle_session(user_id, query, response, context_results)

            except KeyboardInterrupt:
                print("\n[CHAT] Interrupted. Goodbye.")
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                print("\n🤖 AI: Encountered an error, please try again.\n")


# Global instance
modern_chat = ModernChatSystem()

def start_modern_chat():
    modern_chat.start_chat_loop()
