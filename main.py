# privata/main.py

from models.llm_loader import ensure_ollama_running
from ingest import run_ingestion
from chat import start_chat_loop

def show_menu():
    print("\n==== PRIVATA MENU ====")
    print("[1] Ingest Documents")
    print("[2] Start Chatbot")
    print("[3] Exit")

def run_menu():
    while True:
        show_menu()
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            path = input("Enter path to documents: ").strip()
            run_ingestion(path)
        elif choice == "2":
            start_chat_loop()
        elif choice == "3":
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
