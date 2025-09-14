"""
Background scheduler for auto-scraping and ingestion.

This module provides a scheduled background task system that automatically
runs scraping and ingestion jobs every 48 hours.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import components
from src.scrapers.comprehensive_mosdac_scraper import ComprehensiveMOSDACScraper
from src.ingestion.ingest import ModernIngestionPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()

# Job storage
scheduled_jobs: Dict[str, Any] = {}

async def auto_scraping_job():
    """Background job to automatically scrape MOSDAC website."""
    logger.info("🚀 Starting auto-scraping job...")
    try:
        scraper = ComprehensiveMOSDACScraper()
        
        # Run scraping with reasonable limits
        results = await scraper.run_comprehensive_scraping(max_concurrent=5)
        
        logger.info(f"✅ Auto-scraping completed: {results['urls_processed']} pages scraped")
        return {"success": True, "pages_scraped": results['urls_processed']}
        
    except Exception as e:
        logger.error(f"❌ Auto-scraping failed: {str(e)}")
        return {"success": False, "error": str(e)}

async def auto_ingestion_job():
    """Background job to automatically ingest scraped data."""
    logger.info("🚀 Starting auto-ingestion job...")
    try:
        pipeline = ModernIngestionPipeline()
        
        # Run ingestion
        result = pipeline.run_ingestion("./mosdac_complete_data", deduplicate=True)
        
        logger.info(f"✅ Auto-ingestion completed: {result['chunks_stored']} chunks stored")
        return {"success": True, **result}
        
    except Exception as e:
        logger.error(f"❌ Auto-ingestion failed: {str(e)}")
        return {"success": False, "error": str(e)}

async def auto_scraping_and_ingestion_job():
    """
    Combined job that runs scraping followed by ingestion.
    
    This ensures that newly scraped data gets ingested immediately.
    """
    logger.info("🚀 Starting combined auto-scraping and ingestion job...")
    
    # Run scraping first
    scraping_result = await auto_scraping_job()
    
    if not scraping_result["success"]:
        logger.error("❌ Scraping failed, skipping ingestion")
        return scraping_result
    
    # Wait a bit to ensure files are written
    await asyncio.sleep(2)
    
    # Run ingestion
    ingestion_result = await auto_ingestion_job()
    
    return {
        "scraping": scraping_result,
        "ingestion": ingestion_result,
        "combined_success": scraping_result["success"] and ingestion_result["success"]
    }

def schedule_auto_jobs():
    """Schedule all automatic jobs."""
    # Schedule combined scraping + ingestion every 48 hours
    scraping_job = scheduler.add_job(
        auto_scraping_and_ingestion_job,
        trigger=IntervalTrigger(hours=48),
        id="auto_scraping_ingestion",
        name="Auto Scraping and Ingestion (48h)"
    )
    
    scheduled_jobs["auto_scraping_ingestion"] = scraping_job
    
    # Schedule health check every hour
    health_job = scheduler.add_job(
        health_check_job,
        trigger=IntervalTrigger(hours=1),
        id="health_check",
        name="System Health Check (1h)"
    )
    
    scheduled_jobs["health_check"] = health_job
    
    logger.info("✅ Auto jobs scheduled successfully")

async def health_check_job():
    """Background health check job."""
    logger.info("🔍 Running system health check...")
    try:
        # Basic health checks
        scraper = ComprehensiveMOSDACScraper()
        
        # Check if data directory exists and has content
        data_dir_exists = os.path.exists(scraper.output_dir)
        
        # Check vector database health
        from src.retrieval.modern_vectordb import get_vector_db_stats
        vector_stats = get_vector_db_stats()
        
        # Count pages by checking directory structure
        pages_count = 0
        if data_dir_exists:
            try:
                pages_count = len([d for d in scraper.output_dir.iterdir() if d.is_dir()])
            except:
                pages_count = 0
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "data_directory_exists": data_dir_exists,
            "pages_count": pages_count,
            "vector_db_healthy": vector_stats["collection_exists"],
            "documents_count": vector_stats["document_count"]
        }
        
        logger.info(f"✅ Health check passed: {health_status}")
        return {"success": True, "health": health_status}
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return {"success": False, "error": str(e)}

def get_scheduled_jobs() -> Dict[str, Any]:
    """Get information about all scheduled jobs."""
    jobs_info = {}
    for job_id, job in scheduled_jobs.items():
        jobs_info[job_id] = {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        }
    return jobs_info

def reschedule_job(job_id: str, interval_hours: int):
    """Reschedule a job with a new interval."""
    if job_id not in scheduled_jobs:
        raise ValueError(f"Job {job_id} not found")
    
    job = scheduled_jobs[job_id]
    scheduler.reschedule_job(
        job_id,
        trigger=IntervalTrigger(hours=interval_hours)
    )
    
    logger.info(f"✅ Job {job_id} rescheduled to run every {interval_hours} hours")

def pause_job(job_id: str):
    """Pause a scheduled job."""
    if job_id not in scheduled_jobs:
        raise ValueError(f"Job {job_id} not found")
    
    scheduler.pause_job(job_id)
    logger.info(f"⏸️ Job {job_id} paused")

def resume_job(job_id: str):
    """Resume a paused job."""
    if job_id not in scheduled_jobs:
        raise ValueError(f"Job {job_id} not found")
    
    scheduler.resume_job(job_id)
    logger.info(f"▶️ Job {job_id} resumed")

def run_job_immediately(job_id: str):
    """Run a job immediately outside of its schedule."""
    if job_id not in scheduled_jobs:
        raise ValueError(f"Job {job_id} not found")
    
    job = scheduled_jobs[job_id]
    # Create a new coroutine to run the job function
    asyncio.create_task(job.func())
    logger.info(f"🚀 Job {job_id} triggered to run immediately")

# Initialize scheduler on module import
schedule_auto_jobs()

# Export scheduler instance
__all__ = ['scheduler', 'get_scheduled_jobs', 'reschedule_job', 
           'pause_job', 'resume_job', 'run_job_immediately']
