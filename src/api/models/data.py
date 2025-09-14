"""
Pydantic models for data-related API endpoints.

This module defines the request/response schemas for data management operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ScrapingStatus(str, Enum):
    """Scraping job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IngestionStatus(str, Enum):
    """Ingestion job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScrapingJob(BaseModel):
    """Scraping job information."""
    job_id: str = Field(..., description="Unique job identifier")
    status: ScrapingStatus = Field(..., description="Current job status")
    start_time: Optional[datetime] = Field(None, description="Job start timestamp")
    end_time: Optional[datetime] = Field(None, description="Job end timestamp")
    pages_scraped: int = Field(0, description="Number of pages scraped")
    total_pages: Optional[int] = Field(None, description="Total pages to scrape")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class IngestionJob(BaseModel):
    """Ingestion job information."""
    job_id: str = Field(..., description="Unique job identifier")
    status: IngestionStatus = Field(..., description="Current job status")
    start_time: Optional[datetime] = Field(None, description="Job start timestamp")
    end_time: Optional[datetime] = Field(None, description="Job end timestamp")
    documents_processed: int = Field(0, description="Number of documents processed")
    chunks_created: int = Field(0, description="Number of chunks created")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class ScrapingRequest(BaseModel):
    """Request model for starting a scraping job."""
    urls: Optional[List[str]] = Field(None, description="Specific URLs to scrape")
    max_pages: Optional[int] = Field(1000, description="Maximum pages to scrape")
    force_rescrape: bool = Field(False, description="Force re-scraping of existing pages")


class IngestionRequest(BaseModel):
    """Request model for starting an ingestion job."""
    data_path: Optional[str] = Field(None, description="Path to data directory")
    force_reingest: bool = Field(False, description="Force re-ingestion of existing data")


class JobResponse(BaseModel):
    """Response model for job operations."""
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")


class JobListResponse(BaseModel):
    """Response model for listing jobs."""
    jobs: List[Dict[str, Any]] = Field(..., description="List of jobs")
    total_count: int = Field(..., description="Total number of jobs")


class DataStatistics(BaseModel):
    """Data statistics response."""
    total_pages: int = Field(..., description="Total pages scraped")
    total_documents: int = Field(..., description="Total documents in vector DB")
    total_chunks: int = Field(..., description="Total chunks in vector DB")
    last_scraped: Optional[datetime] = Field(None, description="Last scraping timestamp")
    last_ingested: Optional[datetime] = Field(None, description="Last ingestion timestamp")
    storage_size_mb: float = Field(..., description="Storage size in MB")


class DataValidationResult(BaseModel):
    """Data validation result."""
    valid: bool = Field(..., description="Whether data is valid")
    issues: List[str] = Field(..., description="List of validation issues")
    warnings: List[str] = Field(..., description="List of warnings")
