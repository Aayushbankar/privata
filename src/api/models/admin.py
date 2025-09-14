"""
Pydantic models for admin-related API endpoints.

This module defines the request/response schemas for administrative operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SystemConfig(BaseModel):
    """System configuration model."""
    scraping_interval_hours: int = Field(48, description="Auto-scraping interval in hours")
    max_concurrent_jobs: int = Field(3, description="Maximum concurrent jobs")
    data_retention_days: int = Field(30, description="Data retention period in days")
    enable_auto_scraping: bool = Field(True, description="Enable auto-scraping")
    enable_auto_ingestion: bool = Field(True, description="Enable auto-ingestion")


class ConfigUpdateRequest(BaseModel):
    """Request model for updating system configuration."""
    scraping_interval_hours: Optional[int] = Field(None, description="Auto-scraping interval in hours")
    max_concurrent_jobs: Optional[int] = Field(None, description="Maximum concurrent jobs")
    data_retention_days: Optional[int] = Field(None, description="Data retention period in days")
    enable_auto_scraping: Optional[bool] = Field(None, description="Enable auto-scraping")
    enable_auto_ingestion: Optional[bool] = Field(None, description="Enable auto-ingestion")


class ConfigResponse(BaseModel):
    """Response model for configuration operations."""
    config: SystemConfig = Field(..., description="Current system configuration")
    message: str = Field(..., description="Status message")


class SystemLog(BaseModel):
    """System log entry."""
    timestamp: datetime = Field(..., description="Log timestamp")
    level: str = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    component: str = Field(..., description="Component name")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class LogQuery(BaseModel):
    """Log query parameters."""
    level: Optional[str] = Field(None, description="Filter by log level")
    component: Optional[str] = Field(None, description="Filter by component")
    start_time: Optional[datetime] = Field(None, description="Start time filter")
    end_time: Optional[datetime] = Field(None, description="End time filter")
    limit: int = Field(100, description="Maximum number of logs to return")


class LogResponse(BaseModel):
    """Response model for log queries."""
    logs: List[SystemLog] = Field(..., description="List of log entries")
    total_count: int = Field(..., description="Total number of matching logs")


class CacheStats(BaseModel):
    """Cache statistics."""
    total_entries: int = Field(..., description="Total cache entries")
    hit_count: int = Field(..., description="Cache hit count")
    miss_count: int = Field(..., description="Cache miss count")
    hit_rate: float = Field(..., description="Cache hit rate")
    size_mb: float = Field(..., description="Cache size in MB")


class SystemMetrics(BaseModel):
    """System performance metrics."""
    memory_usage: Dict[str, float] = Field(..., description="Memory usage metrics")
    cpu_usage: Dict[str, float] = Field(..., description="CPU usage metrics")
    disk_usage: Dict[str, float] = Field(..., description="Disk usage metrics")
    network_usage: Dict[str, float] = Field(..., description="Network usage metrics")
    timestamp: datetime = Field(..., description="Metrics timestamp")


class MaintenanceRequest(BaseModel):
    """Request model for maintenance operations."""
    operation: str = Field(..., description="Maintenance operation")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")


class MaintenanceResponse(BaseModel):
    """Response model for maintenance operations."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Status message")
    details: Optional[Dict[str, Any]] = Field(None, description="Operation details")
