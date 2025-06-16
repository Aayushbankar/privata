
# PRIVATA

Privata is a lightweight, offline-first document ingestion and querying tool that uses local embeddings and cloud-based LLMs (Google Gemini) to answer questions from your private files — with no server, no browser, and no GPU required.

It follows the RAG (Retrieval-Augmented Generation) architecture and runs entirely via CLI. Users can ingest PDFs, markdown, and text files, then interact with them using AI-powered semantic search.

---

## ✅ Core Features

- 📁 Ingest local `.pdf`, `.txt`, and `.md` files
- 🧩 Auto-chunks and embeds content using HuggingFace models
- 🔍 Stores vectors in lightweight `ChromaDB`
- 🔄 Retrieves relevant context using vector similarity
- 🤖 Sends context + query to Google Gemini (`gemini-1.5-flash`)
- 🧠 Returns accurate, grounded answers — even for technical PDFs
- 🖥️ Fully CLI-based (no browser or web server needed)
- ⚙️ Configurable via single `config.py` file

---

## 🧠 Architecture (High-Level)

```plaintext
           +------------+         +-------------------+
           |   PDFs     |         |   .txt / .md      |
           +------------+         +-------------------+
                   │
                   ▼
          [ Unstructured Loaders ]
                   │
                   ▼
         [ LangChain Text Splitter ]
                   │
                   ▼
         [ Sentence Transformers ]
                   │
                   ▼
             [ ChromaDB Store ]
                   │
                   ▼
   +--------- User Query (CLI Input) --------+
   |                                         |
   ▼                                         ▼
[ Embed Query ]                     [ Retrieve Top-K Chunks ]
            \______________________/ 
                       │
                       ▼
        [ Gemini Prompt Construction ]
                       │
                       ▼
        [ Google Gemini API (gemini-1.5-flash) ]
                       │
                       ▼
              [ Final Response Output ]
```

---

## ✨ Key Features

- **Offline Ingestion** – Parse and embed your local `.pdf`, `.txt`, and `.md` files entirely offline.
- **RAG Pipeline** – Combines vector similarity search with LLM generation for grounded, context-aware answers.
- **Local Vector DB** – Uses `ChromaDB` for lightweight, persistent local document storage.
- **Cloud LLM (Gemini)** – Uses `gemini-1.5-flash` via Google's `google-generativeai` SDK for high-speed, accurate generation.
- **Modular Architecture** – Cleanly separated modules for ingestion, embeddings, vector DB, and LLM API.
- **CLI Interface** – Run everything from a terminal — no server, browser, or UI required.
- **Configurable** – Customize chunk sizes, models, prompts, and retrieval depth via `config.py`.

---

## 🧭 Use Case Example

You can load 100s of pages of PDF textbooks or technical docs, then ask:

- _"What is Unit 4 in Java?"_
- _"What is the difference between stacks and queues?"_
- _"Summarize the networking protocols chapter."_

Gemini will ground its answer in your actual documents, not public internet.

---

## 🗂️ Project Structure

```plaintext
privata/
├── main.py                # CLI menu entry point
├── ingest.py              # Document ingestion + chunking pipeline
├── chat.py                # Chat loop: query → retrieve → respond
├── config.py              # Central config for models, chunking, prompts
├── requirements.txt       # Dependency list
│
├── models/
│   └── llm_loader.py      # Gemini API integration
│
├── retriever/
│   ├── embedder.py        # HuggingFace embedding logic (MiniLM)
│   └── vectordb.py        # ChromaDB interface for storing & retrieving
│
├── utils/
│   └── doc_loader.py      # Loads & parses PDF, text, markdown files
│
├── db/                    # (Auto-generated) stores vector data
│
├── .env.example           # Sample structure for GEMINI_API_KEY
├── .gitignore             # Ignores pycache, env, vector DB, temp files
└── README.md              # This documentation file
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository and install dependencies

```bash
git clone  https://github.com/Aayushbankar/privata.git
cd privata
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure your Gemini API Key

Obtain your API key from https://ai.google.dev.

Then either:

**Option A: Create a `.env` file**

```bash
cp .env.example .env
```

Inside `.env`, add:

```env
GEMINI_API_KEY=your_actual_key_here
```

**Option B: Export key manually in terminal**

```bash
export GEMINI_API_KEY=your_actual_key_here
```

---

## 📥 Ingesting Documents

```bash
python main.py
```

Then:

1. Select `[1] Ingest Documents]`
2. Enter path to a folder containing `.pdf`, `.txt`, or `.md` files
3. Wait while the system loads, chunks, embeds, and stores documents locally into `./db/`

---

## 💬 Starting the Chat

```bash
python main.py
```

Then:

1. Select `[2] Start Chatbot`
2. Ask questions related to the documents you ingested

Example prompts:

- "What is Unit 2 in Java?"
- "List all topics covered in Python basics."
- "Summarize the syllabus for Data Structures."

---

## 🔧 Configuration

All settings are in `config.py`:

```python
chat = {
    "llm_model": "gemini-1.5-flash",
    "top_k": 5,
    "streaming": False,
    "temperature": 0.3,
    "prompt_template": """You are a helpful assistant. Use the following context to answer:

{context}

Question: {query}
Answer:"""
}

ingest = {
    "chunk_size": 500,
    "chunk_overlap": 50
}
```

---

## 🧯 Troubleshooting

- **Gemini API Error 404**  
  → You're using the wrong model name or version. Use `"models/gemini-1.5-flash"`

- **No answer or poor results**  
  → Check if you ingested the correct folder. Also try raising `top_k` in config.

- **High memory usage during ingestion**  
  → PDFs with scanned pages or massive length can cause slow embedding. Try ingesting a smaller folder first.

- **FontBBox warnings**  
  → These are non-fatal parsing issues from `pdfminer`. Safe to ignore.

---

## 🚀 Future Improvements

- Add web-based UI (FastAPI or Streamlit)
- Use async streaming Gemini responses
- Replace Chroma with Faiss or Weaviate for scale
- GPU-backed embedding for large corpus
- Docker containerization and hosted inference

---

## 📄 License

MIT License. See `LICENSE` file for details.

---

Built with ❤️ for working locally, thinking deeply, and querying privately.
