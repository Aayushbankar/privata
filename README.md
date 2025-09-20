# MOSDAC AI Help Bot - Implementation Guide

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
- [📝 Contributing](#-contributing)
- [🔗 Links & Resources](#-links--resources)

---

## 🎯 Project Overview

**MOSDAC AI Help Bot** is an AI-powered assistant for information retrieval from the MOSDAC (Meteorological and Oceanographic Satellite Data Archival Center) portal. This project implements the **SSIP 2025 Problem Statement PS000007** with features including navigation assistance, multi-language support, and feedback collection.

### Project Features
- Navigation assistance system
- Multi-language support
- Feedback collection system
- Chat interface with RAG + LLM

---

## ⭐ Features

| Feature | Description | Implementation Status |
|---------|-------------|---------------------|
| 🧭 **Navigation Assistance** | MOSDAC portal guidance with step-by-step instructions | ✅ Implemented |
| 🌐 **Multi-Language Support** | Support for multiple Indian languages with language selection | ✅ Implemented |
| ⭐ **Feedback Collection** | User feedback system with rating and comments | ✅ Implemented |
| 💬 **Chat System** | RAG-based chat with LLM integration | ✅ Implemented |
| 🔧 **REST API** | FastAPI-based API with documentation | ✅ Implemented |
| 📊 **Data Analytics** | Feedback analytics and basic reporting | ✅ Implemented |

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
| DEVELOPMENT_DIARY.md | Implementation timeline and technical details | [`docs/DEVELOPMENT_DIARY.md`](docs/DEVELOPMENT_DIARY.md) |
| LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md | Language system implementation details | [`docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md`](docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md) |
| API_DEVELOPMENT_JOURNAL.md | API development process documentation | [`docs/API_DEVELOPMENT_JOURNAL.md`](docs/API_DEVELOPMENT_JOURNAL.md) |
| API_FILE_DOCUMENTATION.md | API file structure documentation | [`docs/API_FILE_DOCUMENTATION.md`](docs/API_FILE_DOCUMENTATION.md) |
| MASTER_DEVELOPMENT_JOURNAL.md | Development activities journal | [`docs/MASTER_DEVELOPMENT_JOURNAL.md`](docs/MASTER_DEVELOPMENT_JOURNAL.md) |

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

### System Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   REST API       │    │   Data Layer    │
│   (HTML/JS)     │◄──►│   (FastAPI)      │◄──►│   (ChromaDB)    │
│                 │    │                  │    │                 │
│ • Chat Interface│    │ • Route Handlers │    │ • Vector Search │
│ • Language Sel  │    │ • Request Valida │    │ • Document Store│
│ • Feedback UI   │    │ • Error Handling │    │ • Analytics     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐
│   LLM Layer     │    │   Scraping Layer │
│   (Gemini/      │    │   (Crawl4AI)     │
│   Ollama)       │    │                  │
│                 │    │ • Data Scraping  │
│ • Prompt Eng    │    │ • Data Extraction│
│ • Language Proc │    │ • Scheduled Jobs │
└─────────────────┘    └──────────────────┘
```

### Core Components

#### Main Modules
- **MOSDACBot** (`src/core/mosdac_bot.py`): Main orchestration and control
- **ChatSystem** (`src/chat/chat.py`): RAG + LLM implementation
- **NavigationAssistant** (`src/navigation/navigation_assistant.py`): Navigation guidance

#### API Layer
- **FastAPI Application** (`src/api/main.py`): REST API implementation
- **Route Handlers**: Chat, navigation, feedback endpoints
- **Pydantic Models**: Request/response validation

#### Data Layer
- **Vector Database** (`chroma_db/`): Semantic search and retrieval
- **Feedback Database** (`data/feedback.db`): User feedback storage
- **Scraped Data** (`data/scraped/`): MOSDAC website content

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

| Requirement | Implementation | Status | Documentation |
|-------------|----------------|---------|---------------|
| **Automated Information Retrieval** | MOSDAC data scraping with Crawl4AI | ✅ Implemented | [`docs/DEVELOPMENT_DIARY.md`](docs/DEVELOPMENT_DIARY.md) |
| **Natural Language Understanding** | Multi-language processing | ✅ Implemented | [`docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md`](docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md) |
| **Context Awareness** | Session memory and state tracking | ✅ Implemented | [`docs/src-chat-chat.py.md`](docs/src-chat-chat.py.md) |
| **Self-Learning Capabilities** | Feedback collection system | ✅ Implemented | [`docs/DEVELOPMENT_DIARY.md`](docs/DEVELOPMENT_DIARY.md) |

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

## 🔗 Links & Resources

### Documentation Links
- [Development Diary](docs/DEVELOPMENT_DIARY.md)
- [Language Implementation](docs/LANGUAGE_ENFORCEMENT_IMPLEMENTATION.md)
- [API Development Journal](docs/API_DEVELOPMENT_JOURNAL.md)
- [API File Documentation](docs/API_FILE_DOCUMENTATION.md)

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
1. **Check Documentation**: Review the documentation above
2. **Search Issues**: Look for existing issues on GitHub
3. **Create Issue**: Report bugs or request features
4. **Discussion**: Use GitHub Discussions for questions

**MOSDAC AI Help Bot** - AI assistant for MOSDAC portal information retrieval.

---

*Last Updated: December 2024*
*Version: 1.0.0*
*SSIP PS000007 Implementation*
