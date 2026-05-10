"""
JARVIS Shared Pydantic Schemas
==============================
Data contracts used by both backend and desktop for WebSocket
message serialization/deserialization.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
import uuid


# ── Base Message ──────────────────────────────────────────────────────────────

class WSMessage(BaseModel):
    """Base WebSocket message envelope."""
    type: str
    channel: str
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    client_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: Optional[str] = None

    def model_dump_json_bytes(self) -> bytes:
        return self.model_dump_json().encode("utf-8")


# ── AI Schemas ────────────────────────────────────────────────────────────────

class AIQueryPayload(BaseModel):
    text: str
    model: str = "llama3.2"
    session_id: Optional[str] = None
    context_turns: int = 10
    images: Optional[list[str]] = None

class AITokenPayload(BaseModel):
    token: str
    session_id: str
    done: bool = False

class AIQueryMessage(WSMessage):
    type: str = "ai_query"
    channel: str = "ai"
    payload: AIQueryPayload  # type: ignore[assignment]


# ── System Metrics ────────────────────────────────────────────────────────────

class SystemMetrics(BaseModel):
    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    gpu_percent: Optional[float] = None
    gpu_vram_used_gb: Optional[float] = None
    gpu_vram_total_gb: Optional[float] = None
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    cpu_temp_celsius: Optional[float] = None
    uptime_seconds: float


# ── Notification ──────────────────────────────────────────────────────────────

class NotificationPayload(BaseModel):
    title: str
    message: str
    type: str = "info"   # info | success | warning | error | ai
    duration_ms: int = 4000
    icon: Optional[str] = None


# ── Log Entry ─────────────────────────────────────────────────────────────────

class LogEntry(BaseModel):
    level: str
    message: str
    module: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    extra: dict[str, Any] = Field(default_factory=dict)


# ── API Response Wrappers ─────────────────────────────────────────────────────

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    uptime_seconds: float
    backend_ready: bool
    ai_ready: bool
    voice_ready: bool


# ── Database Schemas ──────────────────────────────────────────────────────────

class ConversationTurn(BaseModel):
    id: Optional[int] = None
    session_id: str
    role: str   # "user" | "assistant"
    content: str
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ConversationSession(BaseModel):
    id: Optional[int] = None
    session_id: str
    title: str = "New Conversation"
    model: str = "llama3.2"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ActivityLog(BaseModel):
    id: Optional[int] = None
    event_type: str
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
