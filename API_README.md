# MOSDAC AI Help Bot API

A production-ready REST API for the MOSDAC AI Help Bot with automatic web scraping and data ingestion capabilities.

## 🚀 Features

- **RESTful API**: Clean, well-documented endpoints for all functionality
- **Auto-Scraping**: Automatic website scraping every 48 hours (configurable)
- **Real-time Chat**: AI-powered chat with MOSDAC website content
- **Background Jobs**: Asynchronous scraping and ingestion jobs
- **Configuration Management**: Dynamic system configuration via API
- **Health Monitoring**: Comprehensive system status and metrics
- **Rate Limiting**: Built-in protection against abuse
- **Production Ready**: Error handling, logging, and monitoring

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

## ⚙️ Auto-Scraping System

The API includes a sophisticated background scheduling system that automatically:

1. **Scrapes MOSDAC website** every 48 hours
2. **Ingests scraped data** into the vector database
3. **Monitors system health** every 5 minutes
4. **Collects performance metrics** regularly

### Configuration

The auto-scraping behavior can be configured via the admin API:

```bash
# Change scraping interval to 24 hours
curl -X PUT "http://localhost:8000/api/v1/admin/config" \
  -H "Content-Type: application/json" \
  -d '{"scraping_interval_hours": 24}'

# Disable auto-scraping
curl -X PUT "http://localhost:8000/api/v1/admin/config" \
  -H "Content-Type: application/json" \
  -d '{"enable_auto_scraping": false}'
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager
- Internet connection (for scraping and LLM access)

### Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Start the API server**:
```bash
python -m src.api.main
```

3. **Test the API**:
```bash
python test_api.py
```

4. **Access API documentation**:
   - Open: http://localhost:8000/api/docs
   - Or: http://localhost:8000/api/redoc

### Manual Scraping & Ingestion

If you want to manually trigger scraping and ingestion:

```bash
# Start scraping job
curl -X POST "http://localhost:8000/api/v1/data/scrape" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.mosdac.gov.in"], "max_pages": 100}'

# Check job status (replace {job_id} with actual ID)
curl "http://localhost:8000/api/v1/data/scrape/{job_id}"

# Start ingestion job
curl -X POST "http://localhost:8000/api/v1/data/ingest" \
  -H "Content-Type: application/json" \
  -d '{"data_directory": "./data/scraped/mosdac_complete_data"}'
```

## 🏗️ Architecture

### File Structure
```
src/api/
├── main.py              # FastAPI app entry point
├── config.py           # Configuration management
├── models/             # Pydantic models
│   ├── chat.py         # Chat request/response models
│   ├── status.py       # Status models
│   ├── data.py         # Data job models
│   └── admin.py        # Admin models
├── routes/             # API routers
│   ├── chat.py         # Chat endpoints
│   ├── status.py       # Status endpoints
│   ├── data.py         # Data endpoints
│   └── admin.py        # Admin endpoints
└── background/         # Background tasks
    └── scheduler.py    # APScheduler integration
```

### Core Components

1. **FastAPI Application**: Main web server with CORS, middleware, and routers
2. **Configuration System**: Dynamic configuration with file persistence
3. **Background Scheduler**: APScheduler for automatic jobs
4. **Job Management**: Async job processing with status tracking
5. **Error Handling**: Comprehensive error handling and logging

## 🔧 Configuration

The system configuration is stored in `config/system_config.json` and can be managed via API:

### Key Configuration Options

- `scraping_interval_hours`: Auto-scraping interval (default: 48)
- `max_scraping_pages`: Maximum pages per scraping job (default: 1000)
- `enable_auto_scraping`: Enable/disable auto-scraping (default: true)
- `api_rate_limit`: Requests per minute limit (default: 100)
- `embedding_model`: Default embedding model (default: "all-MiniLM-L6-v2")

### View Current Configuration

```bash
curl "http://localhost:8000/api/v1/admin/config"
```

## 📊 Monitoring

### Health Checks
```bash
curl "http://localhost:8000/health"
```

### System Status
```bash
curl "http://localhost:8000/api/v1/status"
```

### Job Monitoring
```bash
curl "http://localhost:8000/api/v1/admin/jobs"
```

## 🚨 Troubleshooting

### Common Issues

1. **API won't start**: 
   - Check dependencies: `pip install -r requirements.txt`
   - Check Python version: `python --version`

2. **Scraping fails**:
   - Check network connectivity
   - Verify website availability: `curl -I https://www.mosdac.gov.in`

3. **LLM not responding**:
   - Check LLM configuration in environment variables
   - Verify API keys if using external LLM services

4. **Vector DB errors**:
   - Check ChromaDB installation
   - Verify storage permissions

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export LOG_LEVEL=DEBUG
python -m src.api.main
```

## 🚀 Production Deployment

### Using Gunicorn + Uvicorn

```bash
pip install gunicorn uvloop httptools
gunicorn src.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "-m", "src.api.main"]
```

### Environment Variables

- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `LLM_PROVIDER`: LLM service provider (openai, anthropic, etc.)
- `LLM_API_KEY`: API key for LLM service
- `DATABASE_URL`: Vector database connection string

## 📈 Performance Tips

1. **Use async/await** for I/O-bound operations
2. **Enable caching** for frequent requests
3. **Monitor memory usage** during large scraping jobs
4. **Use appropriate chunk sizes** for ingestion (512 tokens default)
5. **Limit concurrent jobs** based on system resources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review API documentation at `/api/docs`
3. Check server logs for error details
4. Open an issue on GitHub with detailed information

---

**Note**: This API is designed for the MOSDAC AI Help Bot project. Ensure you have proper authorization before scraping websites and comply with all terms of service and robots.txt directives.
