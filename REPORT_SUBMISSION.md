# MOSDAC AI Help Bot – Comprehensive Report (SSIP 2025 PS000007)

This report consolidates the solution details, implementation evidence, KPIs, demo plan, and forward-looking roadmap for the MOSDAC AI Help Bot project.

---

## 1) Executive Summary

- The MOSDAC AI Help Bot is a production-ready, multilingual assistant for ISRO’s MOSDAC portal, designed to drastically reduce time-to-information.
- Core components: Hybrid RAG + LLM chat, navigation assistance, 48-hour auto-scraping and ingestion pipeline, language-enforced responses, and self-learning feedback.
- Backend: FastAPI REST API with endpoints for chat, navigation, status, data jobs, and admin; supported by rate limiting, CORS, monitoring, and robust error handling.
- Frontend: HTML/CSS/JS web client with language selector and feedback capture; middleware patterns for integration documented.
- Outcome: Accurate answers with citations, step-by-step MOSDAC navigation guidance, and an analytics-driven improvement loop.

---

## 2) Problem Statement Fit (PS000007)

- Automated Information Retrieval: Continuous scraping/indexing of MOSDAC content (documents, pages, tables, metadata) with scheduled refresh.
- Natural Language Understanding: Users query in plain language; the bot returns grounded answers with citations.
- Context Awareness: Session-based memory enables follow-ups and continuity.
- Self-Learning: User ratings/comments feed analytics and common-issue extraction.

References: `SYNOPSIS_SUBMISSION.md` Sections 2–5; repo docs `README.md`, `API_DOCUMENTATION.md`, `docs/DEVELOPMENT_DIARY.md`.

---

## 3) System Architecture

- Frontend (HTML/JS): Chat UI with language selector and feedback UI
- REST API (FastAPI): Chat, navigation, data jobs, status, admin
- Data Layer: ChromaDB vector store, SQLite feedback DB, scraped data repo
- LLM Layer: Gemini API and/or Ollama local models (dual-mode resilience)
- Scraping & Ingestion: Crawl4AI async scraper; semantic chunking; embeddings; ingestion pipeline; 48-hour scheduler

See `SYNOPSIS_SUBMISSION.md` Roadmap diagrams for system and chat flow. Export PNGs and include as figures.

---

## 4) Implementation Evidence

- API Endpoints & Scheduling: `API_DOCUMENTATION.md`, `API_README.md`
- Language Enforcement: `docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md`
- Development Log & Metrics: `docs/DEVELOPMENT_DIARY.md`, `docs/MASTER_DEVELOPMENT_JOURNAL.md`
- Source Structure and Components: `README.md` (Architecture, Features)

Screenshots (to be provided by team):
- UI: `images/screenshot_ui_1.png`
- Swagger: `images/screenshot_swagger.png`

---

## 5) KPIs & Validation

- Latency Targets:
  - Navigation intent detection: < 500 ms
  - Chat response (RAG+LLM): < 3 s
  - Feedback submission: < 200 ms
- Quality Targets:
  - Source-backed answers with citations
  - Average feedback rating ≥ 4.2 in pilot
- Coverage & Freshness:
  - ≥ 90% of priority MOSDAC sections indexed
  - Auto-scraping every 48 hours
- Language Consistency:
  - 100% enforced response language across 10+ Indian languages + English

Validation artifacts: logs, `/api/v1/status` responses, feedback analytics distribution, and demo runs.

---

## 6) Demo Plan (10 minutes)

1. Status & Health (30s)
   - Open `/api/docs` and `/api/v1/status` to show available endpoints and component health.
2. Navigation Assistance (2 min)
   - Ask “How to download satellite data?”
   - Show step-by-step guidance with links and selectors.
3. Multilingual Q&A (3 min)
   - Set language to Hindi/Tamil; ask in English/Hindi; demonstrate enforced output language.
4. Grounded Answers with Citations (2 min)
   - Ask a factual question and show source list.
5. Feedback & Analytics (1.5 min)
   - Submit a 5-star rating with a comment; show analytics endpoint response.
6. Auto-Scraping & Admin (1 min)
   - Show `/api/v1/admin/config` and explain the scheduler (48h).

---

## 7) Security, Compliance, and Robustness

- Respect robots.txt and ToS; scoped scraping and polite crawling.
- Rate limiting and CORS configured; structured error handling.
- Citations and attribution for transparency; no hallucinated claims encouraged.
- Option to use local LLM (Ollama) for resilience and cost control.

---

## 8) Differentiators

- MOSDAC-specific navigation mapping and intent guidance (beyond generic chatbots).
- End-to-end language enforcement; inclusive and accessible UX across India.
- Auto-scraping with quality scoring and semantic chunking; evidence-based answers.
- Production API with monitoring, admin controls, and clean integration surface.

---

## 9) Roadmap & Advanced Extensions

Near-term engineering:
- Incremental scraping; Redis caching; advanced admin dashboard.
- Better retrieval with hybrid lexical + dense search and improved reranking.

Advanced personalization & recommendation systems (if selected):
- Motivation: Personalize discovery of MOSDAC products, documents, and services based on user behavior, session context, and feedback.
- Candidates and context:
  - IN (Interest Network): Capture evolving user interests across sessions; model temporal dynamics of user-item interactions to recommend relevant MOSDAC resources (e.g., data products, FAQs, tutorials).
  - DIEN (Deep Interest Evolution Network): Model interest evolution with auxiliary losses; improves recommendation performance when user sequences are long and intent shifts (e.g., from rainfall data to ocean surface current data).
  - YouTube Recommender System: Two-tower candidate generation + deep ranking; scalable for large catalogs (candidate generation on embeddings; ranking with context signals like session language, device type, and prior clicks).
  - BERT4Rec: Bidirectional Transformer for sequential recommendation; captures context on both sides of an item for stronger next-item prediction (useful to recommend next-best MOSDAC resources, documentation, or related services).
- Integration plan:
  - Data: Use anonymized interaction logs (queries, clicks, ratings) with strict privacy safeguards.
  - Features: Query intent, selected language, prior document views, feedback signals, session recency/frequency.
  - Serving: Retrieve top-K candidates via vector similarity; re-rank via DIEN/BERT4Rec; feedback loop to continuously learn.
  - KPIs: CTR uplift, dwell time increase, conversion to data downloads, average rating improvement.

Long-term vision:
- Voice interface (TTS/ASR) in selected languages.
- Mobile client; enterprise SSO; Kubernetes deployment and autoscaling.

---

## 10) How to Run & Deploy

- Local run: `python main.py`
- API run: `python -m src.api.main`
- Docs: `http://localhost:8000/api/docs`
- Configuration: `config/system_config.json` or `/api/v1/admin/config`
- Data paths:
  - Scraped: `data/scraped/mosdac_complete_data/`
  - Vector DB: `chroma_db/`
  - Feedback DB: `data/feedback.db`

---

## 11) Appendices

- Source documents: `SYNOPSIS_SUBMISSION.md`, `README.md`, `API_README.md`, `API_DOCUMENTATION.md`, `docs/DEVELOPMENT_DIARY.md`, `docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md`, `docs/API_DEVELOPMENT_JOURNAL.md`, `docs/MASTER_DEVELOPMENT_JOURNAL.md`
- Figures to include:
  - UI Screenshot: `images/screenshot_ui_1.png`
  - Swagger Screenshot: `images/screenshot_swagger.png`
  - Roadmap 1 (System): `images/roadmap_1.png`
  - Roadmap 2 (Chat Flow): `images/roadmap_2.png`

### ASCII Diagrams (for text-based submissions)

#### System Overview (Roadmap 1)
```text
+-----------------------------------------------------------------------------------------+
|                                     SYSTEM OVERVIEW                                     |
|                               MOSDAC AI HELP BOT (PS000007)                              |
+-----------------------------------------------------------------------------------------+

              ┌────────────────────────┐                      ┌────────────────────────┐
              │        Users           │                      │      Admin/Operators   │
              │  (Citizens, Agencies)  │                      │ (Monitoring & Control) │
              └──────────┬─────────────┘                      └──────────┬─────────────┘
                         │                                               │
                         │ HTTP(S)                                       │ HTTP(S)
                         │                                               │
                 ┌───────▼────────────────────────────────────────────────▼───────┐
                 │                        Frontend (HTML/JS)                       │
                 │  - Chat UI (messages, sources)                                  │
                 │  - Language selector (10 Indian languages + English)            │
                 │  - Feedback UI (stars + comments)                               │
                 │  - Branding (ISRO/MOSDAC)                                       │
                 └──────────┬──────────────────────────────────────────────────────┘
                            │  REST API calls (JSON)
                            │
         ┌──────────────────▼───────────────────┐
         │           FastAPI Backend            │
         │          /api/v1 (Uvicorn)           │
         │  - Chat Endpoints                    │
         │  - Navigation Endpoints              │
         │  - Data Jobs (scrape/ingest)         │
         │  - Status/Health                     │
         │  - Admin/Config                      │
         │  Cross-cutting:                      │
         │   • CORS • Rate Limit • Logging      │
         │   • Error Handling • Monitoring      │
         └─────┬───────────┬──────────┬────────┘
               │           │          │
               │           │          │
               │           │          │
   ┌───────────▼───┐  ┌────▼─────────▼─────┐            ┌───────────────────────────┐
   │ Navigation     │  │   Chat (RAG+LLM)   │            │ Background Scheduler       │
   │ Assistant      │  │ - Retrieval (VecDB)│            │ (APScheduler)             │
   │ - Intent detect│  │ - Rerank + Cite    │            │ - Auto-scrape every 48h   │
   │ - Site mapping │  │ - Language enforce │            │ - Auto-ingest after scrape│
   │ - Step guidance│  │ - Session memory   │            │ - Health/metrics jobs      │
   └──────┬─────────┘  └──────────┬─────────┘            └──────────┬────────────────┘
          │                        │                                │
          │                        │                                │ triggers
          │                        │                          ┌─────▼─────────────────┐
          │                        │                          │  Crawl4AI Scraper     │
          │                        │                          │  - URL discovery      │
          │                        │                          │  - Async fetch/retry  │
          │                        │                          │  - Quality scoring    │
          │                        │                          └─────────┬─────────────┘
          │                        │                                    │ writes
          │                        │                           ┌─────────▼───────────┐
          │                        │                           │ Scraped Data Repo   │
          │                        │                           │ data/scraped/...    │
          │                        │                           └─────────┬───────────┘
          │                        │                                     │
          │                        │                           ┌─────────▼───────────┐
          │                        │                           │ Ingestion Pipeline  │
          │                        │                           │ - Semantic chunking │
          │                        │                           │ - Embeddings (ST)   │
          │                        │                           │ - Metadata enrich   │
          │                        │                           └─────────┬───────────┘
          │                        │                                     │ upserts
          │                 ┌───────▼──────────┐                ┌────────▼────────────┐
          │                 │  Vector Database  │                │ Feedback Database   │
          │                 │   (ChromaDB)      │                │ SQLite data/feedback│
          │                 │ - Similarity search│               │ - Ratings/comments  │
          │                 │ - Metadata filter │                │ - Analytics         │
          │                 └─────────┬─────────┘                └────────┬───────────┘
          │                           │                                   │
          │                  ┌────────▼────────┐                          │
          │                  │ Embedding Model │                          │
          │                  │ all-MiniLM-L6-v2│                          │
          │                  └────────┬────────┘                          │
          │                           │                                   │
          │                  ┌────────▼────────────┐                       │
          │                  │   LLM Providers     │                       │
          │                  │ - Gemini (API)      │                       │
          │                  │ - Ollama (local)    │                       │
          │                  └─────────────────────┘                       │
          │                                                                │
          └────────────────────────────────────────────────────────────────┘
```

#### Chat Flow (Roadmap 2)
```text
+-----------------------------------------------------------------------------------------+
|                                   CHAT FLOW (RAG + LLM)                                 |
|                               MOSDAC AI HELP BOT (PS000007)                              |
+-----------------------------------------------------------------------------------------+

User (any language)
    |
    | 1) Types query in Frontend (HTML/JS)
    v
+-------------------------------------------+
| Frontend                                  |
| - Maintains session_id                    |
| - Selected language (dropdown)            |
| - Sends JSON to /api/v1/chat              |
+---------------------------+---------------+
                            |
                            | 2) POST /api/v1/chat {query, session_id, language}
                            v
+--------------------------------------------------------------+
| FastAPI Backend (Chat Route)                                 |
| - Validate input (Pydantic)                                  |
| - Start timer, attach metadata                               |
| - Forward to Chat Service (RAG pipeline)                     |
+----------------------------+---------------------------------+
                             |
                             | 3) Retrieval Stage
                             v
+--------------------------------------------------------------+
| Retriever (Vector DB: ChromaDB)                              |
| - Embed query (Sentence-Transformers all-MiniLM-L6-v2)       |
| - Similarity search (top_k*N)                                |
| - Return candidate chunks + scores                           |
+----------------------------+---------------------------------+
                             |
                             | 4) Reranking/Scoring
                             v
+--------------------------------------------------------------+
| Reranker / Score Clamping                                    |
| - Optional cross-encoder rerank (as per config)              |
| - Clamp scores to [0..1]                                     |
| - Deduplicate, select final top_k                            |
+----------------------------+---------------------------------+
                             |
                             | 5) Context Assembly
                             v
+--------------------------------------------------------------+
| Context Builder                                              |
| - Truncate chunks (max length)                               |
| - Attach metadata (source file/URL)                          |
| - Build citations list                                       |
+----------------------------+---------------------------------+
                             |
                             | 6) Prompting with Language Enforcement
                             v
+--------------------------------------------------------------+
| LLM Layer                                                    |
| - Providers: Gemini API / Ollama local                       |
| - Prompt includes:                                           |
|     * Context (top chunks with citations)                    |
|     * Strict language instruction (selected language)        |
|     * Answer rules (factual, cite sources, plain text)       |
| - Generate response in enforced language                     |
+----------------------------+---------------------------------+
                             |
                             | 7) Response Packaging
                             v
+--------------------------------------------------------------+
| FastAPI Backend (Chat Route)                                 |
| - Attach sources, timings, session metadata                  |
| - Return JSON {response, sources, metadata}                  |
+----------------------------+---------------------------------+
                             |
                             | 8) Render in Frontend
                             v
+--------------------------------------------------------------+
| Frontend                                                     |
| - Display answer (chosen language)                           |
| - Show citations/sources                                     |
| - Show feedback controls (stars + comment)                   |
+----------------------------+---------------------------------+
                             |
                             | 9) Optional Feedback Submission
                             v
+--------------------------------------------------------------+
| Feedback API (/api/v1/feedback/submit)                       |
| - Store in SQLite (data/feedback.db)                         |
| - Aggregated analytics (rating distribution, issues)         |
+--------------------------------------------------------------+
```

---

Prepared for SSIP 2025 submission (PS000007 – Space Applications Centre ISRO).
