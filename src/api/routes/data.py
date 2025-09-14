"""
Data API router for MOSDAC AI Help Bot.

This module provides REST API endpoints for data management operations
including scraping, ingestion, and data statistics.
"""

import os
import sys
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import models and dependencies
from src.api.models.data import (
    ScrapingRequest, IngestionRequest, JobResponse,
    JobListResponse, DataStatistics, DataValidationResult,
    ScrapingJob, IngestionJob, ScrapingStatus, IngestionStatus
)
from src.api.dependencies import get_scraper, get_ingestor

# Create router
router = APIRouter()

# Job storage (in production, use database)
scraping_jobs: Dict[str, ScrapingJob] = {}
ingestion_jobs: Dict[str, IngestionJob] = {}

@router.post("/data/scrape", response_model=JobResponse)
async def start_scraping(
    request: ScrapingRequest,
    background_tasks: BackgroundTasks,
    scraper = Depends(get_scraper)
):
    """
    Start a scraping job to collect data from MOSDAC website.
    
    This endpoint initiates a background scraping job that will
    collect content from the MOSDAC website for AI processing.
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Create job entry
        scraping_jobs[job_id] = ScrapingJob(
            job_id=job_id,
            status=ScrapingStatus.PENDING,
            pages_scraped=0,
            total_pages=request.max_pages
        )
        
        # Start background task
        background_tasks.add_task(
            run_scraping_job,
            job_id,
            request.urls,
            request.max_pages,
            request.force_rescrape
        )
        
        return JobResponse(
            job_id=job_id,
            status="started",
            message=f"Scraping job {job_id} started successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start scraping job: {str(e)}"
        )


@router.post("/data/ingest", response_model=JobResponse)
async def start_ingestion(
    request: IngestionRequest,
    background_tasks: BackgroundTasks,
    ingestor = Depends(get_ingestor)
):
    """
    Start an ingestion job to process scraped data.
    
    This endpoint initiates a background ingestion job that will
    process scraped content and store it in the vector database.
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Create job entry
        ingestion_jobs[job_id] = IngestionJob(
            job_id=job_id,
            status=IngestionStatus.PENDING,
            documents_processed=0,
            chunks_created=0
        )
        
        # Start background task
        background_tasks.add_task(
            run_ingestion_job,
            job_id,
            request.data_path,
            request.force_reingest
        )
        
        return JobResponse(
            job_id=job_id,
            status="started",
            message=f"Ingestion job {job_id} started successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start ingestion job: {str(e)}"
        )


@router.get("/data/scrape/{job_id}", response_model=ScrapingJob)
async def get_scraping_job(job_id: str):
    """
    Get status of a specific scraping job.
    
    Returns detailed information about a scraping job including
    current status, progress, and any errors.
    """
    if job_id not in scraping_jobs:
        raise HTTPException(status_code=404, detail="Scraping job not found")
    
    return scraping_jobs[job_id]


@router.get("/data/ingest/{job_id}", response_model=IngestionJob)
async def get_ingestion_job(job_id: str):
    """
    Get status of a specific ingestion job.
    
    Returns detailed information about an ingestion job including
    current status, progress, and any errors.
    """
    if job_id not in ingestion_jobs:
        raise HTTPException(status_code=404, detail="Ingestion job not found")
    
    return ingestion_jobs[job_id]


@router.get("/data/scrape", response_model=JobListResponse)
async def list_scraping_jobs():
    """
    List all scraping jobs.
    
    Returns information about all scraping jobs, both active and completed.
    """
    jobs = [job.model_dump() for job in scraping_jobs.values()]
    return JobListResponse(
        jobs=jobs,
        total_count=len(jobs)
    )


@router.get("/data/ingest", response_model=JobListResponse)
async def list_ingestion_jobs():
    """
    List all ingestion jobs.
    
    Returns information about all ingestion jobs, both active and completed.
    """
    jobs = [job.model_dump() for job in ingestion_jobs.values()]
    return JobListResponse(
        jobs=jobs,
        total_count=len(jobs)
    )


@router.delete("/data/scrape/{job_id}")
async def cancel_scraping_job(job_id: str):
    """
    Cancel a scraping job.
    
    Attempts to cancel a running scraping job. Only jobs in PENDING or RUNNING
    state can be cancelled.
    """
    if job_id not in scraping_jobs:
        raise HTTPException(status_code=404, detail="Scraping job not found")
    
    job = scraping_jobs[job_id]
    if job.status not in [ScrapingStatus.PENDING, ScrapingStatus.RUNNING]:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel job that is not pending or running"
        )
    
    job.status = ScrapingStatus.CANCELLED
    job.end_time = datetime.now()
    
    return {"message": f"Scraping job {job_id} cancelled successfully"}


@router.delete("/data/ingest/{job_id}")
async def cancel_ingestion_job(job_id: str):
    """
    Cancel an ingestion job.
    
    Attempts to cancel a running ingestion job. Only jobs in PENDING or RUNNING
    state can be cancelled.
    """
    if job_id not in ingestion_jobs:
        raise HTTPException(status_code=404, detail="Ingestion job not found")
    
    job = ingestion_jobs[job_id]
    if job.status not in [IngestionStatus.PENDING, IngestionStatus.RUNNING]:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel job that is not pending or running"
        )
    
    job.status = IngestionStatus.CANCELLED
    job.end_time = datetime.now()
    
    return {"message": f"Ingestion job {job_id} cancelled successfully"}


@router.get("/data/stats", response_model=DataStatistics)
async def get_data_statistics(
    scraper = Depends(get_scraper),
    ingestor = Depends(get_ingestor)
):
    """
    Get data statistics.
    
    Returns comprehensive statistics about scraped and ingested data
    including counts, sizes, and timestamps.
    """
    try:
        # Get vector DB stats (need to implement this function)
        from src.retrieval.modern_vectordb import get_vector_db_stats
        vector_stats = get_vector_db_stats()
        
        return DataStatistics(
            total_pages=scraper.get_page_count(),
            total_documents=vector_stats["document_count"],
            total_chunks=vector_stats["chunk_count"],
            last_scraped=scraper.get_last_scraped_time(),
            last_ingested=vector_stats["last_ingested"],
            storage_size_mb=scraper.get_storage_size_mb()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get data statistics: {str(e)}"
        )


@router.get("/data/validate", response_model=DataValidationResult)
async def validate_data():
    """
    Validate scraped and ingested data.
    
    Performs validation checks on the scraped data and vector database
    to ensure data integrity and consistency.
    """
    # TODO: Implement comprehensive data validation
    # For now, return basic validation result
    return DataValidationResult(
        valid=True,
        issues=[],
        warnings=["Data validation not fully implemented"]
    )


async def run_scraping_job(job_id: str, urls: Optional[List[str]], max_pages: int, force_rescrape: bool):
    """Background task to run scraping job."""
    try:
        scraper = get_scraper()
        scraping_jobs[job_id].status = ScrapingStatus.RUNNING
        scraping_jobs[job_id].start_time = datetime.now()
        
        # Run scraping
        if urls:
            # Scrape specific URLs
            results = await scraper.scrape_specific_urls(urls, force_rescrape)
        else:
            # Full site scraping
            results = await scraper.scrape_website(max_pages=max_pages, force_rescrape=force_rescrape)
        
        scraping_jobs[job_id].status = ScrapingStatus.COMPLETED
        scraping_jobs[job_id].pages_scraped = len(results)
        scraping_jobs[job_id].end_time = datetime.now()
        
    except Exception as e:
        scraping_jobs[job_id].status = ScrapingStatus.FAILED
        scraping_jobs[job_id].error_message = str(e)
        scraping_jobs[job_id].end_time = datetime.now()


async def run_ingestion_job(job_id: str, data_path: Optional[str], force_reingest: bool):
    """Background task to run ingestion job."""
    try:
        ingestor = get_ingestor()
        ingestion_jobs[job_id].status = IngestionStatus.RUNNING
        ingestion_jobs[job_id].start_time = datetime.now()
        
        # Run ingestion
        if data_path:
            result = ingestor.ingest_from_path(data_path, force_reingest)
        else:
            result = ingestor.ingest_all(force_reingest)
        
        ingestion_jobs[job_id].status = IngestionStatus.COMPLETED
        ingestion_jobs[job_id].documents_processed = result["documents_processed"]
        ingestion_jobs[job_id].chunks_created = result["chunks_created"]
        ingestion_jobs[job_id].end_time = datetime.now()
        
    except Exception as e:
        ingestion_jobs[job_id].status = IngestionStatus.FAILED
        ingestion_jobs[job_id].error_message = str(e)
        ingestion_jobs[job_id].end_time = datetime.now()
