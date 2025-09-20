from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
import logging

from ..models.feedback import (
    FeedbackRequest, FeedbackResponse, FeedbackAnalytics, 
    FeedbackFilter, FeedbackType
)
from ...feedback.feedback_manager import FeedbackManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])

# Initialize feedback manager
feedback_manager = FeedbackManager()

@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest):
    """Submit user feedback for chat responses or navigation assistance"""
    try:
        feedback_id = feedback_manager.add_feedback(
            session_id=feedback.session_id,
            message_id=feedback.message_id,
            feedback_type=feedback.feedback_type.value,
            rating=feedback.rating,
            comment=feedback.comment,
            user_query=feedback.user_query,
            bot_response=feedback.bot_response,
            language=feedback.language or "en"
        )
        
        logger.info(f"Feedback submitted: {feedback_id} for session {feedback.session_id}")
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            message="Feedback submitted successfully. Thank you for helping us improve!"
        )
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

@router.get("/analytics", response_model=FeedbackAnalytics)
async def get_feedback_analytics():
    """Get comprehensive feedback analytics and insights"""
    try:
        analytics = feedback_manager.get_feedback_analytics()
        return FeedbackAnalytics(**analytics)
        
    except Exception as e:
        logger.error(f"Error getting feedback analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@router.get("/list")
async def get_feedback_list(
    feedback_type: Optional[FeedbackType] = None,
    rating_min: Optional[int] = None,
    rating_max: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    language: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get filtered list of feedback entries"""
    try:
        feedback_list = feedback_manager.get_filtered_feedback(
            feedback_type=feedback_type.value if feedback_type else None,
            rating_min=rating_min,
            rating_max=rating_max,
            date_from=date_from,
            date_to=date_to,
            language=language,
            limit=limit,
            offset=offset
        )
        
        return {
            "feedback": feedback_list,
            "count": len(feedback_list),
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting feedback list: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve feedback")

@router.get("/session/{session_id}")
async def get_session_feedback(session_id: str):
    """Get all feedback for a specific chat session"""
    try:
        session_feedback = feedback_manager.get_session_feedback(session_id)
        
        return {
            "session_id": session_id,
            "feedback": session_feedback,
            "count": len(session_feedback)
        }
        
    except Exception as e:
        logger.error(f"Error getting session feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session feedback")

@router.get("/trends")
async def get_feedback_trends(days: int = 30):
    """Get feedback trends over the specified number of days"""
    try:
        if days < 1 or days > 365:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
            
        trends = feedback_manager.get_feedback_trends(days)
        
        return {
            "trends": trends,
            "period": f"Last {days} days"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feedback trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trends")

@router.get("/health")
async def feedback_health_check():
    """Health check endpoint for feedback system"""
    try:
        # Test database connection
        analytics = feedback_manager.get_feedback_analytics()
        
        return {
            "status": "healthy",
            "message": "Feedback system is operational",
            "total_feedback": analytics.get("total_feedback", 0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Feedback system health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Feedback system unavailable")
