# MOSDAC AI Help Bot

An AI-powered help bot for information retrieval from the MOSDAC (Meteorological and Oceanographic Satellite Data Archival Center) website. Features both CLI interface and REST API with automatic web scraping capabilities.

## 🚀 Quick Start

```bash
# Run the bot (CLI mode)
./scripts/run_bot.sh

# Or manually
python main.py

# Start the REST API server
python -m src.api.main

# Access comprehensive HTML documentation
open index.html
```

## 📁 Project Structure

```
privata/
├── src/                          # Source code
│   ├── api/                      # REST API implementation
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # API configuration
│   │   ├── dependencies.py      # API dependencies
│   │   ├── models/              # Pydantic models
│   │   │   ├── chat.py          # Chat models
│   │   │   ├── status.py        # Status models
│   │   │   ├── data.py          # Data job models
│   │   │   └── admin.py         # Admin models
│   │   ├── routes/              # API endpoints
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   ├── status.py        # Status endpoints
│   │   │   ├── data.py          # Data endpoints
│   │   │   └── admin.py         # Admin endpoints
│   │   └── background/          # Background tasks
│   │       └── scheduler.py     # Auto-scraping scheduler
│   ├── core/                     # Core functionality
│   │   ├── mosdac_bot.py        # Main bot controller
│   │   ├── config.py            # Configuration
│   │   └── config.json          # Config file
│   ├── scrapers/                 # Web scraping
│   │   ├── comprehensive_mosdac_scraper.py
│   │   └── crawl4ai_mosdac.py
│   ├── ingestion/                # Data ingestion
│   │   └── ingest.py
│   ├── chat/                     # Chat system
│   │   └── chat.py
│   ├── models/                   # LLM integration
│   │   └── llm_loader.py
│   ├── retrieval/                # Vector search & retrieval
│   │   ├── modern_vectordb.py
│   │   ├── multi_modal_embedder.py
│   │   └── reranker.py
│   └── utils/                    # Utilities
│       ├── enhanced_chunker.py
│       ├── enhanced_doc_loader.py
│       └── structured_extractor.py
├── data/                         # Data storage
│   ├── scraped/                  # Scraped website data
│   │   └── mosdac_complete_data/
│   └── vector_db/                # Vector database
│       └── chroma_db/
├── config/                       # System configuration
│   └── system_config.json        # API configuration file
├── scripts/                      # Utility scripts
│   ├── run_bot.sh               # Bot runner
│   ├── setup_llm.py             # LLM setup helper
│   ├── main.py                  # Legacy main
│   └── advanced_rag_ingestion.py
├── tests/                        # Test files
│   ├── test.py
│   └── test_chat.py
├── docs/                         # Documentation
│   ├── README.md
│   ├── PROJECT_PROGRESS_REPORT.md
│   ├── PROJECT_STATUS_REPORT.md
│   ├── API_DEVELOPMENT_JOURNAL.md
│   ├── API_FILE_DOCUMENTATION.md
│   └── MASTER_DEVELOPMENT_JOURNAL.md
├── main.py                       # Main entry point
├── requirements.txt              # Dependencies
├── API_DOCUMENTATION.md          # API documentation
├── API_README.md                 # API quick start guide
├── index.html                    # Comprehensive HTML documentation
└── README.md                     # This file
```

## 🛠️ Features

### Core Bot Features
- **Comprehensive Web Scraping**: 443 URLs processed (7x more than required)
- **RAG-Optimized Data Extraction**: 4.1M+ characters, 270 structured tables
- **Advanced Ingestion Pipeline**: 708 semantic chunks stored in ChromaDB
- **Fully Functional Chat System**: Natural language Q&A with citations
- **Dual LLM Support**: Gemini API + Ollama offline modes
- **Complete Data Management**: Status monitoring, removal, re-scraping

### REST API Features
- **Production-Ready API**: FastAPI-based RESTful endpoints
- **Auto-Scraping System**: Automatic website scraping every 48 hours
- **Background Job Processing**: Asynchronous scraping and ingestion jobs
- **Real-time Chat API**: AI-powered chat with MOSDAC content
- **Configuration Management**: Dynamic system configuration via API
- **Health Monitoring**: Comprehensive system status and metrics
- **Rate Limiting**: Built-in protection against abuse

## 🔧 Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure LLM**:
```bash
# For API mode (recommended)
export GEMINI_API_KEY="your-api-key"
export LLM_MODE="api"

# For Ollama mode (offline)
export LLM_MODE="ollama"
```

3. **Run Setup Helper**:
```bash
python scripts/setup_llm.py
```

4. **Start API Server**:
```bash
python -m src.api.main
```

## 🎯 Usage

### CLI Interface
```bash
# Main Bot Interface
python main.py

# Direct Core Access
python src/core/mosdac_bot.py

# Test System
python tests/test_chat.py
```

### REST API Interface
```bash
# Start API server
python -m src.api.main

# Test API endpoints
python test_api.py

# Access API documentation
# Swagger UI: http://localhost:8000/api/docs
# ReDoc: http://localhost:8000/api/redoc
```

### Auto-Scraping Configuration
The API includes automatic scraping every 48 hours. Configure via:
```bash
curl -X PUT "http://localhost:8000/api/v1/admin/config" \
  -H "Content-Type: application/json" \
  -d '{"scraping_interval_hours": 24}'
```

## 📊 Current Status

- **Pages Scraped**: 443 URLs
- **Content Volume**: 4.1M+ characters
- **Vector Database**: 708 chunks indexed
- **Tables Extracted**: 270 structured tables
- **Quality Score**: 0.63 average
- **API Status**: Production-ready with auto-scraping

## 📋 API Endpoints

### Chat
- `POST /api/v1/chat` - Send message to AI bot
- `GET /api/v1/chat/sessions` - Get active chat sessions

### Data Management
- `POST /api/v1/data/scrape` - Initiate scraping job
- `GET /api/v1/data/scrape/{job_id}` - Get scraping job status
- `POST /api/v1/data/ingest` - Initiate ingestion job
- `GET /api/v1/data/ingest/{job_id}` - Get ingestion job status

### System Status
- `GET /api/v1/status` - Comprehensive system status
- `GET /health` - Quick health check

### Administration
- `GET /api/v1/admin/config` - Get system configuration
- `PUT /api/v1/admin/config` - Update system configuration
- `GET /api/v1/admin/jobs` - List all jobs
- `POST /api/v1/admin/jobs/cancel/{job_id}` - Cancel a job

## 📝 Documentation

### Comprehensive HTML Documentation
Access the full documentation website by opening `index.html` in your browser. Features include:

- **Complete Usage Guide**: Step-by-step instructions for all CLI options
- **API Documentation**: Detailed endpoint descriptions with examples
- **Client Examples**: Python and JavaScript code samples
- **Troubleshooting**: Solutions for common issues
- **Performance Metrics**: System requirements and benchmarks
- **Configuration Guide**: Auto-scraping schedule and system settings

### Additional Documentation Files
- `API_DOCUMENTATION.md` - Complete API reference
- `API_README.md` - API quick start guide
- `docs/MASTER_DEVELOPMENT_JOURNAL.md` - Full development history
- `docs/API_DEVELOPMENT_JOURNAL.md` - API development progress

## ⚡ Auto-Scraping System

The background scheduler automatically:
- **Scrapes MOSDAC website** every 48 hours (configurable)
- **Ingests scraped data** into the vector database
- **Monitors system health** every 5 minutes
- **Collects performance metrics** regularly

## 🚀 Production Deployment

### Using Gunicorn + Uvicorn
```bash
pip install gunicorn uvloop httptools
gunicorn src.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `LLM_PROVIDER`: LLM service provider
- `LLM_API_KEY`: API key for LLM service
- `DATABASE_URL`: Vector database connection string

## 🚨 Troubleshooting

### Common Issues
1. **API won't start**: Check dependencies and Python version
2. **Scraping fails**: Verify network connectivity and website availability
3. **LLM not responding**: Check LLM configuration and API keys
4. **Vector DB errors**: Verify ChromaDB installation and permissions

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
python -m src.api.main
```

## 📈 Performance

- **Scraping**: 443 URLs in ~15 minutes
- **Ingestion**: 708 chunks in ~110 seconds
- **Retrieval**: Sub-second response times
- **Chat**: Real-time natural language responses
- **API**: Handles 100+ requests per minute

## 🛡️ Quality Assurance

- **Source Citations**: Every response includes source references
- **Quality Scoring**: Automated content quality assessment
- **Session Management**: Context retention across conversations
- **Error Handling**: Graceful failure recovery
- **Rate Limiting**: API protection against abuse

## 🔄 Available Operations

1. **Scrape Data Only** - Extract all MOSDAC content
2. **Ingest Data Only** - Process scraped data into vector DB
3. **Scrape + Ingest** - Complete workflow
4. **Chat with Bot** - Interactive Q&A
5. **Check Data Status** - View system status
6. **Remove All Data** - Clean up data
7. **Re-scrape + Re-ingest** - Full refresh
8. **API Access** - RESTful interface for all operations

## 🤖 LLM Configuration

The bot supports two LLM modes:

### API Mode (Default)
- Uses Gemini API
- Faster, no local setup required
- Requires `GEMINI_API_KEY`

### Ollama Mode (Offline)
- Uses local Ollama installation
- Private, offline operation
- Requires Ollama server running

---

**Status**: Fully Functional ✅  
**API Status**: Production-Ready with Auto-Scraping ✅  
**Last Updated**: September 14, 2025  
**Version**: 2.0
