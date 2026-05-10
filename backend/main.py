"""
JARVIS FastAPI Backend — Main Entry Point
==========================================
Configures and launches the FastAPI application with:
- CORS middleware
- Router registration
- Application lifecycle (startup/shutdown)
- WebSocket hub integration
- Background service management
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.core.config import get_settings
from backend.database.models import init_database, close_database
from backend.websocket.hub import ws_hub
from backend.services.system_service import SystemService
from backend.services.ai_service import AIService
from backend.services.voice_service import VoiceService
from backend.api.routes import ws as ws_router
from backend.api.routes import system as system_router
from backend.api.routes import ai as ai_router
from shared.constants import APP_NAME, APP_VERSION, API_PREFIX

# ── Services (initialized on startup) ────────────────────────────────────────
_system_service: SystemService | None = None
_ai_service: AIService | None = None
_bg_tasks: list[asyncio.Task] = []


# ── Application Lifecycle ─────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown of all services."""
    global _system_service, _ai_service, _voice_service

    settings = get_settings()
    logger.info(f"{'='*60}")
    logger.info(f"  {APP_NAME} v{APP_VERSION} — Backend Starting")
    logger.info(f"  Host: {settings.host}:{settings.port}")
    logger.info(f"{'='*60}")

    # ── Initialize database ───────────────────────────────────────────────────
    await init_database()

    # ── Initialize services ───────────────────────────────────────────────────
    _ai_service = AIService(ws_hub)
    await _ai_service.initialize()

    _voice_service = VoiceService(ws_hub)
    voice_task = asyncio.create_task(_voice_service.initialize())
    _bg_tasks.append(voice_task)

    _system_service = SystemService(ws_hub)

    # ── Inject service dependencies into routers ──────────────────────────────
    ws_router.set_services(_ai_service, _voice_service)
    system_router.set_services(_system_service)
    ai_router.set_services(_ai_service)

    # ── Start background monitoring ───────────────────────────────────────────
    monitor_task = asyncio.create_task(_system_service.start())
    _bg_tasks.append(monitor_task)

    logger.success(f"✓ {APP_NAME} backend ready on {settings.base_url}")

    yield  # ←  App is running

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down JARVIS backend...")

    await _system_service.stop()
    for task in _bg_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    await _ai_service.close()
    await close_database()
    logger.info("Backend shutdown complete.")


# ── FastAPI Application ───────────────────────────────────────────────────────

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=f"{APP_NAME} API",
        description="JARVIS Offline AI Assistant — Local Backend API",
        version=APP_VERSION,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(ws_router.router)
    app.include_router(system_router.router, prefix=API_PREFIX)
    app.include_router(ai_router.router, prefix=API_PREFIX)

    # ── Root endpoint ─────────────────────────────────────────────────────────
    @app.get("/")
    async def root():
        return {
            "name": APP_NAME,
            "version": APP_VERSION,
            "status": "online",
            "docs": f"{settings.base_url}/docs" if settings.debug else "disabled",
            "websocket": settings.ws_url,
        }

    return app


app = create_app()


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.logger import setup_logger
    setup_logger("backend")

    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info",
        access_log=True,
    )
