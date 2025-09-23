"""
MOSDAC AI Help Bot - Flask Frontend Application
Comprehensive middleware implementation with all improvements from documentation
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from flask_session import Session
import requests
import json
import time
import logging
import uuid
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
import os
from dotenv import load_dotenv
import hashlib
try:
    import PyJWT as jwt
except ImportError:
    try:
        import jwt
    except ImportError:
        jwt = None
        print("Warning: PyJWT not available, some features may be limited")

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Backend API configuration
    BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')
    BACKEND_TIMEOUT = int(os.environ.get('BACKEND_TIMEOUT', '30'))
    
    # Security configuration
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE', '60'))
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    
    # Cache configuration
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', '300'))
    CACHE_MAX_SIZE = int(os.environ.get('CACHE_MAX_SIZE', '1000'))
    
    # Session configuration - simplified for development
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = False  # Disable signing to avoid cookie issues
    SESSION_KEY_PREFIX = 'mosdac_'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

app.config.from_object(Config)

# Initialize extensions
CORS(app, resources={
    r"/api/*": {
        "origins": Config.CORS_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key", "X-Requested-With"],
        "expose_headers": ["Content-Type", "X-Request-ID"],
        "max_age": 3600,
        "supports_credentials": True
    }
})

Session(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_frontend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cache implementation
class CacheManager:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.stats = {'hits': 0, 'misses': 0}
    
    def get(self, key):
        if key in self.cache:
            data, timestamp, ttl = self.cache[key]
            if time.time() - timestamp < ttl:
                self.stats['hits'] += 1
                return data
            else:
                del self.cache[key]
        
        self.stats['misses'] += 1
        return None
    
    def set(self, key, value, ttl=300):
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
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

cache_manager = CacheManager(Config.CACHE_MAX_SIZE)

# Rate limiting
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

rate_limiter = RateLimiter(Config.RATE_LIMIT_REQUESTS_PER_MINUTE)

# API Client with connection pooling
class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = self._create_session()
    
    def _create_session(self):
        session = requests.Session()
        
        # Configure adapter with connection pooling
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
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
        kwargs.setdefault('timeout', Config.BACKEND_TIMEOUT)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            if isinstance(e, requests.exceptions.Timeout):
                raise Exception("Request timeout")
            elif isinstance(e, requests.exceptions.ConnectionError):
                raise Exception("Connection error")
            else:
                raise Exception(f"Request failed: {str(e)}")

api_client = APIClient(Config.BACKEND_URL)

# Decorators
def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
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

def cached(ttl=300):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = f(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
            
        return decorated
    return decorator

def require_session(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'session_id' not in session:
            session['session_id'] = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            session['created_at'] = datetime.now().isoformat()
        
        return f(*args, **kwargs)
    
    return decorated

# Request logging
@app.before_request
def before_request():
    request.start_time = time.time()
    request.request_id = str(uuid.uuid4())
    
    # Log request details (excluding sensitive data)
    logger.info(f"Request {request.request_id}: {request.method} {request.path}")
    
    if request.is_json and request.path != '/api/chat':  # Don't log chat content
        data = request.get_json()
        if data:
            sanitized_data = {k: v for k, v in data.items() if k not in ['password', 'token', 'api_key']}
            logger.info(f"Data: {sanitized_data}")

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        logger.info(f"Response {request.request_id}: {response.status_code} - {duration:.3f}s")
    
    return response

# Error handlers
@app.errorhandler(Exception)
def handle_error(error):
    if hasattr(request, 'request_id'):
        logger.error(f"Error {request.request_id}: {str(error)}")
    else:
        logger.error(f"Error: {str(error)}")
    
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'Internal server error'
        }
    }), 500

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'API endpoint not found'
            }
        }), 404
    return render_template('404.html'), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'RATE_LIMITED',
            'message': 'Too many requests. Please try again later.'
        }
    }), 429

# Utility functions
def validate_input(data, required_fields, optional_fields=None):
    """Validate input data against required and optional fields"""
    errors = []
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not data[field]:
            errors.append(f"Field cannot be empty: {field}")
    
    if optional_fields:
        for field in optional_fields:
            if field in data and data[field] is None:
                errors.append(f"Field cannot be null: {field}")
    
    return errors

def sanitize_input(text):
    """Sanitize text input to prevent injection attacks"""
    if not isinstance(text, str):
        return text
    
    import re
    text = re.sub(r'[<>"\']', '', text)
    
    if len(text) > 10000:
        text = text[:10000]
    
    return text.strip()

def validate_language_code(language):
    """Validate language code"""
    valid_languages = ['en', 'hi', 'ta', 'te', 'bn', 'mr', 'gu', 'kn', 'ml', 'pa']
    return language in valid_languages

def get_chat_response_with_fallback(query, session_id, language='en'):
    """Get chat response with fallback for when backend is unavailable"""
    try:
        response = api_client.request('POST', '/api/v1/chat', json={
            'query': query,
            'session_id': session_id,
            'language': language
        })
        return response
        
    except Exception as e:
        logger.error(f"Backend unavailable: {str(e)}")
        
        # Enhanced fallback responses based on query content
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['satellite', 'data', 'download']):
            response_text = """I can help you with satellite data access! Here's how to download satellite data from MOSDAC:

1. **Visit MOSDAC Portal**: Go to www.mosdac.gov.in
2. **Register/Login**: Create an account or login to access data
3. **Browse Data**: Navigate to Data → Satellite Data
4. **Select Parameters**: Choose satellite, sensor, date range, and area
5. **Download**: Click download and wait for processing

**Popular Satellite Data:**
- INSAT-3D/3DR for weather monitoring
- Oceansat-2 for ocean observations  
- Cartosat for land applications
- RISAT for radar imaging

Would you like specific guidance for any particular satellite or data type?"""
            
        elif any(word in query_lower for word in ['weather', 'meteorological', 'climate']):
            response_text = """MOSDAC provides comprehensive weather and meteorological data! Here's what's available:

**Weather Data Types:**
- Temperature and humidity profiles
- Precipitation data
- Wind speed and direction
- Atmospheric pressure
- Cloud imagery and analysis

**Data Sources:**
- INSAT-3D/3DR satellites
- Ground-based weather stations
- Numerical weather prediction models

**Access Methods:**
1. Real-time data through MOSDAC portal
2. Historical archives for research
3. API access for automated retrieval
4. Mobile apps for quick access

What specific weather parameter are you interested in?"""
            
        elif any(word in query_lower for word in ['ocean', 'sea', 'marine']):
            response_text = """MOSDAC offers extensive oceanographic data! Here's what you can access:

**Ocean Parameters:**
- Sea surface temperature (SST)
- Ocean color and chlorophyll
- Sea surface height
- Ocean currents
- Wave height and direction

**Satellite Sources:**
- Oceansat-2 and Oceansat-3
- INSAT series for SST
- SARAL/AltiKa for altimetry

**Applications:**
- Fisheries and aquaculture
- Coastal zone management
- Marine weather forecasting
- Climate studies

Which ocean parameter interests you most?"""
            
        elif any(word in query_lower for word in ['navigation', 'help', 'guide', 'how']):
            response_text = """I'm here to help you navigate MOSDAC! Here are the main sections:

**🏠 Home**: Overview and latest updates
**📊 Data**: Access all satellite and ground data
**🔍 Search**: Find specific datasets
**📱 Services**: Web services and APIs  
**📚 Resources**: Documentation and tutorials
**👥 User**: Account management and support

**Quick Tips:**
- Use the search function to find specific data
- Check the data calendar for availability
- Register for full data access
- Contact support for technical issues

What specific area would you like help with?"""
            
        else:
            response_text = f"""Hello! I'm LEO, your MOSDAC AI assistant. I can help you with:

**🛰️ Satellite Data**: Download and access various satellite datasets
**🌤️ Weather Information**: Meteorological data and forecasts  
**🌊 Ocean Data**: Oceanographic observations and analysis
**🧭 Navigation**: Guide you through the MOSDAC portal
**📞 Support**: Technical assistance and documentation

You asked: "{query}"

I'm currently running in demo mode. For full functionality, the backend API needs to be connected. However, I can still provide guidance and information about MOSDAC services!

What would you like to know more about?"""
        
        return {
            'response': response_text,
            'sources': [
                {
                    'title': 'MOSDAC Portal',
                    'url': 'https://www.mosdac.gov.in',
                    'relevance': 0.9
                },
                {
                    'title': 'MOSDAC Data Catalog',
                    'url': 'https://www.mosdac.gov.in/data',
                    'relevance': 0.8
                }
            ],
            'metadata': {
                'fallback': True,
                'session_id': session_id,
                'response_time_ms': 150,
                'message_count': 1,
                'demo_mode': True
            }
        }

# Routes
@app.route('/')
def index():
    """Main page with chatbot interface"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin dashboard"""
    return render_template('admin.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    return render_template('analytics.html')

# API Routes
@app.route('/api/chat', methods=['POST'])
@rate_limit
@require_session
def handle_chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        
        # Validate input - accept both 'query' and 'message' parameters
        message_field = 'query' if 'query' in data else 'message'
        validation_errors = validate_input(data, [message_field], ['language'])
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
        query = sanitize_input(data[message_field])
        language = data.get('language', 'en')
        session_id = session.get('session_id', 'default')
        
        # Validate language
        if not validate_language_code(language):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_LANGUAGE',
                    'message': 'Invalid language code'
                }
            }), 400
        
        # Get response from backend with fallback
        backend_data = get_chat_response_with_fallback(query, session_id, language)
        
        # Transform response for frontend
        return jsonify({
            'success': True,
            'data': {
                'response': backend_data['response'],
                'sources': backend_data.get('sources', []),
                'metadata': {
                    'session_id': session_id,
                    'message_count': backend_data.get('metadata', {}).get('message_count', 0),
                    'response_time_ms': backend_data.get('metadata', {}).get('response_time_ms', 0),
                    'timestamp': datetime.now().isoformat(),
                    'fallback': backend_data.get('metadata', {}).get('fallback', False)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error'
            }
        }), 500

@app.route('/api/navigation/guide', methods=['POST'])
@rate_limit
@require_session
def handle_navigation_guide():
    """Handle navigation guidance requests"""
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
        response = api_client.request('POST', '/api/v1/navigation/guide', json={
            'query': data['query'],
            'user_id': session.get('session_id'),
            'context': data.get('context', {})
        })
        
        return jsonify({
            'success': True,
            'data': response.get('data', {}),
            'processing_time': response.get('processing_time', 0)
        })
        
    except Exception as e:
        logger.error(f"Navigation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'NAVIGATION_ERROR',
                'message': 'Navigation service error'
            }
        }), 500

@app.route('/api/feedback/submit', methods=['POST'])
@rate_limit
@require_session
def handle_feedback_submit():
    """Handle feedback submission"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['message_id', 'feedback_type', 'rating', 'user_query', 'bot_response']
        validation_errors = validate_input(data, required_fields)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Input validation failed',
                    'details': validation_errors
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
        
        # Add session ID
        data['session_id'] = session.get('session_id')
        
        # Forward to backend feedback service
        response = api_client.request('POST', '/api/v1/feedback/submit', json=data)
        
        return jsonify({
            'success': True,
            'data': {
                'feedback_id': response.get('feedback_id'),
                'message': response.get('message', 'Feedback submitted successfully')
            }
        })
        
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'FEEDBACK_ERROR',
                'message': 'Feedback service error'
            }
        }), 500

@app.route('/api/status', methods=['GET'])
@cached(ttl=60)
def handle_system_status():
    """Get system status"""
    try:
        # Get status from backend
        backend_status = api_client.request('GET', '/api/v1/status')
        
        # Add middleware-specific status
        return jsonify({
            'success': True,
            'data': {
                'backend': backend_status,
                'middleware': {
                    'status': 'healthy',
                    'cache_stats': cache_manager.get_stats(),
                    'rate_limiter_active': True,
                    'session_count': len(session),
                    'timestamp': datetime.now().isoformat()
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Status error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'STATUS_ERROR',
                'message': 'Failed to get system status'
            }
        }), 500

@app.route('/api/sessions', methods=['GET'])
@require_session
def get_chat_sessions():
    """Get chat sessions"""
    try:
        response = api_client.request('GET', '/api/v1/chat/sessions')
        return jsonify({
            'success': True,
            'data': response
        })
    except Exception as e:
        logger.error(f"Sessions error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'SESSIONS_ERROR',
                'message': 'Failed to get sessions'
            }
        }), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_chat_session(session_id):
    """Get specific chat session"""
    try:
        response = api_client.request('GET', f'/api/v1/chat/sessions/{session_id}')
        return jsonify({
            'success': True,
            'data': response
        })
    except Exception as e:
        logger.error(f"Session error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'SESSION_ERROR',
                'message': 'Failed to get session'
            }
        }), 500

@app.route('/api/feedback/analytics', methods=['GET'])
@cached(ttl=300)
def get_feedback_analytics():
    """Get feedback analytics"""
    try:
        response = api_client.request('GET', '/api/v1/feedback/analytics')
        return jsonify({
            'success': True,
            'data': response
        })
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'ANALYTICS_ERROR',
                'message': 'Failed to get analytics'
            }
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'flask': True,
            'cache': len(cache_manager.cache) >= 0,
            'rate_limiter': True,
            'backend': True  # Could add actual backend health check
        }
    })

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache (admin function)"""
    cache_manager.clear()
    return jsonify({
        'success': True,
        'message': 'Cache cleared successfully'
    })

@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """Get cache statistics"""
    return jsonify({
        'success': True,
        'data': cache_manager.get_stats()
    })

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=Config.DEBUG
    )
