# MOSDAC AI Help Bot - Middleware Integration Documentation

## Overview

This document provides a comprehensive guide for creating middleware between the MOSDAC AI Help Bot API and Flask frontend. It covers all API endpoints, data models, authentication, error handling, and implementation patterns needed for seamless integration.

## Table of Contents

1. [API Architecture Overview](#api-architecture-overview)
2. [Complete API Endpoints Reference](#complete-api-endpoints-reference)
3. [Data Models and Schemas](#data-models-and-schemas)
4. [Authentication and Authorization](#authentication-and-authorization)
5. [Error Handling Patterns](#error-handling-patterns)
6. [Middleware Implementation Guide](#middleware-implementation-guide)
7. [Frontend Integration Patterns](#frontend-integration-patterns)
8. [Performance Optimization](#performance-optimization)
9. [Security Considerations](#security-considerations)
10. [Deployment Configuration](#deployment-configuration)

---

## API Architecture Overview

### Base Configuration
- **Base URL**: `http://localhost:8000`
- **API Version**: `/api/v1`
- **Protocol**: HTTP/HTTPS
- **Data Format**: JSON
- **CORS**: Enabled for development origins

### Core Components
1. **FastAPI Backend**: RESTful API server
2. **Background Scheduler**: Automated scraping and ingestion
3. **Vector Database**: ChromaDB for document storage
4. **LLM Integration**: Multiple LLM providers support
5. **Feedback System**: User feedback collection and analytics
6. **Navigation Assistant**: Step-by-step guidance system

### Middleware Responsibilities
- **Request Routing**: Forward frontend requests to appropriate API endpoints
- **Response Transformation**: Format API responses for frontend consumption
- **Session Management**: Handle user sessions and context
- **Error Handling**: Graceful error handling and user-friendly messages
- **Caching**: Implement caching for improved performance
- **Authentication**: Manage user authentication and authorization

---

## Complete API Endpoints Reference

### 1. Chat Endpoints

#### POST `/api/v1/chat`
**Description**: Send a chat message to the AI help bot
**Request Body**:
```json
{
  "query": "What is MOSDAC?",
  "session_id": "user_session_123",
  "language": "en",
  "stream": false
}
```

**Response**:
```json
{
  "response": "MOSDAC is the Meteorological & Oceanographic Satellite Data Archival Centre...",
  "sources": [
    {
      "url": "https://www.mosdac.gov.in/about",
      "title": "About MOSDAC",
      "relevance": 0.85
    }
  ],
  "metadata": {
    "session_id": "user_session_123",
    "message_count": 5,
    "response_time_ms": 1200
  }
}
```

**Middleware Implementation**:
```python
@app.route('/api/chat', methods=['POST'])
def handle_chat():
    try:
        # Forward request to backend API
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat",
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            # Transform response for frontend
            return {
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'error': 'Backend service unavailable',
                'status_code': response.status_code
            }, response.status_code
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to process chat request'
        }, 500
```

#### GET `/api/v1/chat/sessions`
**Description**: List all active chat sessions
**Response**:
```json
{
  "sessions": [
    {
      "session_id": "user_session_123",
      "created_at": "2024-01-15T10:30:00Z",
      "message_count": 5,
      "last_activity": "2024-01-15T10:35:00Z"
    }
  ],
  "total_count": 1
}
```

#### GET `/api/v1/chat/sessions/{session_id}`
**Description**: Get detailed information about a specific session
**Response**:
```json
{
  "session_id": "user_session_123",
  "created_at": "2024-01-15T10:30:00Z",
  "last_activity": "2024-01-15T10:35:00Z",
  "messages": [
    {
      "query": "What is MOSDAC?",
      "response": "MOSDAC is...",
      "timestamp": "2024-01-15T10:31:00Z",
      "sources": [...]
    }
  ],
  "message_count": 5
}
```

#### DELETE `/api/v1/chat/sessions/{session_id}`
**Description**: Delete a specific chat session

#### DELETE `/api/v1/chat/sessions`
**Description**: Clear all chat sessions

#### POST `/api/v1/chat/stream`
**Description**: Stream chat responses in real-time
**Response**: Server-Sent Events (SSE) stream

### 2. Data Management Endpoints

#### POST `/api/v1/data/scrape`
**Description**: Start a scraping job
**Request Body**:
```json
{
  "urls": ["https://www.mosdac.gov.in"],
  "max_pages": 100,
  "force_rescrape": false
}
```

**Response**:
```json
{
  "job_id": "scrape_job_123",
  "status": "started",
  "message": "Scraping job started successfully"
}
```

#### GET `/api/v1/data/scrape/{job_id}`
**Description**: Get status of a scraping job
**Response**:
```json
{
  "job_id": "scrape_job_123",
  "status": "completed",
  "pages_scraped": 85,
  "total_pages": 100,
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T10:35:00Z",
  "error": null
}
```

#### POST `/api/v1/data/ingest`
**Description**: Start an ingestion job
**Request Body**:
```json
{
  "data_path": "./data/scraped/mosdac_complete_data",
  "force_reingest": false
}
```

#### GET `/api/v1/data/ingest/{job_id}`
**Description**: Get status of an ingestion job

#### GET `/api/v1/data/scrape`
**Description**: List all scraping jobs

#### GET `/api/v1/data/ingest`
**Description**: List all ingestion jobs

### 3. Status Endpoints

#### GET `/api/v1/status`
**Description**: Get comprehensive system status
**Response**:
```json
{
  "scraped_data": {
    "pages_count": 85000,
    "total_content_length": 12500000,
    "last_scraped": "2024-01-15T10:30:00Z",
    "data_path": "./data/scraped/mosdac_complete_data"
  },
  "vector_database": {
    "collection_exists": true,
    "document_count": 75000,
    "chunk_count": 150000,
    "last_ingested": "2024-01-15T10:35:00Z"
  },
  "components": {
    "crawler_available": true,
    "ingest_available": true,
    "chat_available": true,
    "llm_available": true
  },
  "llm": {
    "mode": "ollama",
    "api_key_set": false,
    "ollama_model": "llama2",
    "ollama_url": "http://localhost:11434",
    "available": true
  },
  "system": {
    "memory_usage_mb": 512.5,
    "cpu_percent": 15.2,
    "disk_usage_percent": 45.8,
    "uptime_seconds": 86400
  },
  "timestamp": "2024-01-15T10:40:00Z"
}
```

#### GET `/api/v1/status/health`
**Description**: Quick health check
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:40:00Z",
  "components": {
    "bot": true,
    "scraper": true,
    "ingestor": true,
    "llm": true,
    "vector_db": true
  }
}
```

#### GET `/api/v1/status/resources`
**Description**: Get system resource usage

#### GET `/api/v1/status/performance`
**Description**: Get performance metrics

### 4. Admin Endpoints

#### GET `/api/v1/admin/config`
**Description**: Get system configuration
**Response**:
```json
{
  "config": {
    "scraping_interval_hours": 48,
    "max_scraping_pages": 1000,
    "chunk_size": 512,
    "chunk_overlap": 50,
    "max_concurrent_jobs": 5,
    "api_rate_limit": 100,
    "enable_auto_scraping": true,
    "enable_auto_ingestion": true,
    "embedding_model": "all-MiniLM-L6-v2"
  },
  "message": "Configuration retrieved successfully"
}
```

#### PUT `/api/v1/admin/config`
**Description**: Update system configuration
**Request Body**:
```json
{
  "scraping_interval_hours": 24,
  "max_scraping_pages": 500,
  "enable_auto_scraping": true
}
```

#### GET `/api/v1/admin/logs`
**Description**: Retrieve system logs

#### GET `/api/v1/admin/cache/stats`
**Description**: Get cache statistics

#### GET `/api/v1/admin/metrics`
**Description**: Get system metrics

#### POST `/api/v1/admin/maintenance`
**Description**: Perform maintenance operations

### 5. Navigation Endpoints

#### POST `/api/v1/navigation/guide`
**Description**: Get step-by-step navigation guidance
**Request Body**:
```json
{
  "query": "How to download satellite data?",
  "user_id": "user_123",
  "context": {}
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "intent": "download_data",
    "confidence": 0.85,
    "steps": [
      {
        "step_number": 1,
        "instruction": "Navigate to MOSDAC homepage",
        "url": "https://www.mosdac.gov.in",
        "element_selector": ".nav-home"
      },
      {
        "step_number": 2,
        "instruction": "Click on 'Data Products' menu",
        "url": "https://www.mosdac.gov.in/data",
        "element_selector": ".menu-data"
      }
    ],
    "total_steps": 5,
    "estimated_time": "3-5 minutes",
    "difficulty": "easy"
  },
  "processing_time": 0.125
}
```

#### GET `/api/v1/navigation/intent`
**Description**: Detect navigation intent
**Parameters**: `query` (string)
**Response**:
```json
{
  "success": true,
  "data": {
    "query": "download data",
    "intent": "download_data",
    "confidence": 0.92
  },
  "processing_time": 0.045
}
```

#### GET `/api/v1/navigation/structure`
**Description**: Get MOSDAC site structure

#### POST `/api/v1/navigation/path`
**Description**: Get optimized navigation path

#### GET `/api/v1/navigation/health`
**Description**: Navigation service health check

### 6. Feedback Endpoints

#### POST `/api/v1/feedback/submit`
**Description**: Submit user feedback
**Request Body**:
```json
{
  "session_id": "user_session_123",
  "message_id": "msg_456",
  "feedback_type": "chat_response",
  "rating": 4,
  "comment": "Very helpful response!",
  "user_query": "What is MOSDAC?",
  "bot_response": "MOSDAC is...",
  "language": "en"
}
```

**Response**:
```json
{
  "feedback_id": "feedback_789",
  "message": "Feedback submitted successfully. Thank you for helping us improve!"
}
```

#### GET `/api/v1/feedback/analytics`
**Description**: Get feedback analytics
**Response**:
```json
{
  "total_feedback": 150,
  "average_rating": 4.2,
  "rating_distribution": {
    "1": 5,
    "2": 10,
    "3": 20,
    "4": 45,
    "5": 70
  },
  "feedback_by_type": {
    "chat_response": 120,
    "navigation": 30
  },
  "feedback_by_language": {
    "en": 100,
    "hi": 30,
    "ta": 20
  },
  "common_issues": [
    {
      "issue": "Response too generic",
      "count": 15,
      "percentage": 10.0
    }
  ]
}
```

#### GET `/api/v1/feedback/list`
**Description**: Get filtered list of feedback entries

#### GET `/api/v1/feedback/session/{session_id}`
**Description**: Get feedback for a specific session

#### GET `/api/v1/feedback/trends`
**Description**: Get feedback trends over time

#### GET `/api/v1/feedback/health`
**Description**: Feedback system health check

### 7. System Endpoints

#### GET `/`
**Description**: Root endpoint with API information
**Response**:
```json
{
  "message": "MOSDAC AI Help Bot API",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:40:00Z",
  "endpoints": {
    "chat": "/api/v1/chat",
    "status": "/api/v1/status",
    "data": "/api/v1/data",
    "admin": "/api/v1/admin",
    "navigation": "/api/v1/navigation",
    "docs": "/api/docs"
  }
}
```

#### GET `/health`
**Description**: Quick health check
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:40:00Z"
}
```

---

## Data Models and Schemas

### Chat Models

#### ChatRequest
```python
class ChatRequest(BaseModel):
    query: str  # Natural language query (1-1000 chars)
    session_id: Optional[str] = "default"  # Session ID for context
    language: Optional[str] = "en"  # Language code
    stream: Optional[bool] = False  # Stream response
```

#### ChatResponse
```python
class ChatResponse(BaseModel):
    response: str  # AI-generated response
    sources: List[Source]  # Source documents
    metadata: Dict[str, Any]  # Additional metadata
```

#### Source
```python
class Source(BaseModel):
    url: str  # Source URL
    title: str  # Document title
    relevance: float  # Relevance score (0.0-1.0)
```

### Data Management Models

#### ScrapingRequest
```python
class ScrapingRequest(BaseModel):
    urls: List[str]  # URLs to scrape
    max_pages: int = 100  # Maximum pages to scrape
    force_rescrape: bool = False  # Force re-scraping
```

#### IngestionRequest
```python
class IngestionRequest(BaseModel):
    data_path: str  # Path to scraped data
    force_reingest: bool = False  # Force re-ingestion
```

### Navigation Models

#### NavigationRequest
```python
class NavigationRequest(BaseModel):
    query: str  # User query
    user_id: Optional[str] = None  # User identifier
    context: Optional[Dict[str, Any]] = None  # Additional context
```

#### NavigationResponse
```python
class NavigationResponse(BaseModel):
    success: bool  # Operation success status
    data: Optional[Dict[str, Any]] = None  # Response data
    error: Optional[str] = None  # Error message
    processing_time: Optional[float] = None  # Processing time in seconds
```

### Feedback Models

#### FeedbackRequest
```python
class FeedbackRequest(BaseModel):
    session_id: str  # Session identifier
    message_id: str  # Message identifier
    feedback_type: FeedbackType  # Type of feedback
    rating: int  # Rating (1-5)
    comment: Optional[str] = None  # Optional comment
    user_query: str  # Original user query
    bot_response: str  # Bot response
    language: Optional[str] = "en"  # Language code
```

#### FeedbackAnalytics
```python
class FeedbackAnalytics(BaseModel):
    total_feedback: int  # Total feedback count
    average_rating: float  # Average rating
    rating_distribution: Dict[int, int]  # Rating distribution
    feedback_by_type: Dict[str, int]  # Feedback by type
    feedback_by_language: Dict[str, int]  # Feedback by language
    common_issues: List[Dict[str, Any]]  # Common issues
```

---

## Authentication and Authorization

### Current Status
- **Development**: No authentication required
- **Production**: API key authentication recommended

### Middleware Authentication Implementation

```python
from functools import wraps
import jwt
from flask import request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
            
        try:
            # Extract token from header
            token = auth_header.split(' ')[1]
            
            # Verify token (implement your verification logic)
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            
            # Add user info to request context
            request.user = payload
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
    return decorated

# Example protected endpoint
@app.route('/api/protected/chat', methods=['POST'])
@require_auth
def protected_chat():
    # User info available in request.user
    user_id = request.user.get('user_id')
    # Proceed with chat logic
```

### API Key Authentication

```python
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
            
        # Validate API key against database or configuration
        if not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
            
        return f(*args, **kwargs)
        
    return decorated
```

---

## Error Handling Patterns

### Standard Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional error details"
  },
  "timestamp": "2024-01-15T10:40:00Z"
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | BAD_REQUEST | Invalid request parameters |
| 401 | UNAUTHORIZED | Authentication required |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |
| 503 | SERVICE_UNAVAILABLE | Backend service unavailable |

### Middleware Error Handler

```python
@app.errorhandler(Exception)
def handle_error(error):
    # Log the error
    app.logger.error(f"Error occurred: {str(error)}")
    
    # Determine error type and status code
    if isinstance(error, ValueError):
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(error)
            }
        }), 400
    elif isinstance(error, ConnectionError):
        return jsonify({
            'success': False,
            'error': {
                'code': 'BACKEND_UNAVAILABLE',
                'message': 'Backend service is currently unavailable'
            }
        }), 503
    else:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred'
            }
        }), 500
```

### Graceful Degradation

```python
def get_chat_response_with_fallback(query, session_id, language='en'):
    try:
        # Try to get response from backend
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={'query': query, 'session_id': session_id, 'language': language}
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException:
        # Fallback response when backend is unavailable
        return {
            'response': 'I apologize, but I\'m currently experiencing technical difficulties. Please try again later.',
            'sources': [],
            'metadata': {
                'fallback': True,
                'session_id': session_id
            }
        }
```

---

## Middleware Implementation Guide

### Basic Flask Middleware Structure

```python
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import requests
import json
from datetime import datetime
import logging
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
BACKEND_URL = 'http://localhost:8000'
CACHE_TIMEOUT = 300  # 5 minutes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple cache implementation
cache = {}

def get_cache_key(prefix, *args):
    return f"{prefix}:{':'.join(str(arg) for arg in args)}"

def cached_response(timeout=CACHE_TIMEOUT):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            cache_key = get_cache_key(f.__name__, *args)
            
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if datetime.now().timestamp() - timestamp < timeout:
                    return jsonify(cached_data)
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache[cache_key] = (result.get_json(), datetime.now().timestamp())
            return result
            
        return decorated
    return decorator
```

### Chat Middleware Implementation

```python
@app.route('/api/chat', methods=['POST'])
def handle_chat():
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_QUERY',
                    'message': 'Query parameter is required'
                }
            }), 400
        
        # Set default session ID if not provided
        session_id = data.get('session_id', 'default')
        language = data.get('language', 'en')
        
        # Forward request to backend
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={
                'query': data['query'],
                'session_id': session_id,
                'language': language,
                'stream': data.get('stream', False)
            },
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            backend_data = response.json()
            
            # Transform response for frontend
            return jsonify({
                'success': True,
                'data': {
                    'response': backend_data['response'],
                    'sources': backend_data['sources'],
                    'metadata': {
                        'session_id': session_id,
                        'message_count': backend_data['metadata'].get('message_count', 0),
                        'response_time_ms': backend_data['metadata'].get('response_time_ms', 0),
                        'timestamp': datetime.now().isoformat()
                    }
                }
            })
        else:
            logger.error(f"Backend error: {response.status_code} - {response.text}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BACKEND_ERROR',
                    'message': 'Backend service error',
                    'status_code': response.status_code
                }
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': {
                'code': 'TIMEOUT',
                'message': 'Request timeout'
            }
        }), 504
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error'
            }
        }), 500
```

### Navigation Middleware Implementation

```python
@app.route('/api/navigation/guide', methods=['POST'])
def handle_navigation_guide():
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_QUERY',
                    'message': 'Query parameter is required'
                }
            }), 400
        
        # Forward to backend navigation service
        response = requests.post(
            f"{BACKEND_URL}/api/v1/navigation/guide",
            json={
                'query': data['query'],
                'user_id': data.get('user_id'),
                'context': data.get('context', {})
            },
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            backend_data = response.json()
            
            return jsonify({
                'success': True,
                'data': backend_data['data'],
                'processing_time': backend_data.get('processing_time', 0)
            })
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NAVIGATION_ERROR',
                    'message': 'Navigation service error'
                }
            }), response.status_code
            
    except Exception as e:
        logger.error(f"Navigation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error'
            }
        }), 500
```

### Feedback Middleware Implementation

```python
@app.route('/api/feedback/submit', methods=['POST'])
def handle_feedback_submit():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['session_id', 'message_id', 'feedback_type', 'rating', 'user_query', 'bot_response']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'{field} is required'
                    }
                }), 400
        
        # Validate rating range
        if not 1 <= data['rating'] <= 5:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_RATING',
                    'message': 'Rating must be between 1 and 5'
                }
            }), 400
        
        # Forward to backend feedback service
        response = requests.post(
            f"{BACKEND_URL}/api/v1/feedback/submit",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            backend_data = response.json()
            
            return jsonify({
                'success': True,
                'data': {
                    'feedback_id': backend_data['feedback_id'],
                    'message': backend_data['message']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FEEDBACK_ERROR',
                    'message': 'Feedback service error'
                }
            }), response.status_code
            
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error'
            }
        }), 500
```

### Status Middleware Implementation

```python
@app.route('/api/status', methods=['GET'])
@cached_response(timeout=60)  # Cache for 1 minute
def handle_system_status():
    try:
        # Get status from backend
        response = requests.get(
            f"{BACKEND_URL}/api/v1/status",
            timeout=10
        )
        
        if response.status_code == 200:
            backend_data = response.json()
            
            # Add middleware-specific status
            return jsonify({
                'success': True,
                'data': {
                    'backend': backend_data,
                    'middleware': {
                        'status': 'healthy',
                        'cache_size': len(cache),
                        'uptime': 'N/A',  # Implement uptime tracking
                        'timestamp': datetime.now().isoformat()
                    }
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'STATUS_ERROR',
                    'message': 'Failed to get system status'
                }
            }), response.status_code
            
    except Exception as e:
        logger.error(f"Status error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error'
            }
        }), 500
```

---

## Frontend Integration Patterns

### JavaScript API Client

```javascript
class MOSDACAPIClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.sessionId = this.generateSessionId();
        this.selectedLanguage = 'en';
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error?.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Chat methods
    async sendMessage(query, language = this.selectedLanguage) {
        return this.request('/api/chat', {
            method: 'POST',
            body: JSON.stringify({
                query,
                session_id: this.sessionId,
                language,
                stream: false
            })
        });
    }

    async getChatSessions() {
        return this.request('/api/chat/sessions');
    }

    async getChatSession(sessionId) {
        return this.request(`/api/chat/sessions/${sessionId}`);
    }

    // Navigation methods
    async getNavigationGuidance(query) {
        return this.request('/api/navigation/guide', {
            method: 'POST',
            body: JSON.stringify({
                query,
                user_id: this.sessionId
            })
        });
    }

    async detectNavigationIntent(query) {
        return this.request(`/api/navigation/intent?query=${encodeURIComponent(query)}`);
    }

    // Feedback methods
    async submitFeedback(feedbackData) {
        return this.request('/api/feedback/submit', {
            method: 'POST',
            body: JSON.stringify({
                ...feedbackData,
                session_id: this.sessionId,
                language: this.selectedLanguage
            })
        });
    }

    async getFeedbackAnalytics() {
        return this.request('/api/feedback/analytics');
    }

    // Status methods
    async getSystemStatus() {
        return this.request('/api/status');
    }

    async getHealthStatus() {
        return this.request('/health');
    }
}

// Usage example
const apiClient = new MOSDACAPIClient();

// Send a chat message
async function handleUserMessage(message) {
    try {
        const response = await apiClient.sendMessage(message);
        
        // Display response
        displayBotMessage(response.data.response);
        
        // Show sources if available
        if (response.data.sources && response.data.sources.length > 0) {
            displaySources(response.data.sources);
        }
        
        // Show feedback option
        showFeedbackOption();
        
    } catch (error) {
        console.error('Chat error:', error);
        displayErrorMessage('Sorry, I encountered an error. Please try again.');
    }
}

// Get navigation guidance
async function handleNavigationRequest(query) {
    try {
        const response = await apiClient.getNavigationGuidance(query);
        
        if (response.success && response.data) {
            displayNavigationSteps(response.data.steps);
        } else {
            displayErrorMessage('Navigation guidance not available.');
        }
        
    } catch (error) {
        console.error('Navigation error:', error);
        displayErrorMessage('Sorry, I cannot provide navigation guidance at the moment.');
    }
}

// Submit feedback
async function submitFeedback(rating, comment = '') {
    try {
        const response = await apiClient.submitFeedback({
            message_id: lastMessageId,
            feedback_type: 'chat_response',
            rating: rating,
            comment: comment,
            user_query: lastUserQuery,
            bot_response: lastBotResponse
        });
        
        if (response.success) {
            showFeedbackSuccess();
        }
        
    } catch (error) {
        console.error('Feedback error:', error);
        showFeedbackError();
    }
}
```

### React Integration Example

```jsx
import React, { useState, useEffect } from 'react';
import MOSDACAPIClient from './api-client';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [selectedLanguage, setSelectedLanguage] = useState('en');
    
    const apiClient = new MOSDACAPIClient();

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const userMessage = {
            id: Date.now(),
            text: inputValue,
            sender: 'user',
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            const response = await apiClient.sendMessage(inputValue, selectedLanguage);
            
            const botMessage = {
                id: Date.now() + 1,
                text: response.data.response,
                sender: 'bot',
                timestamp: new Date().toISOString(),
                sources: response.data.sources
            };

            setMessages(prev => [...prev, botMessage]);
            
        } catch (error) {
            const errorMessage = {
                id: Date.now() + 1,
                text: 'Sorry, I encountered an error. Please try again.',
                sender: 'bot',
                timestamp: new Date().toISOString(),
                error: true
            };
            
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleLanguageChange = (language) => {
        setSelectedLanguage(language);
        apiClient.selectedLanguage = language;
    };

    return (
        <div className="chat-interface">
            <div className="chat-header">
                <h3>MOSDAC AI Assistant</h3>
                <select 
                    value={selectedLanguage}
                    onChange={(e) => handleLanguageChange(e.target.value)}
                    className="language-selector"
                >
                    <option value="en">English</option>
                    <option value="hi">हिंदी</option>
                    <option value="ta">தமிழ்</option>
                    <option value="te">తెలుగు</option>
                </select>
            </div>
            
            <div className="messages-container">
                {messages.map((message) => (
                    <div key={message.id} className={`message ${message.sender}`}>
                        <div className="message-content">
                            {message.text}
                            {message.sources && message.sources.length > 0 && (
                                <div className="sources">
                                    <h4>Sources:</h4>
                                    <ul>
                                        {message.sources.map((source, index) => (
                                            <li key={index}>
                                                <a href={source.url} target="_blank" rel="noopener noreferrer">
                                                    {source.title}
                                                </a>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                        <span className="timestamp">
                            {new Date(message.timestamp).toLocaleTimeString()}
                        </span>
                    </div>
                ))}
                
                {isLoading && (
                    <div className="message bot loading">
                        <div className="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                )}
            </div>
            
            <div className="input-area">
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask about MOSDAC..."
                    disabled={isLoading}
                />
                <button 
                    onClick={handleSendMessage}
                    disabled={isLoading || !inputValue.trim()}
                >
                    Send
                </button>
            </div>
        </div>
    );
};

export default ChatInterface;
```

---

## Performance Optimization

### Caching Strategy

```python
from functools import wraps
import time
from flask import request

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.stats = {'hits': 0, 'misses': 0}
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache[key][2]:  # Check TTL
                self.stats['hits'] += 1
                return data
            else:
                # Remove expired entry
                del self.cache[key]
        
        self.stats['misses'] += 1
        return None
    
    def set(self, key, value, ttl=300):
        self.cache[key] = (value, time.time(), ttl)
    
    def clear(self):
        self.cache.clear()
    
    def get_stats(self):
        total = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total if total > 0 else 0
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': hit_rate,
            'total_entries': len(self.cache)
        }

cache_manager = CacheManager()

def cached(ttl=300):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Generate cache key based on function name and arguments
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
            
        return decorated
    return decorator
```

### Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = self._create_session()
    
    def _create_session(self):
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        
        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        
        # Set default timeout
        kwargs.setdefault('timeout', 30)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Handle different types of request exceptions
            if isinstance(e, requests.exceptions.Timeout):
                raise Exception("Request timeout")
            elif isinstance(e, requests.exceptions.ConnectionError):
                raise Exception("Connection error")
            else:
                raise Exception(f"Request failed: {str(e)}")

# Usage
api_client = APIClient('http://localhost:8000')
```

### Rate Limiting

```python
from flask import request, jsonify
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, key):
        now = time.time()
        minute_ago = now - 60
        
        # Remove old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > minute_ago]
        
        # Check if under limit
        if len(self.requests[key]) < self.requests_per_minute:
            self.requests[key].append(now)
            return True
        
        return False

rate_limiter = RateLimiter()

def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get client IP
        client_ip = request.remote_addr
        
        if not rate_limiter.is_allowed(client_ip):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'RATE_LIMITED',
                    'message': 'Too many requests. Please try again later.'
                }
            }), 429
        
        return f(*args, **kwargs)
    
    return decorated

# Apply rate limiting to endpoints
@app.route('/api/chat', methods=['POST'])
@rate_limit
def handle_chat():
    # Chat implementation
    pass
```

---

## Security Considerations

### Input Validation

```python
from flask import request
import re

def validate_input(data, required_fields, optional_fields=None):
    """Validate input data against required and optional fields"""
    errors = []
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not data[field]:
            errors.append(f"Field cannot be empty: {field}")
    
    # Check optional fields if provided
    if optional_fields:
        for field in optional_fields:
            if field in data and data[field] is None:
                errors.append(f"Field cannot be null: {field}")
    
    return errors

def sanitize_input(text):
    """Sanitize text input to prevent injection attacks"""
    if not isinstance(text, str):
        return text
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(text) > 10000:
        text = text[:10000]
    
    return text.strip()

def validate_language_code(language):
    """Validate language code"""
    valid_languages = ['en', 'hi', 'ta', 'te', 'bn', 'mr', 'gu', 'kn', 'ml', 'pa']
    return language in valid_languages

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    try:
        data = request.get_json()
        
        # Validate input
        validation_errors = validate_input(data, ['query'], ['session_id', 'language'])
        if validation_errors:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Input validation failed',
                    'details': validation_errors
                }
            }), 400
        
        # Sanitize inputs
        query = sanitize_input(data['query'])
        session_id = sanitize_input(data.get('session_id', 'default'))
        language = data.get('language', 'en')
        
        # Validate language
        if not validate_language_code(language):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_LANGUAGE',
                    'message': 'Invalid language code'
                }
            }), 400
        
        # Process the request...
        
    except Exception as e:
        # Handle errors
        pass
```

### CORS Configuration

```python
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS with specific settings
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://yourdomain.com"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-API-Key",
            "X-Requested-With"
        ],
        "expose_headers": [
            "Content-Type",
            "X-Request-ID"
        ],
        "max_age": 3600,
        "supports_credentials": True
    }
})
```

### Request Logging

```python
import logging
from flask import request, g
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('middleware.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    """Log incoming requests"""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()
    
    # Log request details
    logger.info(f"Request {g.request_id}: {request.method} {request.path}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Don't log sensitive data
    if request.is_json:
        data = request.get_json()
        if data:
            # Sanitize sensitive fields
            sanitized_data = {k: v for k, v in data.items() if k not in ['password', 'token', 'api_key']}
            logger.info(f"Data: {sanitized_data}")

@app.after_request
def after_request(response):
    """Log response details"""
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        logger.info(f"Response {g.request_id}: {response.status_code} - {duration:.3f}s")
    
    return response

@app.errorhandler(Exception)
def handle_error(error):
    """Log errors"""
    if hasattr(g, 'request_id'):
        logger.error(f"Error {g.request_id}: {str(error)}")
    else:
        logger.error(f"Error: {str(error)}")
    
    # Return error response
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'Internal server error'
        }
    }), 500
```

---

## Deployment Configuration

### Production Configuration

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Backend API configuration
    BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')
    BACKEND_TIMEOUT = int(os.environ.get('BACKEND_TIMEOUT', '30'))
    
    # Security configuration
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE', '60'))
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Cache configuration
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', '300'))
    CACHE_MAX_SIZE = int(os.environ.get('CACHE_MAX_SIZE', '1000'))
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'middleware.log')
    
    # Database configuration (if needed)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///middleware.db')
    
    # Authentication configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', '24'))

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    TESTING = True
    BACKEND_URL = 'http://localhost:8001'  # Test backend

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### Docker Deployment

```dockerfile
# Dockerfile for Flask middleware
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  # Flask middleware
  middleware:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - BACKEND_URL=http://backend:8000
      - SECRET_KEY=your-secret-key-here
      - JWT_SECRET_KEY=your-jwt-secret-here
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - mosdac-network

  # FastAPI backend
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped
    networks:
      - mosdac-network

  # Frontend (React/Vue/Static)
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000
    depends_on:
      - middleware
    restart: unless-stopped
    networks:
      - mosdac-network

  # Redis for caching (optional)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - mosdac-network

  # Nginx reverse proxy (optional)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - middleware
      - frontend
    restart: unless-stopped
    networks:
      - mosdac-network

volumes:
  redis_data:

networks:
  mosdac-network:
    driver: bridge
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Middleware API
    location /api/ {
        proxy_pass http://middleware:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin $http_origin always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-API-Key" always;
        
        # Handle preflight requests
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin $http_origin;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-API-Key";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain; charset=utf-8';
            add_header Content-Length 0;
            return 204;
        }
    }
    
    # Backend API (direct access for admin)
    location /backend/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Basic authentication for backend
        auth_basic "Admin Area";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
    
    # Gzip compression
    gzip on;
    gzip_types
        text/plain
        text/css
        text/js
        text/xml
        text/javascript
        application/javascript
        application/json
        application/xml+rss;
}
```

---

## Conclusion

This comprehensive middleware documentation provides all the necessary information to create a robust integration between the MOSDAC AI Help Bot API and Flask frontend. The documentation covers:

1. **Complete API Reference**: All endpoints with request/response examples
2. **Data Models**: Detailed schema definitions for all API interactions
3. **Security Implementation**: Authentication, input validation, and CORS configuration
4. **Error Handling**: Comprehensive error management patterns
5. **Performance Optimization**: Caching, connection pooling, and rate limiting
6. **Frontend Integration**: JavaScript and React implementation examples
7. **Deployment Configuration**: Docker, Nginx, and production setup

### Key Implementation Points:

1. **Start with Basic Middleware**: Implement core routing and error handling first
2. **Add Security**: Implement authentication and input validation early
3. **Optimize Performance**: Add caching and connection pooling for production
4. **Monitor and Log**: Implement comprehensive logging and monitoring
5. **Test Thoroughly**: Test all endpoints and error scenarios
6. **Deploy Securely**: Use proper SSL/TLS and security headers in production

The middleware serves as a crucial layer between the frontend and backend, providing security, performance optimization, and a clean API interface for the frontend application.
