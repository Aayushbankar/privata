# MOSDAC AI Help Bot

An AI-powered help bot for information retrieval from the MOSDAC (Meteorological and Oceanographic Satellite Data Archival Center) website.

## 🚀 Quick Start

```bash
# Run the bot
./scripts/run_bot.sh

# Or manually
python main.py
```

## 📁 Project Structure

```
privata/
├── src/                          # Source code
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
│   └── PROJECT_STATUS_REPORT.md
├── main.py                       # Main entry point
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## 🛠️ Features

- **Comprehensive Web Scraping**: 443 URLs processed (7x more than required)
- **RAG-Optimized Data Extraction**: 4.1M+ characters, 270 structured tables
- **Advanced Ingestion Pipeline**: 708 semantic chunks stored in ChromaDB
- **Fully Functional Chat System**: Natural language Q&A with citations
- **Dual LLM Support**: Gemini API + Ollama offline modes
- **Complete Data Management**: Status monitoring, removal, re-scraping

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

## 🎯 Usage

### Main Bot Interface
```bash
python main.py
```

### Direct Core Access
```bash
python src/core/mosdac_bot.py
```

### Test System
```bash
python tests/test_chat.py
```

## 📊 Current Status

- **Pages Scraped**: 443 URLs
- **Content Volume**: 4.1M+ characters
- **Vector Database**: 708 chunks indexed
- **Tables Extracted**: 270 structured tables
- **Quality Score**: 0.63 average

## 🔄 Available Operations

1. **Scrape Data Only** - Extract all MOSDAC content
2. **Ingest Data Only** - Process scraped data into vector DB
3. **Scrape + Ingest** - Complete workflow
4. **Chat with Bot** - Interactive Q&A
5. **Check Data Status** - View system status
6. **Remove All Data** - Clean up data
7. **Re-scrape + Re-ingest** - Full refresh

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

## 📈 Performance

- **Scraping**: 443 URLs in ~15 minutes
- **Ingestion**: 708 chunks in ~110 seconds
- **Retrieval**: Sub-second response times
- **Chat**: Real-time natural language responses

## 🛡️ Quality Assurance

- **Source Citations**: Every response includes source references
- **Quality Scoring**: Automated content quality assessment
- **Session Management**: Context retention across conversations
- **Error Handling**: Graceful failure recovery

## 📝 Documentation

- `docs/PROJECT_PROGRESS_REPORT.md` - Detailed development history
- `docs/PROJECT_STATUS_REPORT.md` - Current system status
- `scripts/setup_llm.py` - LLM configuration helper

## 🚀 Next Steps

1. **Continuous Crawling** - Automated updates
2. **Self-Learning** - Feedback collection and improvement
3. **Production Deployment** - Web interface and API
4. **Advanced Features** - Enhanced NLU and analytics

---

**Status**: Fully Functional ✅  
**Last Updated**: September 13, 2025  
**Version**: 1.0
