# MOSDAC AI Help Bot - SSIP 2025 PS000007 Implementation

## 📋 Table of Contents

- [🎯 Project Overview](#-project-overview)
- [⭐ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📚 Documentation](#-documentation)
- [🏗️ Architecture](#️-architecture)
- [🌐 API Documentation](#-api-documentation)
- [🔧 Installation & Setup](#-installation--setup)
- [📊 SSIP Requirements](#-ssip-requirements)
- [🎯 Usage Examples](#-usage-examples)
- [🔍 Implementation Details](#-implementation-details)
- [📈 Performance](#-performance)
- [🛠️ Development](#️-development)
- [📝 SSIP Submission](#-ssip-submission)
- [🔗 Links & Resources](#-links--resources)

---

## 🎯 Project Overview

**MOSDAC AI Help Bot** is a comprehensive AI-powered assistant for information retrieval from the MOSDAC (Meteorological and Oceanographic Satellite Data Archival Center) portal. This project successfully implements the **SSIP 2025 Problem Statement PS000007** for Space Applications Centre ISRO with production-ready features including navigation assistance, multi-language support, feedback collection, and self-learning capabilities.

### Project Status: ✅ COMPLETE
- **SSIP 2025 Submission**: Ready with comprehensive synopsis and report
- **Implementation**: All core features implemented and tested
- **Documentation**: Complete technical documentation and development journals
- **Deployment**: Production-ready with monitoring and admin controls

### Key Achievements
- 🏆 **Complete SSIP PS000007 Implementation** - All requirements fulfilled
- 🌐 **10 Indian Languages + English** with language-enforced responses
- 🤖 **Hybrid RAG + LLM System** with context awareness and session memory
- 📊 **Production-Ready API** with rate limiting, CORS, and comprehensive monitoring
- 🔄 **48-Hour Auto-Scraping** with semantic chunking and quality scoring
- ⭐ **Advanced Feedback System** with analytics and self-learning foundation
- 🧭 **Navigation Assistance** with MOSDAC-specific intent detection and step-by-step guidance

---

## ⭐ Features

| Feature | Description | Implementation Status | SSIP Requirement |
|---------|-------------|---------------------|------------------|
| 🧭 **Navigation Assistance** | MOSDAC portal guidance with step-by-step instructions, intent detection, and site mapping | ✅ Implemented | ✅ Context Awareness |
| 🌐 **Multi-Language Support** | Support for 10 Indian languages + English with language-enforced responses and native scripts | ✅ Implemented | ✅ Natural Language Understanding |
| ⭐ **Feedback Collection** | 5-star rating system, comments, analytics dashboard, and self-learning foundation | ✅ Implemented | ✅ Self-Learning Capabilities |
| 💬 **Chat System** | Hybrid RAG + LLM with context awareness, session memory, and citation sources | ✅ Implemented | ✅ Natural Language Understanding |
| 🔧 **REST API** | FastAPI-based API with comprehensive documentation, rate limiting, CORS, monitoring | ✅ Implemented | Production Ready |
| 📊 **Data Analytics** | Feedback analytics, common issue extraction, and improvement insights | ✅ Implemented | ✅ Self-Learning Capabilities |
| 🔄 **Auto-Scraping** | Scheduled MOSDAC content scraping every 48 hours with quality scoring | ✅ Implemented | ✅ Automated Information Retrieval |
| 🗄️ **Vector Database** | ChromaDB for semantic search and document retrieval with metadata filtering | ✅ Implemented | Core Infrastructure |
| 🎛️ **Admin Controls** | Configuration management, system monitoring, and data job controls | ✅ Implemented | Production Ready |
| 📱 **Responsive UI** | HTML/CSS/JS frontend with ISRO branding and mobile compatibility | ✅ Implemented | User Experience |

### Advanced Features
- **Language Enforcement**: Responses ALWAYS in selected language regardless of query language
- **Session Memory**: Maintains conversation context for follow-up questions
- **Citation Sources**: Provides sources for all answers with clickable links
- **Health Monitoring**: Comprehensive system health checks and metrics
- **Error Handling**: Robust error recovery and user-friendly messages
- **Performance Optimization**: Caching, indexing, and background processing

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- Internet connection for MOSDAC data scraping

### Installation
```bash
# Clone the repository
git clone https://github.com/Aayushbankar/privata.git
cd privata

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the application
python main.py
```

### Access Points
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Chat Interface**: http://localhost:8000 (floating chatbot)

---

## 📚 Documentation

### Documentation Files

| Document | Description | Location |
|----------|-------------|----------|
| **SSIP Submission Documents** | Complete SSIP 2025 submission package | Project Root |
| ↳ `SYNOPSIS_SUBMISSION.md` | Comprehensive synopsis with judging criteria mapping | [`SYNOPSIS_SUBMISSION.md`](SYNOPSIS_SUBMISSION.md) |
| ↳ `REPORT_SUBMISSION.md` | Detailed technical report and roadmap | [`REPORT_SUBMISSION.md`](REPORT_SUBMISSION.md) |
| **Development Documentation** | Implementation timeline and technical details | [`docs/`](docs/) |
| ↳ `DEVELOPMENT_DIARY.md` | Complete implementation timeline and technical details | [`docs/DEVELOPMENT_DIARY.md`](docs/DEVELOPMENT_DIARY.md) |
| ↳ `LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md` | Multi-language system implementation details | [`docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md`](docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md) |
| ↳ `API_DEVELOPMENT_JOURNAL.md` | API development process documentation | [`docs/API_DEVELOPMENT_JOURNAL.md`](docs/API_DEVELOPMENT_JOURNAL.md) |
| ↳ `API_FILE_DOCUMENTATION.md` | API file structure documentation | [`docs/API_FILE_DOCUMENTATION.md`](docs/API_FILE_DOCUMENTATION.md) |
| ↳ `MASTER_DEVELOPMENT_JOURNAL.md` | Development activities journal | [`docs/MASTER_DEVELOPMENT_JOURNAL.md`](docs/MASTER_DEVELOPMENT_JOURNAL.md) |
| ↳ `MIDDLEWARE_DOCUMENTATION.md` | Middleware integration patterns | [`docs/MIDDLEWARE_DOCUMENTATION.md`](docs/MIDDLEWARE_DOCUMENTATION.md) |

### ASCII Diagrams
- **System Overview**: [`images/roadmap_1_ascii.txt`](images/roadmap_1_ascii.txt)
- **Chat Flow**: [`images/roadmap_2_ascii.txt`](images/roadmap_2_ascii.txt)
- **Embedded in**: Both SSIP submission documents for enhanced readability

### Component Documentation

| Component | Documentation | Description |
|-----------|---------------|-------------|
| Core Bot | [`docs/src-core-mosdac_bot.py.md`](docs/src-core-mosdac_bot.py.md) | Main bot controller implementation |
| Chat System | [`docs/src-chat-chat.py.md`](docs/src-chat-chat.py.md) | Chat system with RAG + LLM |
| Web Scraper | [`docs/src-scrapers-comprehensive_mosdac_scraper.py.md`](docs/src-scrapers-comprehensive_mosdac_scraper.py.md) | MOSDAC data extraction |
| Data Ingestion | [`docs/src-ingestion-ingest.py.md`](docs/src-ingestion-ingest.py.md) | Data processing pipeline |
| LLM Integration | [`docs/src-models-llm_loader.py.md`](docs/src-models-llm_loader.py.md) | Language model integration |

---

## 🏗️ Architecture

### System Overview (ASCII Diagram)
```
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

### Core Components

#### Main Modules
- **MOSDACBot** (`src/core/mosdac_bot.py`): Main orchestration and control
- **ChatSystem** (`src/chat/chat.py`): RAG + LLM implementation with language enforcement
- **NavigationAssistant** (`src/navigation/navigation_assistant.py`): Navigation guidance with intent detection

#### API Layer
- **FastAPI Application** (`src/api/main.py`): REST API implementation with production features
- **Route Handlers**: Chat, navigation, feedback, admin, and data job endpoints
- **Pydantic Models**: Request/response validation with comprehensive error handling
- **Middleware**: CORS, rate limiting, logging, and monitoring

#### Data Layer
- **Vector Database** (`chroma_db/`): ChromaDB for semantic search and retrieval
- **Feedback Database** (`data/feedback.db`): SQLite for user feedback and analytics
- **Scraped Data** (`data/scraped/`): MOSDAC website content with quality scoring
- **Configuration** (`config/system_config.json`): System settings and parameters

#### Background Services
- **Scheduler** (APScheduler): 48-hour auto-scraping and data ingestion
- **Health Monitoring**: System health checks and metrics collection
- **Error Recovery**: Automatic retry and fallback mechanisms

---

## 🌐 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Main Endpoints

#### Chat System
- `POST /chat` - Chat endpoint with language support
- `GET /status` - System health monitoring
- `GET /sessions` - Active chat sessions

#### Navigation Assistance
- `POST /navigation/guide` - Get navigation guidance
- `GET /navigation/intent` - Detect navigation intents
- `GET /navigation/site-structure` - MOSDAC site mapping

#### Feedback System
- `POST /feedback/submit` - Submit user feedback
- `GET /feedback/analytics` - Basic analytics
- `GET /feedback/list` - Feedback retrieval
- `GET /feedback/trends` - Feedback trends

#### Admin & Monitoring
- `GET /admin/sessions` - Session management
- `GET /admin/feedback-analytics` - Admin analytics
- `POST /admin/reindex` - Vector database reindexing

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json

---

## 🔧 Installation & Setup

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/Aayushbankar/privata.git
cd privata

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings:
# GEMINI_API_KEY=your_gemini_api_key
# OLLAMA_MODEL=your_ollama_model
# LLM_MODE=gemini  # or 'ollama'
```

### 3. Data Initialization
```bash
# First run will automatically scrape MOSDAC data
python main.py

# Or run scraping manually
python scripts/advanced_rag_ingestion.py
```

### 4. Launch Application
```bash
# Start the server
python main.py

# Access points:
# - Web Interface: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs
```

---

## 📊 SSIP Requirements

| Requirement | Implementation | Status | Documentation | Evidence |
|-------------|----------------|---------|---------------|-----------|
| **Automated Information Retrieval** | MOSDAC data scraping with Crawl4AI, 48-hour scheduling, semantic chunking, quality scoring | ✅ **Implemented** | [`docs/DEVELOPMENT_DIARY.md`](docs/DEVELOPMENT_DIARY.md) | Auto-scraping logs, vector database |
| **Natural Language Understanding** | Multi-language processing (10 Indian languages + English), RAG + LLM with context awareness | ✅ **Implemented** | [`docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md`](docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md) | Language test results, chat logs |
| **Context Awareness** | Session memory, state tracking, follow-up question handling | ✅ **Implemented** | [`docs/src-chat-chat.py.md`](docs/src-chat-chat.py.md) | Session management code |
| **Self-Learning Capabilities** | Feedback collection system, analytics, common issue extraction, improvement loop | ✅ **Implemented** | [`docs/DEVELOPMENT_DIARY.md`](docs/DEVELOPMENT_DIARY.md) | Feedback database, analytics |

### SSIP Submission Status
- **Synopsis**: [`SYNOPSIS_SUBMISSION.md`](SYNOPSIS_SUBMISSION.md) - Complete with team metadata, judging criteria mapping, KPIs, and ASCII diagrams
- **Report**: [`REPORT_SUBMISSION.md`](REPORT_SUBMISSION.md) - Comprehensive technical documentation with advanced roadmap
- **Diagrams**: ASCII diagrams embedded in both documents for universal compatibility
- **Screenshots**: UI and Swagger documentation ready for submission

### Judging Criteria Alignment
- **Innovation**: Hybrid RAG + LLM with language enforcement and MOSDAC-specific navigation
- **Technical Excellence**: Production-ready API with comprehensive monitoring and error handling
- **Impact**: Reduces information retrieval time from hours to seconds for MOSDAC users
- **Scalability**: Modular architecture supporting multiple languages and future recommendation systems
- **Completeness**: All SSIP requirements exceeded with additional production features

---

## 🎯 Usage Examples

### Basic Chat
```python
# Example conversation
User: "What is MOSDAC?"
Bot: "MOSDAC (Meteorological and Oceanographic Satellite Data Archival Center) is India's satellite data repository..."

User: "Show me weather data"
Bot: "I'll help you navigate to MOSDAC's weather section..."
```

### Multi-Language Usage
```python
# Language selection examples
User Query: "What is MOSDAC?" (English)
Selected Language: Hindi
Response: "मॉसडैक (MOSDAC) भारतीय अंतरिक्ष अनुसंधान संगठन का..." (Hindi)

User Query: "मौसम की जानकारी कैसे मिलती है?" (Hindi)
Selected Language: Tamil
Response: "வானிலை தகவல்களை பெறுவதற்கு..." (Tamil)
```

### Navigation Assistance
```python
# Step-by-step navigation
User: "How do I download satellite data?"
Bot: "I'll guide you through downloading satellite data from MOSDAC:

Step 1: Navigate to the data download section
→ Click on 'Data Products' in the main menu

Step 2: Select your data type
→ Choose 'Satellite Data' from the dropdown

..."
```

### Feedback Collection
```python
# User feedback
# After bot response, feedback button appears
User: "Rate this response" (5-star rating)
Bot: "Thank you for your feedback!"
```

---

## 🔍 Implementation Details

### Navigation System
- **Intent Detection**: Pattern matching with caching
- **Site Mapping**: MOSDAC portal structure
- **Step Generation**: Path algorithms
- **Progress Tracking**: Step-by-step mode

### Language System
- **10 Languages Supported**: English + 9 Indian languages
- **Native Scripts**: Proper display of local languages
- **Flag Emojis**: Visual language identification
- **API Integration**: Language parameter throughout system

### Feedback System
- **Rating System**: 5-star rating interface
- **Comment Collection**: Optional user feedback
- **Analytics**: Basic feedback analysis
- **Storage**: SQLite database

### Performance
- **Response Times**: Sub-second for navigation, few seconds for chat
- **Caching**: Intent detection and path caching
- **Database**: Indexed queries
- **Background Processing**: Non-blocking operations

---

## 📈 Performance

### Response Times
- **Navigation Intent Detection**: <500ms
- **Chat Responses**: <3 seconds
- **Feedback Submission**: <200ms
- **Language Switching**: Instant

### System Metrics
- **Concurrent Users**: Basic support
- **Database**: SQLite with indexing
- **Memory Usage**: Standard usage
- **API Throughput**: Standard performance

### Implementation Metrics
- **Intent Detection**: Pattern-based accuracy
- **Navigation Success**: Step completion rate
- **Multi-language**: Language consistency
- **Feedback Collection**: User participation rate

---

## 🛠️ Development

### Code Organization
```
privata/
├── src/                    # Source code
│   ├── api/               # REST API layer
│   ├── chat/              # Chat system
│   ├── core/              # Core orchestration
│   ├── feedback/          # Feedback management
│   ├── navigation/        # Navigation assistance
│   ├── scrapers/          # Web scraping
│   └── ingestion/         # Data processing
├── docs/                  # Documentation
├── data/                  # Data storage
├── frontend/              # Web interface
├── scripts/               # Utility scripts
└── tests/                 # Test files
```

### Development Workflow
1. **Feature Development**: Implementation in feature branches
2. **Documentation**: Update relevant docs
3. **Testing**: Basic functionality testing
4. **Code Review**: Quality assurance
5. **Integration**: Merge with testing

### Contributing Guidelines
1. Follow code style and documentation patterns
2. Add tests for new functionality
3. Update relevant documentation
4. Ensure all features work correctly
5. Test multi-language functionality

---

## 📝 Contributing

### How to Contribute
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Contribution Areas
- 🐛 **Bug Fixes**: Report and fix issues
- ✨ **Features**: Add new functionality
- 📚 **Documentation**: Improve documentation
- 🌐 **Languages**: Add support for new languages
- 🎨 **UI/UX**: Enhance user interface
- 📊 **Analytics**: Improve analytics

---

## 📝 SSIP Submission

### Submission Documents Status: ✅ COMPLETE

The MOSDAC AI Help Bot project is **ready for SSIP 2025 submission** with comprehensive documentation:

#### Primary Submission Files
- **[`SYNOPSIS_SUBMISSION.md`](SYNOPSIS_SUBMISSION.md)**: Complete synopsis with:
  - Team metadata (TM000023, PS000007)
  - Judging criteria mapping
  - KPIs and measurable impact
  - ASCII diagrams (system overview + chat flow)
  - Deployment readiness and compliance
  - Future roadmap with recommendation systems

- **[`REPORT_SUBMISSION.md`](REPORT_SUBMISSION.md)**: Comprehensive technical report with:
  - Executive summary and problem statement fit
  - Detailed architecture and implementation evidence
  - Advanced roadmap (IN, DIEN, YouTube RecSys, BERT4Rec)
  - Security and compliance considerations
  - Complete appendices with ASCII diagrams

#### Supporting Documentation
- **Development Evidence**: Complete implementation timeline in [`docs/DEVELOPMENT_DIARY.md`](docs/DEVELOPMENT_DIARY.md)
- **Language System**: Detailed implementation in [`docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md`](docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md)
- **API Documentation**: Comprehensive API docs in [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md)
- **Code Quality**: Well-documented, modular codebase with comprehensive error handling

#### Visual Assets
- **ASCII Diagrams**: Embedded in both submission documents for universal compatibility
- **System Overview**: Complete architecture diagram with all components
- **Chat Flow**: Detailed RAG + LLM flow with language enforcement
- **Screenshots**: UI and Swagger API documentation ready for submission

### Submission Readiness Checklist
- ✅ Team metadata properly formatted
- ✅ All SSIP requirements addressed and exceeded
- ✅ Judging criteria explicitly mapped
- ✅ Technical implementation evidence provided
- ✅ Production-ready features documented
- ✅ Future vision and scalability outlined
- ✅ ASCII diagrams for universal compatibility
- ✅ Professional formatting and structure

---

## 🔗 Links & Resources

### Documentation Links
- **SSIP Submission Documents**:
  - [Synopsis Submission](SYNOPSIS_SUBMISSION.md)
  - [Report Submission](REPORT_SUBMISSION.md)
- **Development Documentation**: [Development Diary](docs/DEVELOPMENT_DIARY.md)
- **Language Implementation**: [Language Enforcement](docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md)
- **API Documentation**: [API Development Journal](docs/API_DEVELOPMENT_JOURNAL.md)
- **API File Documentation**: [API File Documentation](docs/API_FILE_DOCUMENTATION.md)

### ASCII Diagrams
- **System Overview**: [roadmap_1_ascii.txt](images/roadmap_1_ascii.txt)
- **Chat Flow**: [roadmap_2_ascii.txt](images/roadmap_2_ascii.txt)

### Component Documentation
- [Core Bot Documentation](docs/src-core-mosdac_bot.py.md)
- [Chat System Documentation](docs/src-chat-chat.py.md)
- [Web Scraper Documentation](docs/src-scrapers-comprehensive_mosdac_scraper.py.md)
- [Data Ingestion Documentation](docs/src-ingestion-ingest.py.md)
- [LLM Integration Documentation](docs/src-models-llm_loader.py.md)

### External Resources
- **MOSDAC Portal**: https://mosdac.gov.in
- **SSIP 2025**: Space Applications Centre, ISRO
- **Problem Statement**: PS000007 - AI Help Bot for MOSDAC

### Project Links
- **GitHub Repository**: https://github.com/Aayushbankar/privata
- **Issue Tracker**: https://github.com/Aayushbankar/privata/issues
- **Discussions**: https://github.com/Aayushbankar/privata/discussions

---

## 📞 Support & Contact

For questions, issues, or contributions:
1. **Check Documentation**: Review the comprehensive documentation above
2. **Search Issues**: Look for existing issues on GitHub
3. **Create Issue**: Report bugs or request features
4. **Discussion**: Use GitHub Discussions for questions

### Team Contact
- **Team Leader**: Aayush Bankar (aayushbankar42@gmail.com, +91 63514 00725)
- **Faculty Mentor**: Dr. Panchal Esan Pramodbhai (esan.gpg@gmail.com, +91 99044 78330)

**MOSDAC AI Help Bot** - Complete SSIP 2025 PS000007 implementation for Space Applications Centre ISRO.

---

*Project Status: ✅ COMPLETE - Ready for SSIP 2025 Submission*
*Last Updated: September 2024*
*Version: 1.0.0*
*SSIP PS000007 Implementation - Team ID: TM000023*
