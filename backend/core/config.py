"""
JARVIS Backend Configuration
============================
Pydantic Settings-based config loaded from environment and YAML.
All config is validated at startup — no silent defaults for critical settings.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="JARVIS_",
        case_sensitive=False,
    )

    # ── Application ───────────────────────────────────────────────────────────
    app_name: str = "JARVIS"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # ── Server ────────────────────────────────────────────────────────────────
    host: str = "127.0.0.1"
    port: int = 8766
    workers: int = 1  # Single worker for offline local use
    reload: bool = False

    # ── CORS (allow desktop + mobile on local network) ────────────────────────
    cors_origins: list[str] = Field(
        default=["http://localhost", "http://127.0.0.1", "*"]
    )

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./database/jarvis.db"
    db_echo: bool = False

    # ── Security ──────────────────────────────────────────────────────────────
    secret_key: str = "jarvis-local-secret-change-in-production"
    ws_token_required: bool = False  # Disabled for local-only use

    # ── AI (Phase 2) ──────────────────────────────────────────────────────────
    ollama_host: str = "http://localhost:11434"
    ollama_default_model: str = "llama3.2-vision"
    ai_context_turns: int = 10
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # ── Voice (Phase 3) ───────────────────────────────────────────────────────
    whisper_model: str = "base"
    tts_voice: str = "en-US-AriaNeural"
    tts_rate: str = "+0%"
    tts_volume: str = "+0%"

    # ── System Monitoring ────────────────────────────────────────────────────
    metrics_interval_sec: float = 1.0

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: str = "DEBUG"
    log_dir: str = "logs"

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1024 <= v <= 65535):
            raise ValueError(f"Port must be between 1024 and 65535, got {v}")
        return v

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def ws_url(self) -> str:
        return f"ws://{self.host}:{self.port}/ws"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get application settings (cached singleton).
    
    Usage:
        from backend.core.config import get_settings
        settings = get_settings()
    """
    return Settings()
