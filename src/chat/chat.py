# privata/chat_modern.py

import sys
sys.path.append('src/core')
sys.path.append('src/retrieval')
sys.path.append('src/models')
sys.path.append('src/navigation')

from config import Config
from modern_vectordb import vector_db
from multi_modal_embedder import multi_modal_embedder
from reranker import reranker
from llm_loader import run_llm
from navigation_assistant import navigation_assistant
import json
from datetime import datetime
from typing import Any, List, Dict

class ModernChatSystem:
    """Hybrid RAG + Augmented LLM chat system"""

    def __init__(self):
        self.top_k = 10  # reduce for faster responses while keeping quality
        self.chunk_max_length = 3000
        self.augmentation_threshold = 0.05
        self.max_extra_tokens = 400
        self.prompt_template = Config.chat["prompt_template"]

        self.session_memory: Dict[str, List[Dict[str, str]]] = {}

    def _build_intent_prompt(self, user_input: str, recent_history: List[Dict[str, str]]) -> str:
        history_lines = []
        for turn in recent_history[-4:]:
            history_lines.append(f"User: {turn.get('query','')[:200]}")
            history_lines.append(f"Assistant: {turn.get('response','')[:200]}")
        history_text = "\n".join(history_lines)
        return (
            "You are an intent classifier for a MOSDAC help assistant. "
            "Classify the user's message and extract any goals.\n"
            "Intent labels: 'chitchat' (greetings/small talk), 'qa' (fact-seeking about scraped docs), "
            "'info' (general MOSDAC info gathering that may need augmentation), 'command' (actions), 'other'."
        ) + f"\n\nRecent history:\n{history_text}\n\n" + (
            "User message: " + user_input + "\n\n"
            "Respond ONLY in JSON with keys: intent, confidence (0-1), goals (string), entities (string)."
        )

    def detect_intent(self, user_id: str, user_input: str) -> Dict[str, Any]:
        recent_history = self.session_memory.get(user_id, [])
        prompt = self._build_intent_prompt(user_input, recent_history)
        try:
            raw = run_llm(prompt)
            # Best-effort JSON parse
            data = {}
            try:
                data = json.loads(raw)
            except Exception:
                # Attempt to extract JSON substring
                start = raw.find('{')
                end = raw.rfind('}')
                if start != -1 and end != -1 and end > start:
                    data = json.loads(raw[start:end+1])
            intent = (data.get('intent') or 'qa').lower()
            confidence = float(data.get('confidence') or 0.5)
            goals = data.get('goals') or ''
            entities = data.get('entities') or ''
            return {"intent": intent, "confidence": confidence, "goals": goals, "entities": entities}
        except Exception:
            return {"intent": "qa", "confidence": 0.4, "goals": "", "entities": ""}

    def retrieve_relevant_docs(self, query: str) -> List[Dict[str, Any]]:
        query_embedding = multi_modal_embedder.embed_query(query)
        initial_results = vector_db.query_similar_docs(query_embedding, top_k=self.top_k * 3)
        reranked_results = reranker.hybrid_rerank(query, query_embedding, initial_results, top_k=self.top_k)
        final_results = reranker.remove_duplicates(reranked_results)
        print(f"[CHAT] Retrieved {len(final_results)} relevant documents")
        return final_results

    def _average_score(self, results: List[Dict[str, Any]]) -> float:
        if not results:
            return 0.0
        scores = [r.get("score", 0.0) for r in results]
        return sum(scores) / max(1, len(scores))

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

    def build_grounded_prompt(self, query: str, context: str, augment: bool = False, intent_context: str = "", language: str = "en") -> str:
        # Language instruction mapping
        language_instructions = {
            "hi": "आपको हिंदी में उत्तर देना है।",
            "ta": "நீங்கள் தமிழில் பதிலளிக்க வேண்டும்।",
            "te": "మీరు తెలుగులో సమాధానం ఇవ్వాలి।",
            "bn": "আপনাকে বাংলায় উত্তর দিতে হবে।",
            "mr": "तुम्हाला मराठीत उत्तर द्यावे लागेल।",
            "gu": "તમારે ગુજરાતીમાં જવાબ આપવો પડશે।",
            "kn": "ನೀವು ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಬೇಕು।",
            "ml": "നിങ്ങൾ മലയാളത്തിൽ ഉത്തരം നൽകണം।",
            "pa": "ਤੁਹਾਨੂੰ ਪੰਜਾਬੀ ਵਿੱਚ ਜਵਾਬ ਦੇਣਾ ਹੈ।",
            "en": "You must respond in English."
        }
        
        language_instruction = language_instructions.get(language, language_instructions["en"])
        
        instructions = f"""Based on the provided context, provide a detailed answer.
CRITICAL LANGUAGE REQUIREMENT: {language_instruction} REGARDLESS of the language used in the question, you MUST respond ONLY in the specified language.

IMPORTANT:
1. Use information from context primarily.
2. Cite all sources as shown.
3. If context is insufficient, indicate it clearly.
4. Provide factual, precise answers.
5. Respond in PLAIN TEXT only. Do NOT use Markdown, bullet points, bold, italics, code blocks, or links.
6. ALWAYS respond in the specified language: {language_instruction}
"""
        if augment:
            instructions += f"\n7. You may supplement the answer with general knowledge only if necessary, but limit extra content to {self.max_extra_tokens} tokens."

        intent_note = f"\nINTENT CONTEXT: {intent_context}" if intent_context else ""

        template = f"""{instructions}{intent_note}

CONTEXT:
{context}

USER QUESTION: {query}

Please respond with clear citations in the specified language:"""
        return template

    def generate_response(self, query: str, context: str, augment: bool, intent_context: str = "", language: str = "en") -> str:
        prompt = self.build_grounded_prompt(query, context, augment, intent_context, language)
        try:
            response = run_llm(prompt)
            if "[Source:" not in response:
                response += "\n\n*Response generated based on retrieved MOSDAC documentation*"
            return response
        except Exception as e:
            return f"I encountered an error while generating a response: {str(e)}"

    def _build_refine_prompt(self, query: str, rag_answer: str, context: str) -> str:
        return (
            "You are a MOSDAC assistant refining an answer.\n"
            "Inputs: user question, initial RAG answer (with citations), and retrieved context.\n"
            "Tasks:\n"
            "1) Fill gaps using general MOSDAC knowledge if safe, without contradicting context.\n"
            "2) Improve clarity and guidance (what to do next, where to look).\n"
            "3) Repair/add citations to the provided context chunks when applicable.\n"
            "4) If something is outside the provided docs, state it clearly and avoid fabricating MOSDAC-specific facts.\n"
            "Output a final cohesive answer with citations. Respond in PLAIN TEXT only.\n"
            "Do NOT use Markdown, bullet points, bold, italics, code blocks, or links.\n\n"
            f"USER QUESTION:\n{query}\n\n"
            f"INITIAL RAG ANSWER:\n{rag_answer}\n\n"
            f"RETRIEVED CONTEXT:\n{context}\n\n"
            "FINAL IMPROVED ANSWER:"
        )

    def refine_answer(self, query: str, rag_answer: str, context: str) -> str:
        try:
            prompt = self._build_refine_prompt(query, rag_answer, context)
            refined = run_llm(prompt)
            return refined.strip() or rag_answer
        except Exception:
            return rag_answer

    def _build_smalltalk_prompt(self, user_input: str) -> str:
        return (
            "You are a friendly MOSDAC help assistant. If the user greets or makes small talk, "
            "respond naturally, briefly, and offer assistance about MOSDAC data, satellites, and tools. "
            "Do not fabricate MOSDAC-specific facts if not asked. Respond in PLAIN TEXT only. Do NOT use Markdown, bullet points, bold, italics, code blocks, or links.\n\n"
            f"User: {user_input}\nAssistant:"
        )

    def handle_smalltalk(self, user_input: str) -> str:
        try:
            return run_llm(self._build_smalltalk_prompt(user_input))
        except Exception as e:
            return f"Hello! I can help you with MOSDAC data and tools. (engine error: {e})"

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
    
    def _format_navigation_response(self, navigation_guidance: Dict[str, Any]) -> str:
        """Format navigation guidance into a user-friendly response"""
        path = navigation_guidance.get("navigation_path", {})
        steps = path.get("steps", [])
        
        if not steps:
            return "I can help you navigate MOSDAC, but I need more specific information about what you're looking for."
        
        response = f"🧭 **Navigation Guide: {path.get('goal', 'MOSDAC Portal')}**\n\n"
        response += f"**Estimated time:** {path.get('estimated_time', 0)} seconds | **Difficulty:** {path.get('difficulty', 'Medium')}\n\n"
        
        for i, step in enumerate(steps[:3], 1):  # Show first 3 steps for brevity
            response += f"**Step {i}:** {step.get('description', '')}\n"
            response += f"→ {step.get('action', '')}\n\n"
        
        if len(steps) > 3:
            response += f"... and {len(steps) - 3} more steps.\n\n"
        
        # Add quick tips
        tips = navigation_guidance.get("quick_tips", [])
        if tips:
            response += "💡 **Quick Tips:**\n"
            for tip in tips[:2]:  # Show first 2 tips
                response += f"• {tip}\n"
        
        return response

    def start_chat_loop(self, user_id: str = "default_user"):
        print("\n[CHAT] Modern chat system ready. Type your question or 'exit' to quit.\n")
        while True:
            try:
                query = input("🧠 You: ").strip()
                if not query or query.lower() == "exit":
                    print("[CHAT] Exiting.")
                    break

                # Stage 1: Check for navigation intent first
                nav_intent, nav_confidence = navigation_assistant.detect_navigation_intent(query)
                
                if nav_confidence > 0.6:  # High confidence navigation request
                    navigation_guidance = navigation_assistant.get_navigation_guidance(query)
                    nav_response = self._format_navigation_response(navigation_guidance)
                    print(f"\n🧭 Navigation Assistant: {nav_response}\n")
                    self.handle_session(user_id, query, nav_response, [])
                    continue
                
                # Stage 2: Detect general intent and possibly handle small talk
                intent_info = self.detect_intent(user_id, query)
                intent = intent_info.get("intent", "qa")
                intent_conf = intent_info.get("confidence", 0.0)
                intent_ctx = \
                    f"intent={intent}, confidence={intent_conf:.2f}, goals={intent_info.get('goals','')}, entities={intent_info.get('entities','')}"

                if intent in ("chitchat", "other") and intent_conf >= 0.5:
                    smalltalk_reply = self.handle_smalltalk(query)
                    print(f"\n🤖 AI: {smalltalk_reply}\n")
                    # Log and continue without RAG
                    self.handle_session(user_id, query, smalltalk_reply, [])
                    continue

                # Stage 3: RAG retrieval for QA/command/info
                context_results = self.retrieve_relevant_docs(query)

                context = self.format_context_with_citations(context_results)
                augment = self._should_augment(context_results)
                # If no context, fall back to small talk/general answer
                if not context_results:
                    fallback = self.handle_smalltalk(query)
                    print(f"\n🤖 AI: {fallback}\n")
                    metrics = self.get_response_quality_metrics(query, fallback, context_results)
                    print(f"[METRICS] {json.dumps(metrics, indent=2)}")
                    self.handle_session(user_id, query, fallback, context_results)
                    continue

                # First-pass RAG answer
                response = self.generate_response(query, context, augment, intent_ctx, language="en")

                # Decide whether to run refinement pass (info-gathering or weak relevance)
                avg_score = self._average_score(context_results)
                if (intent == "info" and intent_conf >= 0.5) or avg_score < max(0.12, self.augmentation_threshold):
                    response = self.refine_answer(query, response, context)

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
