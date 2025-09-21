"""
FastAPI main application for MOSDAC AI Help Bot API.

This module serves as the entry point for the FastAPI application,
providing REST API endpoints for chat, data, status, admin, navigation, feedback and system monitoring.
"""

import os
import sys
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import existing components
from src.core.mosdac_bot import MOSDACBot
from src.scrapers.comprehensive_mosdac_scraper import ComprehensiveMOSDACScraper
from src.ingestion.ingest import ModernIngestionPipeline
from src.models.llm_loader import get_llm_info

# Import API routers
from src.api.routes.chat import router as chat_router
from src.api.routes.data import router as data_router
from src.api.routes.status import router as status_router
from src.api.routes.admin import router as admin_router
from src.api.routes.navigation import router as navigation_router
from src.api.routes.feedback import router as feedback_router

# Import background scheduler
from src.api.background.scheduler import scheduler

# Import configuration system
from src.api.config import get_config, update_config

# Create FastAPI application
app = FastAPI(
    title="MOSDAC AI Help Bot API",
    description="REST API for MOSDAC AI Help Bot with auto-scraping capabilities",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for development
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "file://",  # Allow file:// protocol for development
        "http://0.0.0.0:3000",  # Allow requests from 0.0.0.0
        "http://localhost:8001",  # Allow additional ports
        "http://127.0.0.1:8001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(data_router, prefix="/api/v1", tags=["data"])
app.include_router(status_router, prefix="/api/v1", tags=["status"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(navigation_router, prefix="/api/v1", tags=["navigation"])
app.include_router(feedback_router, prefix="/api/v1", tags=["feedback"])

# Import dependencies
from src.api.dependencies import get_bot, get_scraper, get_ingestor

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("🚀 Starting MOSDAC AI Help Bot API...")
    
    # Initialize components
    get_bot()
    get_scraper()
    get_ingestor()
    
    # Start background scheduler
    scheduler.start()
    print("✅ Background scheduler started")
    
    print("✅ API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup application on shutdown."""
    print("🛑 Shutting down MOSDAC AI Help Bot API...")
    
    # Stop background scheduler
    scheduler.shutdown()
    print("✅ Background scheduler stopped")
    
    print("✅ API shutdown complete")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "MOSDAC AI Help Bot API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "chat": "/api/v1/chat",
            "status": "/api/v1/status",
            "data": "/api/v1/data",
            "admin": "/api/v1/admin",
            "navigation": "/api/v1/navigation",
            "docs": "/api/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if core components are available
        bot = get_bot()
        llm_info = get_llm_info()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "bot": True,
                "llm": llm_info["available"],
                "scraper": True,
                "ingestor": True,
                "scheduler": scheduler.running
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for consistent error responses."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
