"""
MOSDAC AI Help Bot - Flask Frontend Configuration
Configuration settings for different environments
"""

import os
from datetime import timedelta
from typing import Dict, Any


class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session configuration
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'mosdac:'
    SESSION_REDIS = None  # Will be set in app factory
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    
    # Cache configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/1'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_KEY_PREFIX = 'mosdac_cache:'
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/2'
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # API configuration
    API_BASE_URL = os.environ.get('API_BASE_URL') or 'http://localhost:8000'
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', '30'))
    API_RETRY_ATTEMPTS = int(os.environ.get('API_RETRY_ATTEMPTS', '3'))
    API_RETRY_BACKOFF = float(os.environ.get('API_RETRY_BACKOFF', '1.0'))
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization', 'X-Requested-With']
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.environ.get('LOG_FILE')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', '5'))
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Language settings
    LANGUAGES = {
        'en': 'English',
        'hi': 'हिन्दी',
        'ta': 'தமிழ்',
        'te': 'తెలుగు',
        'bn': 'বাংলা',
        'mr': 'मराठी',
        'gu': 'ગુજરાતી',
        'kn': 'ಕನ್ನಡ',
        'ml': 'മലയാളം',
        'pa': 'ਪੰਜਾਬੀ'
    }
    DEFAULT_LANGUAGE = 'en'
    
    # Feature flags
    FEATURES = {
        'VOICE_INPUT': os.environ.get('FEATURE_VOICE_INPUT', 'true').lower() == 'true',
        'FILE_UPLOAD': os.environ.get('FEATURE_FILE_UPLOAD', 'true').lower() == 'true',
        'OFFLINE_SUPPORT': os.environ.get('FEATURE_OFFLINE_SUPPORT', 'true').lower() == 'true',
        'ANALYTICS': os.environ.get('FEATURE_ANALYTICS', 'true').lower() == 'true',
        'FEEDBACK': os.environ.get('FEATURE_FEEDBACK', 'true').lower() == 'true',
        'ADMIN_PANEL': os.environ.get('FEATURE_ADMIN_PANEL', 'false').lower() == 'true'
    }
    
    # Performance settings
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=12)
    
    # Health check settings
    HEALTH_CHECK_ENABLED = True
    HEALTH_CHECK_ENDPOINT = '/health'
    
    @staticmethod
    def init_app(app):
        """Initialize application with this config"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'
    
    # Relaxed security for development
    WTF_CSRF_ENABLED = False
    
    # Development API URL
    API_BASE_URL = os.environ.get('API_BASE_URL') or 'http://localhost:8000'
    
    # Cache settings for development
    CACHE_DEFAULT_TIMEOUT = 60  # 1 minute for faster development
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Development-specific initialization
        import logging
        logging.basicConfig(level=logging.DEBUG)


class TestingConfig(Config):
    """Testing configuration"""
    
    DEBUG = False
    TESTING = True
    
    # Use in-memory storage for testing
    SESSION_TYPE = 'filesystem'
    CACHE_TYPE = 'simple'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Test API URL
    API_BASE_URL = 'http://localhost:8000'
    
    # Faster timeouts for testing
    API_TIMEOUT = 5
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)


class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Production rate limiting
    RATELIMIT_DEFAULT = "60 per hour"
    
    # Production cache settings
    CACHE_DEFAULT_TIMEOUT = 3600  # 1 hour
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if Config.LOG_FILE:
                file_handler = RotatingFileHandler(
                    Config.LOG_FILE,
                    maxBytes=Config.LOG_MAX_BYTES,
                    backupCount=Config.LOG_BACKUP_COUNT
                )
                file_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
                file_handler.setLevel(logging.WARNING)
                app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.WARNING)
            app.logger.info('MOSDAC Flask Frontend startup')


class DockerConfig(ProductionConfig):
    """Docker container configuration"""
    
    # Docker-specific settings
    API_BASE_URL = os.environ.get('API_BASE_URL') or 'http://api:8000'
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://redis:6379/0'
    
    @staticmethod
    def init_app(app):
        ProductionConfig.init_app(app)
        
        # Docker-specific initialization
        import logging
        
        # Log to stdout in Docker
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """Get configuration class by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, DevelopmentConfig)


# Environment-specific settings
class EnvironmentConfig:
    """Environment-specific configuration helper"""
    
    @staticmethod
    def get_database_url() -> str:
        """Get database URL based on environment"""
        return os.environ.get('DATABASE_URL') or 'sqlite:///mosdac_frontend.db'
    
    @staticmethod
    def get_redis_config() -> Dict[str, Any]:
        """Get Redis configuration"""
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        
        # Parse Redis URL for detailed config
        if redis_url.startswith('redis://'):
            # Basic Redis URL
            return {
                'url': redis_url,
                'decode_responses': True,
                'socket_keepalive': True,
                'socket_keepalive_options': {},
                'health_check_interval': 30
            }
        elif redis_url.startswith('rediss://'):
            # SSL Redis URL
            return {
                'url': redis_url,
                'decode_responses': True,
                'ssl_cert_reqs': None,
                'socket_keepalive': True,
                'health_check_interval': 30
            }
        else:
            # Fallback configuration
            return {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'decode_responses': True
            }
    
    @staticmethod
    def get_cors_config() -> Dict[str, Any]:
        """Get CORS configuration"""
        return {
            'origins': os.environ.get('CORS_ORIGINS', '*').split(','),
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
            'supports_credentials': True
        }
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production"""
        return os.environ.get('FLASK_ENV') == 'production'
    
    @staticmethod
    def is_development() -> bool:
        """Check if running in development"""
        return os.environ.get('FLASK_ENV') in ('development', 'dev', None)
    
    @staticmethod
    def is_testing() -> bool:
        """Check if running tests"""
        return os.environ.get('FLASK_ENV') == 'testing'


# Application constants
class Constants:
    """Application constants"""
    
    # API endpoints
    API_ENDPOINTS = {
        'CHAT': '/api/chat',
        'NAVIGATION': '/api/navigation',
        'FEEDBACK': '/api/feedback',
        'STATUS': '/api/status',
        'HEALTH': '/api/health'
    }
    
    # Cache keys
    CACHE_KEYS = {
        'API_STATUS': 'api_status',
        'NAVIGATION_DATA': 'navigation_data',
        'USER_SESSION': 'user_session_{session_id}',
        'RATE_LIMIT': 'rate_limit_{ip}_{endpoint}'
    }
    
    # Session keys
    SESSION_KEYS = {
        'USER_ID': 'user_id',
        'SESSION_ID': 'session_id',
        'LANGUAGE': 'language',
        'PREFERENCES': 'preferences',
        'LAST_ACTIVITY': 'last_activity'
    }
    
    # Error messages
    ERROR_MESSAGES = {
        'API_UNAVAILABLE': 'API service is currently unavailable',
        'RATE_LIMIT_EXCEEDED': 'Too many requests. Please try again later.',
        'INVALID_REQUEST': 'Invalid request format',
        'SESSION_EXPIRED': 'Your session has expired. Please refresh the page.',
        'UPLOAD_FAILED': 'File upload failed. Please try again.',
        'NETWORK_ERROR': 'Network error. Please check your connection.'
    }
    
    # Success messages
    SUCCESS_MESSAGES = {
        'FEEDBACK_SUBMITTED': 'Thank you for your feedback!',
        'FILE_UPLOADED': 'File uploaded successfully',
        'PREFERENCES_SAVED': 'Preferences saved successfully'
    }
