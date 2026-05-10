"""
JARVIS Backend API Routes — System Endpoints
============================================
REST endpoints for system status, health check, and live metrics.
"""

from __future__ import annotations

import time
from datetime import datetime

from fastapi import APIRouter
from loguru import logger

from backend.services.system_service import SystemService
from shared.schemas import APIResponse, HealthResponse, SystemMetrics
from shared.constants import APP_VERSION

router = APIRouter(prefix="/system", tags=["system"])

_system_service: SystemService | None = None
_start_time = time.time()


def set_services(sys_svc: SystemService) -> None:
    global _system_service
    _system_service = sys_svc


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint — used by clients to verify backend is alive."""
    uptime = time.time() - _start_time
    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        uptime_seconds=round(uptime, 1),
        backend_ready=True,
        ai_ready=False,   # Phase 2
        voice_ready=False, # Phase 3
    )


@router.get("/metrics", response_model=APIResponse)
async def get_metrics():
    """Get latest system metrics snapshot."""
    if _system_service:
        metrics = _system_service.get_latest_metrics()
        if metrics:
            return APIResponse(success=True, data=metrics.model_dump())
    return APIResponse(success=False, error="Metrics not yet available")


@router.get("/info", response_model=APIResponse)
async def get_system_info():
    """Get static system information."""
    import platform
    import psutil

    info = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "cpu_cores_physical": psutil.cpu_count(logical=False),
        "cpu_cores_logical": psutil.cpu_count(logical=True),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
    }
    return APIResponse(success=True, data=info)
