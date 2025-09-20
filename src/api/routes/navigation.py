"""
FastAPI routes for Navigation Assistant functionality.
Provides high-performance endpoints for navigation guidance.
"""

import sys
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# Add navigation module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.navigation.navigation_assistant import navigation_assistant

router = APIRouter()

class NavigationRequest(BaseModel):
    """Request model for navigation guidance"""
    query: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class NavigationResponse(BaseModel):
    """Response model for navigation guidance"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

@router.post("/navigation/guide")
async def get_navigation_guidance(request: NavigationRequest) -> NavigationResponse:
    """
    Get step-by-step navigation guidance for MOSDAC portal.
    
    Fast endpoint optimized for minimal latency.
    """
    try:
        import time
        start_time = time.time()
        
        # Get navigation guidance
        guidance = navigation_assistant.get_navigation_guidance(request.query)
        
        processing_time = time.time() - start_time
        
        return NavigationResponse(
            success=True,
            data=guidance,
            processing_time=processing_time
        )
        
    except Exception as e:
        return NavigationResponse(
            success=False,
            error=f"Navigation guidance failed: {str(e)}"
        )

@router.get("/navigation/intent")
async def detect_intent(query: str = Query(..., description="User query to analyze")) -> NavigationResponse:
    """
    Fast intent detection endpoint.
    
    Lightweight endpoint for real-time intent detection.
    """
    try:
        import time
        start_time = time.time()
        
        intent, confidence = navigation_assistant.detect_navigation_intent(query)
        
        processing_time = time.time() - start_time
        
        return NavigationResponse(
            success=True,
            data={
                "query": query,
                "intent": intent,
                "confidence": confidence
            },
            processing_time=processing_time
        )
        
    except Exception as e:
        return NavigationResponse(
            success=False,
            error=f"Intent detection failed: {str(e)}"
        )

@router.get("/navigation/structure")
async def get_site_structure() -> NavigationResponse:
    """
    Get MOSDAC site structure for navigation.
    
    Cached endpoint for site structure information.
    """
    try:
        import time
        start_time = time.time()
        
        structure = navigation_assistant._load_mosdac_structure()
        
        processing_time = time.time() - start_time
        
        return NavigationResponse(
            success=True,
            data={
                "site_structure": structure,
                "total_sections": len(structure),
                "available_intents": list(navigation_assistant.intent_patterns.keys())
            },
            processing_time=processing_time
        )
        
    except Exception as e:
        return NavigationResponse(
            success=False,
            error=f"Site structure retrieval failed: {str(e)}"
        )

@router.post("/navigation/path")
async def get_navigation_path(request: NavigationRequest) -> NavigationResponse:
    """
    Get optimized navigation path without full guidance.
    
    Lightweight endpoint for just the navigation path.
    """
    try:
        import time
        start_time = time.time()
        
        intent, confidence = navigation_assistant.detect_navigation_intent(request.query)
        path = navigation_assistant.generate_navigation_path(intent, request.query)
        
        processing_time = time.time() - start_time
        
        return NavigationResponse(
            success=True,
            data={
                "query": request.query,
                "intent": intent,
                "confidence": confidence,
                "path": {
                    "goal": path.goal,
                    "total_steps": len(path.steps),
                    "estimated_time": path.total_time,
                    "difficulty": path.difficulty,
                    "success_rate": path.success_rate
                }
            },
            processing_time=processing_time
        )
        
    except Exception as e:
        return NavigationResponse(
            success=False,
            error=f"Navigation path generation failed: {str(e)}"
        )

@router.get("/navigation/health")
async def navigation_health_check() -> NavigationResponse:
    """
    Health check endpoint for navigation service.
    """
    try:
        # Quick test of navigation assistant
        test_intent, test_confidence = navigation_assistant.detect_navigation_intent("download data")
        
        return NavigationResponse(
            success=True,
            data={
                "status": "healthy",
                "cache_size": len(navigation_assistant.navigation_cache),
                "test_intent": test_intent,
                "test_confidence": test_confidence
            }
        )
        
    except Exception as e:
        return NavigationResponse(
            success=False,
            error=f"Navigation health check failed: {str(e)}"
        )
