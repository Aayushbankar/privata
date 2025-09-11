# privata/main.py

from models.llm_loader import ensure_ollama_running
from ingest import run_ingestion
from chat import start_chat_loop
from ingest_modern import run_modern_ingestion
from chat_modern import start_modern_chat

def show_menu():
    print("\n==== PRIVATA MENU ====")
    print("[1] Ingest Documents (Legacy)")
    print("[2] Start Chatbot (Legacy)")
    print("[3] Modern Ingestion")
    print("[4] Modern Chatbot")
    print("[5] Exit")

def run_menu():
    while True:
        show_menu()
        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            path = input("Enter path to documents: ").strip()
            run_ingestion(path)
        elif choice == "2":
            start_chat_loop()
        elif choice == "3":
            path = input("Enter path to documents: ").strip()
            run_modern_ingestion(path)
        elif choice == "4":
            start_modern_chat()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__": 
    try:
        ensure_ollama_running()
        run_menu()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
    except Exception as e:
        print(f"[ERROR] {e}")
