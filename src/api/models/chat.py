"""
Pydantic models for chat-related API endpoints.

This module defines the request/response schemas for the chat functionality.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Source(BaseModel):
    """Source information for chat responses."""
    url: str = Field(..., description="URL of the source document")
    title: str = Field(..., description="Title of the source document")
    relevance: float = Field(..., description="Relevance score (0.0 to 1.0)", ge=0.0, le=1.0)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., description="Natural language query", min_length=1, max_length=1000)
    session_id: Optional[str] = Field("default", description="Session ID for context retention")
    language: Optional[str] = Field("en", description="Language code for response (e.g., 'en', 'hi', 'ta')")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="AI-generated response")
    sources: List[Source] = Field(..., description="List of sources used for the response")
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {},
        description="Additional metadata about the response"
    )


class ChatError(BaseModel):
    """Error response model for chat endpoint."""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ChatStreamChunk(BaseModel):
    """Streaming response chunk for chat endpoint."""
    chunk: str = Field(..., description="Text chunk")
    is_final: bool = Field(False, description="Whether this is the final chunk")
    sources: Optional[List[Source]] = Field(None, description="Sources (only in final chunk)")


class SessionInfo(BaseModel):
    """Information about a chat session."""
    session_id: str = Field(..., description="Session ID")
    created_at: datetime = Field(..., description="Session creation timestamp")
    message_count: int = Field(..., description="Number of messages in session")
    last_activity: datetime = Field(..., description="Last activity timestamp")


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""
    sessions: List[SessionInfo] = Field(..., description="List of active sessions")
    total_count: int = Field(..., description="Total number of sessions")
