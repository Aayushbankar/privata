"""
Status API router for MOSDAC AI Help Bot.

This module provides REST API endpoints for system status monitoring.
"""

import os
import sys
import psutil
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import models and dependencies
from src.api.models.status import (
    SystemStatus, ScrapedDataStatus, VectorDBStatus,
    ComponentsStatus, LLMStatus, SystemResources,
    HealthCheckResponse, PerformanceMetrics
)
from src.api.dependencies import get_bot, get_scraper, get_ingestor
from src.models.llm_loader import get_llm_info
from src.retrieval.modern_vectordb import get_vector_db_stats

# Create router
router = APIRouter()

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """
    Get comprehensive system status information.
    
    Returns detailed status about all system components including:
    - Scraped data status
    - Vector database status
    - Component availability
    - LLM configuration
    - System resource usage
    """
    try:
        # Get scraped data status
        scraper = get_scraper()
        scraped_data_status = ScrapedDataStatus(
            pages_count=scraper.get_page_count(),
            total_content_length=scraper.get_total_content_length(),
            last_scraped=scraper.get_last_scraped_time(),
            data_path=scraper.data_path
        )
        
        # Get vector database status
        vector_db_stats = get_vector_db_stats()
        vector_db_status = VectorDBStatus(
            collection_exists=vector_db_stats["collection_exists"],
            document_count=vector_db_stats["document_count"],
            chunk_count=vector_db_stats["chunk_count"],
            last_ingested=vector_db_stats["last_ingested"]
        )
        
        # Get components status
        components_status = ComponentsStatus(
            crawler_available=True,  # Assuming crawler is always available
            ingest_available=True,    # Assuming ingestion is always available
            chat_available=True,      # Assuming chat is always available
            llm_available=get_llm_info()["available"]
        )
        
        # Get LLM status
        llm_info = get_llm_info()
        llm_status = LLMStatus(
            mode=llm_info["mode"],
            api_key_set=llm_info.get("api_key_set"),
            ollama_model=llm_info.get("ollama_model"),
            ollama_url=llm_info.get("ollama_url"),
            available=llm_info["available"]
        )
        
        # Get system resources
        system_resources = get_system_resources()
        
        return SystemStatus(
            scraped_data=scraped_data_status,
            vector_database=vector_db_status,
            components=components_status,
            llm=llm_status,
            system=system_resources,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system status: {str(e)}"
        )


@router.get("/status/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint for the entire system.
    
    Provides a quick overview of system health and component availability.
    """
    try:
        # Check all components
        bot = get_bot()
        scraper = get_scraper()
        ingestor = get_ingestor()
        llm_info = get_llm_info()
        
        components = {
            "bot": True,  # Bot instance created successfully
            "scraper": True,  # Scraper instance created successfully
            "ingestor": True,  # Ingestor instance created successfully
            "llm": llm_info["available"],
            "vector_db": get_vector_db_stats()["collection_exists"]
        }
        
        return HealthCheckResponse(
            status="healthy" if all(components.values()) else "degraded",
            timestamp=datetime.now(),
            components=components
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"System unhealthy: {str(e)}"
        )


@router.get("/status/resources", response_model=SystemResources)
async def get_resources():
    """
    Get current system resource usage.
    
    Returns detailed information about CPU, memory, disk, and network usage.
    """
    try:
        return get_system_resources()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get resource usage: {str(e)}"
        )


@router.get("/status/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """
    Get performance metrics for the system.
    
    Returns various performance metrics including response times,
    processing times, and error rates.
    """
    # TODO: Implement actual performance metrics collection
    # For now, return placeholder data
    return PerformanceMetrics(
        scraping_time_seconds=None,
        ingestion_time_seconds=None,
        average_response_time_ms=None,
        requests_per_minute=None,
        error_rate=None
    )


def get_system_resources() -> SystemResources:
    """Get current system resource usage."""
    try:
        # Get memory usage
        memory = psutil.virtual_memory()
        
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get disk usage for current directory
        disk = psutil.disk_usage('/')
        
        # Get uptime
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        
        return SystemResources(
            memory_usage_mb=memory.used / (1024 * 1024),
            cpu_percent=cpu_percent,
            disk_usage_percent=disk.percent,
            uptime_seconds=uptime.total_seconds()
        )
    except Exception:
        # Fallback if psutil is not available or fails
        return SystemResources(
            memory_usage_mb=0,
            cpu_percent=0,
            disk_usage_percent=0,
            uptime_seconds=0
        )


@router.get("/status/version")
async def get_version_info():
    """
    Get version information about the system.
    
    Returns version details for the API and all major components.
    """
    return {
        "api_version": "1.0.0",
        "llm_version": get_llm_info().get("model_version", "unknown"),
        "vector_db_version": "chromadb-0.4.22",
        "scraper_version": "1.0.0",
        "ingestor_version": "1.0.0",
        "deployment_timestamp": datetime.now().isoformat()
    }


@router.get("/status/config")
async def get_config_summary():
    """
    Get configuration summary.
    
    Returns a summary of the current system configuration.
    """
    # TODO: Implement actual configuration retrieval
    # For now, return placeholder data
    return {
        "scraping_interval_hours": 48,
        "max_concurrent_jobs": 3,
        "data_retention_days": 30,
        "enable_auto_scraping": True,
        "enable_auto_ingestion": True,
        "llm_mode": get_llm_info()["mode"]
    }
