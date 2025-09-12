# MOSDAC AI Help Bot

An AI-powered help bot for information retrieval from web content, specifically designed for the MOSDAC (Meteorological and Oceanographic Satellite Data Archival Centre) website.

## 🎯 Project Overview

This project implements a comprehensive RAG (Retrieval-Augmented Generation) system that:
- **Scrapes** website content using intelligent crawling
- **Processes** and **indexes** content for optimal retrieval
- **Provides** natural language chat interface for information retrieval
- **Maintains** context and learns from interactions

## 📁 Project Structure

### Core Files
```
privata/
├── mosdac_bot.py          # 🎮 Master control file - Main entry point
├── main.py                # 🚀 Alternative entry point
├── chat.py                # 💬 Chat system implementation
├── ingest.py              # 📥 Data ingestion pipeline
├── crawl4ai_mosdac.py     # 🕷️ Website crawler
├── config.py              # ⚙️ Configuration management
├── config.json            # 📋 Configuration file
└── requirements.txt       # 📦 Dependencies
```

### Core Modules
```
models/
└── llm_loader.py          # 🤖 LLM integration

retriever/
├── modern_vectordb.py     # 🗄️ Vector database operations
├── multi_modal_embedder.py # 🔤 Text embedding
└── reranker.py            # 🎯 Result reranking

utils/
├── enhanced_chunker.py    # ✂️ Document chunking
├── enhanced_doc_loader.py # 📄 Document loading
└── structured_extractor.py # 🔍 Data extraction
```

### Data Directory
```
crawl4ai_output_enhanced/  # 📊 Scraped website data
├── home/                  # Individual page directories
├── about-us/
├── contact-us/
└── crawling_summary.json  # Scraping statistics
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Master Bot
```bash
python mosdac_bot.py
```

### 3. Choose Your Operation
- **Option 1**: Scrape data only
- **Option 2**: Ingest data only  
- **Option 3**: Complete workflow (scrape + ingest)
- **Option 4**: Chat with the bot
- **Option 5**: Check data status
- **Option 6**: Remove all data
- **Option 7**: Re-scrape and re-ingest
- **Option 8**: Exit

## 🔧 Features

### 🕷️ Intelligent Web Crawling
- **Sitemap Discovery**: Automatically discovers all URLs from sitemap.xml
- **Structured Data Extraction**: Extracts tables, metadata, and structured content
- **Quality Scoring**: Rates content quality for better RAG performance
- **Parallel Processing**: Efficient concurrent crawling

### 📥 Advanced Data Ingestion
- **Semantic Chunking**: Intelligent document segmentation
- **Multi-modal Embeddings**: Rich content representation
- **Deduplication**: Removes duplicate content
- **Quality Filtering**: Keeps only high-quality content

### 💬 Smart Chat System
- **Context-Aware**: Maintains conversation context
- **Source Citations**: Provides source references
- **Reranking**: Optimizes result relevance
- **Natural Language**: Intuitive user interaction

### 🗄️ Vector Database
- **ChromaDB Integration**: Efficient similarity search
- **Persistent Storage**: Data survives restarts
- **Metadata Rich**: Comprehensive content indexing
- **Performance Optimized**: Fast retrieval

## ⚙️ Configuration

Edit `config.json` to customize:
- **Chunking parameters**: Size, overlap, strategy
- **Embedding model**: Text embedding configuration
- **Vector database**: Collection settings
- **Chat system**: Prompt templates and behavior

## 📊 Data Flow

1. **Crawling** → Website content extraction
2. **Processing** → Content cleaning and structuring
3. **Chunking** → Semantic document segmentation
4. **Embedding** → Vector representation creation
5. **Storage** → Vector database indexing
6. **Retrieval** → Similarity-based content search
7. **Generation** → LLM-powered response creation

## 🎯 Use Cases

- **Information Retrieval**: Find specific information quickly
- **FAQ System**: Answer common questions
- **Documentation Search**: Navigate complex documentation
- **Research Assistant**: Help with research tasks
- **Customer Support**: Provide automated support

## 🔍 Technical Details

### RAG Pipeline
- **Retrieval**: Semantic similarity search
- **Augmentation**: Context enrichment
- **Generation**: LLM response creation

### Chunking Strategies
- **Semantic Similarity**: Content-based segmentation
- **Heading-Based**: Structure-aware splitting
- **Table Integrity**: Preserve table structure
- **Hybrid Approach**: Multiple strategies combined

### Embedding Models
- **Sentence Transformers**: High-quality text embeddings
- **Multi-modal**: Content, title, metadata integration
- **Context-Aware**: Relationship-aware representations

## 🚨 Requirements

- Python 3.8+
- ChromaDB
- Sentence Transformers
- BeautifulSoup4
- LangChain
- Crawl4AI (for web crawling)

## 📝 License

This project is part of the MOSDAC AI Help Bot system.

## 🤝 Contributing

This is a specialized system for MOSDAC website content. For modifications or improvements, please refer to the project documentation.

---

**Note**: This system is optimized for the MOSDAC website structure but can be adapted for other websites by modifying the crawler configuration.