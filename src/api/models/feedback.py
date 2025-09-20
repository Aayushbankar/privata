from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class FeedbackType(str, Enum):
    RESPONSE_RATING = "response_rating"
    NAVIGATION_RATING = "navigation_rating"
    GENERAL_FEEDBACK = "general_feedback"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"

class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for the chat")
    message_id: Optional[str] = Field(None, description="ID of the specific message being rated")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1-5 stars")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment")
    user_query: Optional[str] = Field(None, description="Original user query")
    bot_response: Optional[str] = Field(None, description="Bot response being rated")
    language: Optional[str] = Field("en", description="Language of the interaction")
    
class FeedbackResponse(BaseModel):
    feedback_id: str = Field(..., description="Unique feedback ID")
    message: str = Field(..., description="Success message")
    
class FeedbackAnalytics(BaseModel):
    total_feedback: int = Field(..., description="Total number of feedback entries")
    average_rating: float = Field(..., description="Average rating across all feedback")
    rating_distribution: dict = Field(..., description="Distribution of ratings 1-5")
    feedback_by_type: dict = Field(..., description="Count of feedback by type")
    recent_feedback: List[dict] = Field(..., description="Recent feedback entries")
    common_issues: List[str] = Field(..., description="Common issues mentioned in comments")
    
class FeedbackFilter(BaseModel):
    feedback_type: Optional[FeedbackType] = None
    rating_min: Optional[int] = Field(None, ge=1, le=5)
    rating_max: Optional[int] = Field(None, ge=1, le=5)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    language: Optional[str] = None
    limit: Optional[int] = Field(50, ge=1, le=1000)
    offset: Optional[int] = Field(0, ge=0)
