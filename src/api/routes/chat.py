"""
Chat API router for MOSDAC AI Help Bot.

This module provides REST API endpoints for chat functionality.
"""

import os
import sys
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import re
import traceback
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
def _sanitize_response_text(text: str) -> str:
    """Remove chunk index and noisy debug info from AI response before sending to frontend.

    - Remove patterns like "Chunk 3/8" (optionally preceded by comma/space)
    - Remove relevance annotations like "(Relevance: 0.532)"
    - Remove inline citations like "[Source: ...]" with local file paths
    - Strip any inline http/https URLs from the body (we append links separately)
    - Collapse excessive spaces
    - Remove file path references
    """
    try:
        cleaned = text
        # Remove ", Chunk d+/d+" or "Chunk d+/d+"
        cleaned = re.sub(r"\s*,?\s*Chunk\s+\d+/\d+", "", cleaned, flags=re.IGNORECASE)
        # Remove "(Relevance: 0.xxx)"
        cleaned = re.sub(r"\(\s*Relevance:\s*[^)]+\)", "", cleaned, flags=re.IGNORECASE)
        # Remove inline [Source: ...] citations completely
        cleaned = re.sub(r"\[\s*Source\s*:[^\]]*\]", "", cleaned, flags=re.IGNORECASE)
        # Remove "Source:" followed by file paths
        cleaned = re.sub(r"Source:\s*[^\n;]+;?\s*", "", cleaned, flags=re.IGNORECASE)
        # Remove file path patterns like "/home/kai/..."
        cleaned = re.sub(r"/[^\s;]+\.md[;\s]*", "", cleaned)
        # Remove inline raw URLs (http/https)
        cleaned = re.sub(r"https?://\S+", "", cleaned)
        # Remove Markdown-style links [text](url) -> text
        cleaned = re.sub(r"\[([^\]]+)\]\(https?://[^)]+\)", r"\1", cleaned)
        # Remove excessive semicolons and clean up punctuation
        cleaned = re.sub(r";\s*;+", ";", cleaned)
        cleaned = re.sub(r";\s*$", "", cleaned, flags=re.MULTILINE)
        # Remove stray multiple spaces and clean up formatting
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        cleaned = re.sub(r"\n\s*\n\s*\n", "\n\n", cleaned)
        return cleaned.strip()
    except Exception:
        return text

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
        
        # Get response from bot with language parameter
        response_text, sources = bot.get_response(request.query, request.session_id, language=request.language)
        response_text = _sanitize_response_text(response_text)
        
        # Add to session history
        sessions[request.session_id]["messages"].append({
            "query": request.query,
            "response": response_text,
            "timestamp": datetime.now(),
            "sources": [{"url": s["url"], "title": s["title"]} for s in sources]
        })
        
        # Clamp relevance to [0,1]
        safe_sources = []
        for s in sources:
            rel = s.get("relevance", 0.8)
            try:
                rel = max(0.0, min(1.0, float(rel)))
            except Exception:
                rel = 0.0
            safe_sources.append({"url": s["url"], "title": s["title"], "relevance": rel})

        # Build clean related links section
        related_lines = []
        for s in safe_sources[:3]:  # Limit to 3 most relevant sources
            url = s.get("url", "")
            title = s.get("title", "")
            
            # Only include if it's a valid HTTP URL and has a meaningful title
            if isinstance(url, str) and url.startswith("http") and title and title != url:
                # Clean up the title to remove file paths
                clean_title = title.replace("/home/kai/aayush/Projects/privata/data/scraped/mosdac_complete_data/", "")
                clean_title = clean_title.replace("/content.md", "").replace("-", " ").title()
                related_lines.append(f"📄 {clean_title}")
        
        related_block = ("\n\n**Related Resources:**\n" + "\n".join(related_lines)) if related_lines else ""

        return ChatResponse(
            response=(response_text.strip() + related_block),
            sources=safe_sources,
            metadata={
                "session_id": request.session_id,
                "message_count": len(sessions[request.session_id]["messages"]),
                "response_time_ms": 0  # TODO: Add timing
            }
        )
        
    except Exception as e:
        # Log full traceback for debugging
        tb = traceback.format_exc()
        try:
            with open("/tmp/api_errors.log", "a") as f:
                f.write(f"\n[CHAT_ERROR] {datetime.now().isoformat()}\n{tb}\n")
        except Exception:
            pass
        # Graceful fallback response instead of 500
        fallback = (
            "I had trouble generating a complete answer just now. "
            "Please try rephrasing your question, or ask something more specific about MOSDAC data, satellites, or tools."
        )
        return ChatResponse(
            response=fallback,
            sources=[],
            metadata={
                "session_id": request.session_id,
                "message_count": len(sessions.get(request.session_id, {}).get("messages", [])),
                "error": str(e)
            }
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
