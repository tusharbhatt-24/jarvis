"""
JARVIS System Monitoring Service
=================================
Async background service that polls CPU, RAM, GPU, Disk metrics
and broadcasts them over WebSocket to all subscribed clients.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Optional

import psutil
from loguru import logger

from shared.constants import WS_CHANNEL_SYSTEM, WSEventType, METRICS_BROADCAST_INTERVAL_SEC
from shared.schemas import SystemMetrics

# Optional GPU support
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    logger.warning("[SystemService] GPUtil not available — GPU metrics disabled")

_START_TIME = time.time()


def _collect_metrics() -> SystemMetrics:
    """
    Collect system metrics synchronously.
    Called in a thread pool executor to avoid blocking the event loop.
    """
    # CPU
    cpu_percent = psutil.cpu_percent(interval=None)

    # RAM
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    ram_used_gb = ram.used / (1024 ** 3)
    ram_total_gb = ram.total / (1024 ** 3)

    # Disk
    disk = psutil.disk_usage("/")
    disk_percent = disk.percent
    disk_used_gb = disk.used / (1024 ** 3)
    disk_total_gb = disk.total / (1024 ** 3)

    # CPU Temperature (platform-dependent)
    cpu_temp: Optional[float] = None
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for key in ("coretemp", "cpu_thermal", "acpitz"):
                if key in temps:
                    cpu_temp = temps[key][0].current
                    break
    except (AttributeError, NotImplementedError):
        pass

    # GPU (optional)
    gpu_percent: Optional[float] = None
    gpu_vram_used: Optional[float] = None
    gpu_vram_total: Optional[float] = None
    if GPU_AVAILABLE:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                g = gpus[0]
                gpu_percent = g.load * 100
                gpu_vram_used = g.memoryUsed / 1024
                gpu_vram_total = g.memoryTotal / 1024
        except Exception:
            pass

    uptime = time.time() - _START_TIME

    return SystemMetrics(
        cpu_percent=cpu_percent,
        ram_percent=ram_percent,
        ram_used_gb=round(ram_used_gb, 2),
        ram_total_gb=round(ram_total_gb, 2),
        gpu_percent=gpu_percent,
        gpu_vram_used_gb=round(gpu_vram_used, 2) if gpu_vram_used else None,
        gpu_vram_total_gb=round(gpu_vram_total, 2) if gpu_vram_total else None,
        disk_percent=disk_percent,
        disk_used_gb=round(disk_used_gb, 2),
        disk_total_gb=round(disk_total_gb, 2),
        cpu_temp_celsius=round(cpu_temp, 1) if cpu_temp else None,
        uptime_seconds=round(uptime, 1),
    )


class SystemService:
    """
    Background asyncio service for system monitoring.
    
    Usage:
        service = SystemService(ws_hub)
        asyncio.create_task(service.start())
    """

    def __init__(self, ws_hub):
        self._hub = ws_hub
        self._running = False
        self._latest_metrics: Optional[SystemMetrics] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def start(self) -> None:
        """Start the monitoring loop."""
        self._running = True
        self._loop = asyncio.get_running_loop()
        logger.info("[SystemService] Monitoring started")

        # Pre-warm CPU percent (first call returns 0.0)
        psutil.cpu_percent(interval=None)

        while self._running:
            try:
                # Run blocking metric collection in thread pool
                metrics = await self._loop.run_in_executor(None, _collect_metrics)
                self._latest_metrics = metrics

                # Broadcast to all system channel subscribers
                await self._hub.broadcast(WS_CHANNEL_SYSTEM, {
                    "type": WSEventType.SYSTEM_METRICS,
                    "channel": WS_CHANNEL_SYSTEM,
                    "payload": metrics.model_dump(),
                    "timestamp": datetime.utcnow().isoformat(),
                })

            except Exception as e:
                logger.error(f"[SystemService] Error collecting metrics: {e}")

            await asyncio.sleep(METRICS_BROADCAST_INTERVAL_SEC)

    async def stop(self) -> None:
        """Gracefully stop the monitoring loop."""
        self._running = False
        logger.info("[SystemService] Monitoring stopped")

    def get_latest_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recently collected metrics (synchronous)."""
        return self._latest_metrics
