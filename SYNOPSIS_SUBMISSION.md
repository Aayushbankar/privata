# SSIP 2025 – Synopsis Submit Page (MOSDAC AI Help Bot)

This document compiles a complete, submission-ready synopsis for SSIP 2025 based on the project's implementation and documentation in this repository.

---

## Team & Submission Metadata

- Team ID: TM000023
- Industry Name: Space Applications Centre ISRO (PSU)
- Problem ID: PS000007
- Problem Statement: AI based Help bot for information retrieval out of web content
- Relevant Discipline: CE/IT
- Team Leader: Aayush Bankar — aayushbankar42@gmail.com — +91 63514 00725
- Faculty Mentor: Dr. Panchal Esan Pramodbhai — esan.gpg@gmail.com — +91 99044 78330

This synopsis describes the implemented solution, the system vision, measurable impact, and why the design best fits the expectations of Space Applications Centre ISRO for PS000007.

## 1) Problem ID

- PS000007

---

## 2) Problem Statement

AI-based help bot for information retrieval from web content, targeted to MOSDAC (www.mosdac.gov.in) — the Meteorological and Oceanographic Satellite Data Archival Center of ISRO. The system continuously scans and indexes MOSDAC content (documents, static pages, tables, meta tags, aria-labels), supports natural-language queries, preserves session context, and learns from user feedback.

Challenge description with context (as per PS):
- Automated Information Retrieval: Continuously scan and index content to keep responses up-to-date.
- Natural Language Understanding (NLU): Users query in natural language; bot returns precise answers.
- Context Awareness: Session memory ensures relevant follow-ups.
- Self-Learning Capabilities: Responses improve over time using user ratings and comments.

Background and users:
- MOSDAC hosts satellite data and services for citizens and agencies. Users struggle to locate specific information due to navigation complexity, mixed content, and time constraints.
- Primary users: Citizens, agencies, end users requiring fast access to accurate MOSDAC information.

Expected outcomes and impact:
- A help bot that integrates directly with the web, enabling self-service support, improved satellite data learning and acceptance, reduced human intervention for routine queries, and enhanced user experience.

Context and motivation:
- Users (citizens, agencies, end users) struggle to navigate MOSDAC due to large, mixed, and distributed content across many sections and microsites.
- A multilingual, context-aware assistant can reduce time-to-information, improve accessibility, and increase the overall utility of the portal.

References in repo: `README.md` (Project Overview), `docs/DEVELOPMENT_DIARY.md` (Project Overview), `docs/MASTER_DEVELOPMENT_JOURNAL.md` (Original Vision section).

---

## 3) Synopsis Abstract

MOSDAC AI Help Bot is a production-ready assistant for ISRO’s MOSDAC portal that delivers fast, grounded answers and step-by-step guidance in 10 Indian languages + English. The solution combines hybrid RAG (vector search + reranking) with LLM generation, a scheduled web-scraping and ingestion pipeline, language-enforced responses, and a self-learning feedback loop. The REST API (FastAPI) provides comprehensive endpoints for chat, status, data management, and admin operations with rate limiting, CORS, monitoring, and robust error handling. A lightweight web interface offers chat, language selection, and feedback capture, enabling immediate deployment and integration.

Key outcomes:
- Faster, accurate answers with citations from MOSDAC content
- Step-by-step navigation guidance across MOSDAC sections
- Consistent responses in the user’s chosen language
- Feedback-driven improvement and analytics

Sources: `README.md`, `API_README.md`, `API_DOCUMENTATION.md`, `docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md`, `docs/DEVELOPMENT_DIARY.md`.

---

## 4) Literature Review / Existing Innovation & Technology

Relevant approaches and technologies that inform the solution:
- Retrieval-Augmented Generation (RAG): Combines semantic retrieval over a vector database with LLM generation for grounded answers. Implemented with ChromaDB and sentence-transformers; reranking patterns referenced in `docs/MASTER_DEVELOPMENT_JOURNAL.md`.
- Semantic Chunking: Preserves context by splitting content by headings/paragraphs with overlaps instead of fixed-size tokens (see Development Journals).
- Vector Databases: ChromaDB used for document storage, similarity search, metadata filtering (`README.md`, `API_DOCUMENTATION.md`).
- Web Scraping at Scale: Crawl4AI-based async scraping, controlled concurrency, URL discovery via sitemaps/robots and quality scoring pipeline (documented in Master Development Journal).
- Multilingual NLU & Prompting: Language-enforced responses regardless of query language; systemwide language parameter propagation (`docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md`).
- Production API Patterns: FastAPI with CORS, rate limiting, background schedulers (APScheduler), error handling, health checks, and configuration management (see `API_README.md`, `API_DOCUMENTATION.md`).
- Feedback-Driven Self Learning: Star ratings, comments, analytics, common issue extraction as a foundation for iterative improvement (`docs/DEVELOPMENT_DIARY.md`).

Differentiating innovations for MOSDAC context:
- MOSDAC-specific site mapping and navigation intent system for high-precision guidance.
- Language enforcement that guarantees output language regardless of query language, improving inclusivity and accessibility.
- Dual-LLM mode (Gemini API and Ollama) for resilience, cost control, and offline capability.

---

## 5) Approach to Solve the Problem

Architecture overview (see `README.md` → Architecture section):
- Frontend (HTML/JS): Chat UI, language selector, feedback UI
- REST API (FastAPI): Endpoints for chat, navigation, data, status, admin
- Data Layer: ChromaDB vector store, SQLite feedback DB, scraped content repository
- LLM Layer: Gemini API and/or local Ollama models
- Scraping Layer: Crawl4AI-based async scraper with scheduler

Core algorithms and flows:
- Hybrid Retrieval: Vector similarity search → optional reranking → context assembly with citations → LLM generation
- Language Enforcement: Selected language travels through `ChatRequest` to prompt templates ensuring response language (`docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md`)
- Navigation Assistance: Intent detection + step-wise instruction generation with MOSDAC-specific site mapping (see `docs/DEVELOPMENT_DIARY.md`)
- Auto-Scraping & Ingestion: 48-hour schedule → scrape → quality scoring → chunking → embedding → vector DB ingestion (`API_README.md`, `API_DOCUMENTATION.md`)
- Self-Learning Feedback Loop: Ratings/comments captured via API → analytics → common issues extraction (future ML fine-tuning ready)

Operational readiness:
- Configurable via `config/system_config.json` and `/api/v1/admin/config`.
- Health monitoring via `/health` and `/api/v1/status`.
- Rate limiting, logging, structured error handling across routes.

---

## 6) Road map / Flow Diagram to Develop Final Solution (1)

ASCII diagram (System overview):

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

Notes:
- Health: /health, /api/v1/status
- Admin/Config: /api/v1/admin/config
- Jobs: /api/v1/data/scrape, /api/v1/data/ingest
- Security: CORS, rate limiting, error handling, monitoring
```

If you need image files for upload, export this ASCII to PNG (already saved to `images/roadmap_1_ascii.txt`) and attach as “Roadmap 1”.

---

## 7) Road map / Flow Diagram to Develop Final Solution (2)

ASCII diagram (RAG chat flow with language enforcement):

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

Operational Notes:
- Health: /health, /api/v1/status
- Admin: /api/v1/admin/config (scheduler, limits)
- Auto-Scrape/Ingest: every 48h updates the Vector DB
```

Export this ASCII to PNG and attach as “Roadmap 2” if the portal only accepts images.

---

## 8) Tools and Technologies

- Backend: FastAPI, Uvicorn, Pydantic, APScheduler
- Data: ChromaDB (vector), SQLite (feedback)
- Embeddings: sentence-transformers (all-MiniLM-L6-v2)
- LLM: Google Gemini API and/or Ollama local models
- Scraping: Crawl4AI, aiohttp, BeautifulSoup
- Frontend: HTML, CSS, JavaScript (chat UI, language dropdown, feedback modal)
- DevOps/Prod: Rate limiting, CORS, health/status endpoints, logging, monitoring

References: `API_README.md`, `API_DOCUMENTATION.md`, `MIDDLEWARE_DOCUMENTATION.md`, `README.md`.

---

## 9) Challenges / Risk in Implementing the Final Prototype

- Data Variability: Inconsistent page structures across MOSDAC subsections; mitigated via quality scoring and semantic chunking.
- Scraping Robustness: Network errors, robots/sitemap changes; mitigated with retries, discovery, and scheduler management.
- Legal/Compliance: Respect robots.txt and terms; constrain scraping to permitted domains and usage.
- Performance & Scale: Embedding and retrieval latency; mitigated with caching, controlled concurrency, and reranking.
- Multilingual Consistency: Enforcing language responses; mitigated with explicit prompt instructions and end-to-end language parameter.
- Vector DB Growth: Storage and retrieval costs; mitigated with indexing, pruning strategies, and scheduled reingestion.
- LLM Availability/Cost: API outages or quotas; mitigated with dual-mode (Gemini/Ollama) support.

Risk ownership & monitoring:
- Status dashboards via `/api/v1/status` and admin metrics endpoints.
- Logs and structured errors for rapid triage; rate limits to protect service.

---

## 10) Possible Outcome of Your Work

- A deployed web assistant that reduces time-to-information and increases MOSDAC portal usability.
- Consistent multilingual answers with citations and navigation guidance.
- Operational metrics and feedback analytics to drive continuous improvement.
- Foundation for advanced capabilities (voice, mobile app, analytics dashboard, ML-driven learning).

Impact metrics (from docs):
- Navigation intent detection < 500ms; chat responses < 3s; feedback submission < 200ms (`README.md`, `docs/DEVELOPMENT_DIARY.md`).

---

## 11) Work Done Till Date

Implemented features (see `README.md` → Features; `docs/DEVELOPMENT_DIARY.md`; `docs/API_DEVELOPMENT_JOURNAL.md`):
- Complete REST API (FastAPI) with auto-scraping every 48 hours
- Chat system (RAG + LLM) with citations and session memory
- Navigation assistance with intent detection and step-by-step guidance
- Multi-language support with enforcement (10 Indian languages + English)
- Feedback collection, storage, and analytics (SQLite)
- Production features: rate limiting, CORS, error handling, monitoring, health checks
- Frontend web interface (HTML/CSS/JS) integrated with API
- Comprehensive documentation across `docs/` and root README

Evidence:
- `API_DOCUMENTATION.md` and `API_README.md` (endpoints, scheduler, configs)
- `docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md` (language pipeline and prompts)
- `docs/DEVELOPMENT_DIARY.md` and `docs/MASTER_DEVELOPMENT_JOURNAL.md` (architecture, algorithms, metrics)

KPIs validated (dev environment):
- End-to-end response time within targets; stable auto-scrape schedule; correct language enforcement in UI-to-LLM chain; feedback analytics populated.

---

## 12) Image / Screenshot of Solution (1)

- Suggested file to upload: A UI screenshot of `frontend/index.html` running locally.
- Placeholder path (replace with real screenshot when captured): `images/screenshot_ui_1.png` (to be created).
- Existing asset for illustration: `frontend/des_1.jpeg` (branding/visual reference).

---

## 13) Image / Screenshot of Solution (2)

- Suggested file to upload: API Swagger UI at `http://localhost:8000/api/docs`.
- Placeholder path: `images/screenshot_swagger.png` (to be created).

---

## 14) Report in PDF

- Export this markdown (`SYNOPSIS_SUBMISSION.md`) to PDF and upload as the Report.
- Also include `API_DOCUMENTATION.md` excerpts or appendices if the portal allows.
- Maximum file size note: 20 MB (per portal instruction).

---

## 15) Judging Criteria Mapping (Why this is winner-grade)

- Relevance to PS000007: Directly addresses automated retrieval, NLU, context awareness, and self-learning on MOSDAC.
- Technical Depth: Hybrid RAG with reranking, semantic chunking, dual-LLM, auto-scraping scheduler, robust API with production features.
- Impact & Accessibility: 10+ languages with enforced output; navigation guidance reduces user effort dramatically.
- Feasibility & Readiness: End-to-end implemented with documentation, runbooks, health checks, and clear deployment steps.
- Scalability & Maintainability: Modular architecture (`src/`), configuration-driven ops, background jobs, and observability endpoints.

## 16) KPIs & Validation Plan

- Response latency targets: navigation intent < 500ms; chat < 3s; feedback submit < 200ms.
- Answer quality: source-backed responses with citations; feedback rating average ≥ 4.2 in pilot.
- Coverage: ≥ 90% of priority MOSDAC sections indexed; scheduled refresh every 48h.
- Language consistency: 100% enforced language in end-to-end tests across 10+ languages.

## 17) Deployment & Demo Readiness

- Local run via `python main.py`; API via `python -m src.api.main`.
- Interactive docs at `/api/docs`; sample test scripts `test_api.py`, `tests/`.
- Demo script: show navigation guidance, multilingual Q&A, feedback submission, status dashboard.

## 18) Compliance & Ethics

- Respect MOSDAC robots.txt and ToS; curated domain scope; attribution via citations.
- Data minimization and safe logging; rate limiting to protect services.
- Clear user communication; fallbacks and error messaging.

## 19) Differentiators vs typical chatbots

- MOSDAC-specific navigation assistant (intent + step guidance), not just Q&A.
- Language enforcement end-to-end; consistent UX regardless of query language.
- Auto-scraping with quality scoring; evidence-based answers with citations.
- Production-grade API with monitoring and admin operations.

## 20) Future Roadmap

- Advanced analytics dashboard; incremental scraping; Redis caching.
- Voice interface; mobile client; enterprise SSO; Kubernetes deployment.

---

## Appendices (Optional but Recommended)

- API Base URL (local dev): `http://localhost:8000/api/v1`
- Key Endpoints: `/chat`, `/status`, `/data/scrape`, `/data/ingest`, `/feedback/submit`, `/admin/config` (see `API_DOCUMENTATION.md`)
- Data paths:
  - Scraped data: `data/scraped/mosdac_complete_data/`
  - Vector DB: `chroma_db/`
  - Feedback DB: `data/feedback.db`
- How to Run: See `README.md` → Quick Start and Installation & Setup

---

## Submission Notes

- If the portal only accepts JPG/PNG for diagrams, export the Mermaid diagrams above to PNG and upload them as “Roadmap 1” and “Roadmap 2”.
- Replace placeholder image paths with real screenshots before submission.
- Keep Problem ID as PS000007 and ensure the title references MOSDAC AI Help Bot.

---

Prepared from repository documents: `README.md`, `API_README.md`, `API_DOCUMENTATION.md`, `MIDDLEWARE_DOCUMENTATION.md`, `docs/DEVELOPMENT_DIARY.md`, `docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md`, `docs/API_DEVELOPMENT_JOURNAL.md`, `docs/MASTER_DEVELOPMENT_JOURNAL.md`.
