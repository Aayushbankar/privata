"""
Pydantic models for status-related API endpoints.

This module defines the request/response schemas for system status monitoring.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ScrapedDataStatus(BaseModel):
    """Status information about scraped data."""
    pages_count: int = Field(..., description="Number of pages scraped")
    total_content_length: int = Field(..., description="Total content length in characters")
    last_scraped: Optional[datetime] = Field(None, description="Last scraping timestamp")
    data_path: str = Field(..., description="Path to scraped data directory")


class VectorDBStatus(BaseModel):
    """Status information about vector database."""
    collection_exists: bool = Field(..., description="Whether collection exists")
    document_count: int = Field(..., description="Number of documents in collection")
    chunk_count: int = Field(..., description="Number of chunks in collection")
    last_ingested: Optional[datetime] = Field(None, description="Last ingestion timestamp")


class ComponentsStatus(BaseModel):
    """Status information about system components."""
    crawler_available: bool = Field(..., description="Whether crawler is available")
    ingest_available: bool = Field(..., description="Whether ingestion is available")
    chat_available: bool = Field(..., description="Whether chat is available")
    llm_available: bool = Field(..., description="Whether LLM is available")


class LLMStatus(BaseModel):
    """Status information about LLM configuration."""
    mode: str = Field(..., description="LLM mode (api/ollama)")
    api_key_set: Optional[bool] = Field(None, description="Whether API key is set")
    ollama_model: Optional[str] = Field(None, description="Ollama model name")
    ollama_url: Optional[str] = Field(None, description="Ollama server URL")
    available: bool = Field(..., description="Whether LLM is available")


class SystemResources(BaseModel):
    """System resource usage information."""
    memory_usage_mb: float = Field(..., description="Memory usage in MB")
    cpu_percent: float = Field(..., description="CPU usage percentage")
    disk_usage_percent: float = Field(..., description="Disk usage percentage")
    uptime_seconds: float = Field(..., description="System uptime in seconds")


class SystemStatus(BaseModel):
    """Comprehensive system status response."""
    scraped_data: ScrapedDataStatus = Field(..., description="Scraped data status")
    vector_database: VectorDBStatus = Field(..., description="Vector database status")
    components: ComponentsStatus = Field(..., description="Components status")
    llm: LLMStatus = Field(..., description="LLM status")
    system: SystemResources = Field(..., description="System resources")
    timestamp: datetime = Field(..., description="Status check timestamp")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    components: Dict[str, bool] = Field(..., description="Component availability")


class PerformanceMetrics(BaseModel):
    """Performance metrics for the system."""
    scraping_time_seconds: Optional[float] = Field(None, description="Last scraping time")
    ingestion_time_seconds: Optional[float] = Field(None, description="Last ingestion time")
    average_response_time_ms: Optional[float] = Field(None, description="Average chat response time")
    requests_per_minute: Optional[float] = Field(None, description="Request rate")
    error_rate: Optional[float] = Field(None, description="Error rate percentage")
