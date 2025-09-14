"""
Chat API router for MOSDAC AI Help Bot.

This module provides REST API endpoints for chat functionality.
"""

import os
import sys
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import models and dependencies
from src.api.models.chat import (
    ChatRequest, ChatResponse, ChatError, ChatStreamChunk,
    SessionInfo, SessionListResponse
)
from src.api.dependencies import get_bot
from src.core.mosdac_bot import MOSDACBot

# Create router
router = APIRouter()

# Session storage (in production, use Redis or database)
sessions = {}

@router.post("/chat", response_model=ChatResponse, responses={500: {"model": ChatError}})
async def chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    bot: MOSDACBot = Depends(get_bot)
):
    """
    Send a chat message to the MOSDAC AI Help Bot.
    
    This endpoint processes natural language queries and returns AI-generated responses
    based on the scraped MOSDAC website content.
    """
    try:
        # Initialize session if it doesn't exist
        if request.session_id not in sessions:
            sessions[request.session_id] = {
                "created_at": datetime.now(),
                "messages": [],
                "last_activity": datetime.now()
            }
        
        # Update session activity
        sessions[request.session_id]["last_activity"] = datetime.now()
        
        # Process the query
        if request.stream:
            # For streaming responses, we'll handle differently
            raise HTTPException(status_code=501, detail="Streaming not implemented yet")
        
        # Get response from bot
        response_text, sources = bot.get_response(request.query, request.session_id)
        
        # Add to session history
        sessions[request.session_id]["messages"].append({
            "query": request.query,
            "response": response_text,
            "timestamp": datetime.now(),
            "sources": [{"url": s["url"], "title": s["title"]} for s in sources]
        })
        
        return ChatResponse(
            response=response_text,
            sources=[{"url": s["url"], "title": s["title"], "relevance": s.get("relevance", 0.8)} for s in sources],
            metadata={
                "session_id": request.session_id,
                "message_count": len(sessions[request.session_id]["messages"]),
                "response_time_ms": 0  # TODO: Add timing
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.get("/chat/sessions", response_model=SessionListResponse)
async def list_sessions():
    """
    List all active chat sessions.
    
    Returns information about all currently active chat sessions,
    including creation time and message count.
    """
    session_list = []
    for session_id, session_data in sessions.items():
        session_list.append(SessionInfo(
            session_id=session_id,
            created_at=session_data["created_at"],
            message_count=len(session_data["messages"]),
            last_activity=session_data["last_activity"]
        ))
    
    return SessionListResponse(
        sessions=session_list,
        total_count=len(session_list)
    )


@router.get("/chat/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get detailed information about a specific chat session.
    
    Returns the complete message history for a session.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "created_at": sessions[session_id]["created_at"],
        "last_activity": sessions[session_id]["last_activity"],
        "messages": sessions[session_id]["messages"],
        "message_count": len(sessions[session_id]["messages"])
    }


@router.delete("/chat/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a specific chat session.
    
    Removes all message history for the specified session.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {"message": f"Session {session_id} deleted successfully"}


@router.delete("/chat/sessions")
async def clear_all_sessions():
    """
    Clear all chat sessions.
    
    Removes all session data and message history.
    """
    global sessions
    session_count = len(sessions)
    sessions = {}
    return {"message": f"Cleared {session_count} sessions"}


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, bot: MOSDACBot = Depends(get_bot)):
    """
    Stream chat responses in real-time.
    
    This endpoint streams the AI response chunk by chunk for better UX.
    """
    async def generate():
        try:
            # Initialize session if it doesn't exist
            if request.session_id not in sessions:
                sessions[request.session_id] = {
                    "created_at": datetime.now(),
                    "messages": [],
                    "last_activity": datetime.now()
                }
            
            # Update session activity
            sessions[request.session_id]["last_activity"] = datetime.now()
            
            # For streaming, we need to implement streaming in the bot
            # For now, simulate streaming by chunking the response
            response_text, sources = bot.get_response(request.query, request.session_id)
            
            # Split response into chunks for streaming
            words = response_text.split()
            for i, word in enumerate(words):
                is_final = i == len(words) - 1
                chunk_data = ChatStreamChunk(
                    chunk=word + " ",
                    is_final=is_final,
                    sources=sources if is_final else None
                )
                yield f"data: {chunk_data.model_dump_json()}\n\n"
                
                # Small delay for realistic streaming
                import asyncio
                await asyncio.sleep(0.05)
                
        except Exception as e:
            error_chunk = ChatStreamChunk(
                chunk=f"Error: {str(e)}",
                is_final=True,
                sources=None
            )
            yield f"data: {error_chunk.model_dump_json()}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# Health check endpoint for chat service
@router.get("/chat/health")
async def chat_health(bot: MOSDACBot = Depends(get_bot)):
    """
    Health check for chat functionality.
    
    Verifies that the chat service is operational and can process queries.
    """
    try:
        # Test with a simple query
        test_query = "Hello"
        response, _ = bot.get_response(test_query, "health_check")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "response_time_ms": 0,  # TODO: Add timing
            "test_query": test_query,
            "test_response": response[:50] + "..." if len(response) > 50 else response
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Chat service unhealthy: {str(e)}"
        )
