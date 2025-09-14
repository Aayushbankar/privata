"""
Configuration management for MOSDAC AI Help Bot API.

This module handles loading, updating, and managing system configuration
for the API, including scraping intervals, job limits, and feature flags.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemConfig(BaseModel):
    """System configuration model."""
    
    # Scraping configuration
    scraping_interval_hours: int = Field(default=48, description="Auto-scraping interval in hours")
    max_scraping_pages: int = Field(default=1000, description="Maximum pages to scrape per job")
    scraping_timeout_seconds: int = Field(default=300, description="Scraping timeout in seconds")
    
    # Ingestion configuration
    chunk_size: int = Field(default=512, description="Text chunk size for ingestion")
    chunk_overlap: int = Field(default=50, description="Chunk overlap size")
    max_documents_per_job: int = Field(default=10000, description="Max documents per ingestion job")
    
    # API configuration
    max_concurrent_jobs: int = Field(default=5, description="Maximum concurrent background jobs")
    job_history_limit: int = Field(default=100, description="Maximum job history entries to keep")
    api_rate_limit: int = Field(default=100, description="API requests per minute limit")
    
    # Feature flags
    enable_auto_scraping: bool = Field(default=True, description="Enable auto-scraping feature")
    enable_auto_ingestion: bool = Field(default=True, description="Enable auto-ingestion feature")
    enable_health_checks: bool = Field(default=True, description="Enable health check feature")
    enable_data_validation: bool = Field(default=False, description="Enable data validation feature")
    
    # Performance settings
    cache_size_mb: int = Field(default=100, description="Cache size in MB")
    vector_db_batch_size: int = Field(default=100, description="Vector DB batch insert size")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Default embedding model")
    
    # Monitoring settings
    log_level: str = Field(default="INFO", description="Logging level")
    metrics_interval_minutes: int = Field(default=5, description="Metrics collection interval")
    retention_days: int = Field(default=30, description="Data retention period in days")

class ConfigManager:
    """Configuration manager for the system."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'config', 'system_config.json'
        )
        self.default_config = SystemConfig()
        self.current_config = self._load_config()
    
    def _load_config(self) -> SystemConfig:
        """Load configuration from file or create default."""
        try:
            config_dir = os.path.dirname(self.config_path)
            os.makedirs(config_dir, exist_ok=True)
            
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                return SystemConfig(**config_data)
            else:
                # Create default config file
                self._save_config(self.default_config)
                return self.default_config
                
        except Exception as e:
            logger.warning(f"Failed to load config from {self.config_path}: {e}")
            return self.default_config
    
    def _save_config(self, config: SystemConfig) -> None:
        """Save configuration to file."""
        try:
            config_dir = os.path.dirname(self.config_path)
            os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config.model_dump(), f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_path}: {e}")
    
    def get_config(self) -> SystemConfig:
        """Get current configuration."""
        return self.current_config
    
    def update_config(self, updates: Dict[str, Any]) -> SystemConfig:
        """
        Update configuration with provided values.
        
        Args:
            updates: Dictionary of configuration updates
            
        Returns:
            Updated configuration
        """
        current_dict = self.current_config.model_dump()
        current_dict.update(updates)
        
        # Validate the updated configuration
        updated_config = SystemConfig(**current_dict)
        self.current_config = updated_config
        
        # Save to file
        self._save_config(updated_config)
        
        logger.info(f"Configuration updated: {updates}")
        return updated_config
    
    def reset_to_defaults(self) -> SystemConfig:
        """Reset configuration to default values."""
        self.current_config = self.default_config
        self._save_config(self.default_config)
        
        logger.info("Configuration reset to defaults")
        return self.current_config
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration and return any issues."""
        issues = []
        
        # Validate scraping interval
        if self.current_config.scraping_interval_hours < 1:
            issues.append("scraping_interval_hours must be at least 1")
        
        # Validate chunk size
        if self.current_config.chunk_size < 100:
            issues.append("chunk_size must be at least 100")
        
        # Validate API rate limit
        if self.current_config.api_rate_limit < 1:
            issues.append("api_rate_limit must be at least 1")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": self.current_config.model_dump()
        }

# Global config manager instance
_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """Get or create global config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config() -> SystemConfig:
    """Get current system configuration."""
    return get_config_manager().get_config()

def update_config(updates: Dict[str, Any]) -> SystemConfig:
    """Update system configuration."""
    return get_config_manager().update_config(updates)

def reset_config() -> SystemConfig:
    """Reset configuration to defaults."""
    return get_config_manager().reset_to_defaults()

def validate_config() -> Dict[str, Any]:
    """Validate current configuration."""
    return get_config_manager().validate_config()

# Export configuration functions for API use
__all__ = [
    'SystemConfig', 'ConfigManager', 'get_config', 
    'update_config', 'reset_config', 'validate_config'
]
