# privata/chat.py

from config import Config
from retriever.vectordb import get_vector_store, retrieve_similar_docs
from retriever.embedder import embed_query
from models.llm_loader import run_llm



def format_context(context_docs):
    """
    Combines top-k retrieved documents into a single context string.
    """
    return "\n---\n".join([doc.page_content for doc in context_docs])


def build_prompt(user_query: str, context: str) -> str:
    """
    Injects retrieved context and user query into the prompt template.
    """
    template = Config.chat["prompt_template"]
    return template.format(context=context, query=user_query)


def start_chat_loop():
    """
    Runs the interactive chat loop.
    """
    print("\n[CHAT] Ready. Type your question or 'exit' to quit.\n")
    store = get_vector_store()

    while True:
        try:
            query = input("🧠 You: ").strip()
            if not query or query.lower() == "exit":
                print("[CHAT] Exiting.")
                break

            q_vec = embed_query(query)
            docs = retrieve_similar_docs(store, q_vec, Config.chat["top_k"])
            context = format_context(docs)
            prompt = build_prompt(query, context)
            response = run_llm(prompt)

            print("\n🤖 AI:", response, "\n")

        except KeyboardInterrupt:
            print("\n[CHAT] Interrupted. Goodbye.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
