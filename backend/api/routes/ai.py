"""
JARVIS Backend API Routes — AI Endpoints
=========================================
REST endpoints for AI conversations, session management.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from loguru import logger

from shared.schemas import APIResponse, AIQueryPayload
from shared.constants import APP_VERSION

router = APIRouter(prefix="/ai", tags=["ai"])

_ai_service = None


def set_services(ai_svc) -> None:
    global _ai_service
    _ai_service = ai_svc


@router.get("/status", response_model=APIResponse)
async def ai_status():
    """Get AI engine status."""
    return APIResponse(success=True, data={
        "ready": _ai_service.is_ready() if _ai_service else False,
        "phase": "foundation",
        "engine": "ollama (not connected yet)",
        "note": "Phase 2 will enable full Ollama inference",
    })


@router.delete("/session/{session_id}", response_model=APIResponse)
async def clear_session(session_id: str):
    """Clear a conversation session from memory."""
    if _ai_service:
        _ai_service.clear_session(session_id)
        return APIResponse(success=True, data={"cleared": session_id})
    raise HTTPException(status_code=503, detail="AI service not available")


@router.get("/session/{session_id}/history", response_model=APIResponse)
async def get_session_history(session_id: str):
    """Get conversation history for a session."""
    if _ai_service:
        history = _ai_service.get_session_history(session_id)
        return APIResponse(success=True, data={"turns": history, "count": len(history)})
    raise HTTPException(status_code=503, detail="AI service not available")
