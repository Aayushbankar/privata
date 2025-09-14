# MOSDAC AI Help Bot API Documentation

## Overview

The MOSDAC AI Help Bot API provides a RESTful interface for interacting with the AI-powered help bot system. It includes endpoints for chat interactions, data management, system monitoring, and administrative functions.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication for development purposes. In production, consider implementing API key authentication or OAuth2.

## API Endpoints

### Chat Endpoints

#### POST `/chat`

Send a message to the AI help bot.

**Request Body:**
```json
{
  "message": "What is MOSDAC?",
  "session_id": "user_session_123"
}
```

**Response:**
```json
{
  "response": "MOSDAC is the Meteorological & Oceanographic Satellite Data Archival Centre...",
  "session_id": "user_session_123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Data Management Endpoints

#### POST `/data/scrape`

Initiate a web scraping job.

**Request Body:**
```json
{
  "urls": ["https://www.mosdac.gov.in"],
  "max_pages": 100,
  "force_rescrape": false
}
```

**Response:**
```json
{
  "job_id": "scrape_job_123",
  "status": "queued",
  "message": "Scraping job created successfully"
}
```

#### GET `/data/scrape/{job_id}`

Get the status of a scraping job.

**Response:**
```json
{
  "job_id": "scrape_job_123",
  "status": "completed",
  "pages_scraped": 85,
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T10:35:00Z"
}
```

#### POST `/data/ingest`

Initiate data ingestion into vector database.

**Request Body:**
```json
{
  "data_directory": "/path/to/scraped/data",
  "chunk_size": 512,
  "chunk_overlap": 50
}
```

**Response:**
```json
{
  "job_id": "ingest_job_456",
  "status": "queued",
  "message": "Ingestion job created successfully"
}
```

#### GET `/data/ingest/{job_id}`

Get the status of an ingestion job.

**Response:**
```json
{
  "job_id": "ingest_job_456",
  "status": "completed",
  "documents_processed": 1200,
  "start_time": "2024-01-15T10:40:00Z",
  "end_time": "2024-01-15T10:45:00Z"
}
```

### Status Endpoints

#### GET `/status`

Get system status and component health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "bot": true,
    "llm": true,
    "scraper": true,
    "ingestor": true,
    "scheduler": true,
    "vector_db": true
  },
  "metrics": {
    "total_chats": 1500,
    "active_sessions": 25,
    "scraped_pages": 85000,
    "ingested_documents": 75000
  }
}
```

#### GET `/health`

Quick health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Admin Endpoints

#### GET `/admin/config`

Get current system configuration.

**Response:**
```json
{
  "scraping_interval_hours": 48,
  "max_scraping_pages": 1000,
  "chunk_size": 512,
  "chunk_overlap": 50,
  "max_concurrent_jobs": 5,
  "api_rate_limit": 100,
  "enable_auto_scraping": true,
  "enable_auto_ingestion": true,
  "embedding_model": "all-MiniLM-L6-v2"
}
```

#### PUT `/admin/config`

Update system configuration.

**Request Body:**
```json
{
  "scraping_interval_hours": 24,
  "max_scraping_pages": 500,
  "enable_data_validation": true
}
```

**Response:**
```json
{
  "message": "Configuration updated successfully",
  "updated_fields": ["scraping_interval_hours", "max_scraping_pages", "enable_data_validation"]
}
```

#### POST `/admin/jobs/cancel/{job_id}`

Cancel a running job.

**Response:**
```json
{
  "message": "Job cancelled successfully",
  "job_id": "scrape_job_123"
}
```

#### GET `/admin/jobs`

Get list of all jobs.

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "scrape_job_123",
      "type": "scraping",
      "status": "completed",
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:35:00Z"
    },
    {
      "job_id": "ingest_job_456",
      "type": "ingestion",
      "status": "running",
      "created_at": "2024-01-15T10:40:00Z"
    }
  ]
}
```

## Auto-Scraping System

The API includes a background scheduler that automatically runs scraping and ingestion jobs every 48 hours (configurable).

### Scheduled Jobs

1. **Auto-Scraping**: Runs every 48 hours to scrape MOSDAC website
2. **Auto-Ingestion**: Runs after scraping completes to ingest data into vector database
3. **Health Checks**: Runs every 5 minutes to monitor system health
4. **Metrics Collection**: Runs every 5 minutes to collect system metrics

### Configuration

The auto-scraping system can be configured via the `/admin/config` endpoint:

- `scraping_interval_hours`: Interval between auto-scraping runs (default: 48)
- `enable_auto_scraping`: Enable/disable auto-scraping (default: true)
- `enable_auto_ingestion`: Enable/disable auto-ingestion (default: true)
- `max_scraping_pages`: Maximum pages to scrape per job (default: 1000)

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Resource not found
- `500`: Internal server error

Error responses include a JSON object with error details:

```json
{
  "error": "Internal server error",
  "message": "Database connection failed",
  "path": "/api/v1/chat"
}
```

## Rate Limiting

The API includes rate limiting to prevent abuse:

- Default limit: 100 requests per minute per IP
- Configurable via `/admin/config` endpoint

## Setup and Deployment

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the API server:
```bash
python -m src.api.main
```

### Development

Run the test suite:
```bash
python test_api.py
```

### Production Deployment

For production deployment:

1. Use a production WSGI server (Gunicorn + Uvicorn)
2. Configure reverse proxy (Nginx)
3. Set up monitoring and logging
4. Implement proper authentication
5. Configure database persistence
6. Set up backup and recovery procedures

## File Structure

```
src/api/
├── main.py              # FastAPI application entry point
├── config.py           # Configuration management
├── models/             # Pydantic models
│   ├── chat.py
│   ├── status.py
│   ├── data.py
│   └── admin.py
├── routes/             # API routers
│   ├── chat.py
│   ├── status.py
│   ├── data.py
│   └── admin.py
└── background/         # Background tasks
    └── scheduler.py   # APScheduler integration
```

## Dependencies

Key dependencies include:

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `apscheduler`: Background scheduling
- `requests`: HTTP client
- `pydantic`: Data validation
- `chromadb`: Vector database
- `sentence-transformers`: Embeddings

## Monitoring and Logging

The API includes built-in monitoring:

- Health check endpoints
- System metrics collection
- Job status tracking
- Error logging
- Performance monitoring

Use the `/status` endpoint to monitor system health and the `/admin/jobs` endpoint to track background jobs.

## Troubleshooting

Common issues and solutions:

1. **API not starting**: Check dependencies with `pip install -r requirements.txt`
2. **Vector DB errors**: Ensure ChromaDB is properly configured
3. **Scraping failures**: Check network connectivity and website availability
4. **LLM not responding**: Verify LLM configuration and API keys

For detailed debugging, check the server logs and use the health check endpoints.
