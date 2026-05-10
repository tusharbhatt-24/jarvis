"""
JARVIS Desktop — WebSocket Worker Thread
=========================================
Runs the WebSocket client in a dedicated QThread.
Emits Qt signals to safely update the main UI thread.
Never touches UI directly from this thread.
"""

from __future__ import annotations

import asyncio
import json
import threading
from datetime import datetime
from typing import Optional

from PySide6.QtCore import QThread, Signal, QObject
from loguru import logger

from shared.constants import BACKEND_WS_URL, WSEventType, WS_CHANNEL_SYSTEM, WS_CHANNEL_AI, WS_CHANNEL_LOGS
from shared.schemas import SystemMetrics


class WSWorkerSignals(QObject):
    """Signal container (must be QObject for signal support)."""
    connected = Signal()
    disconnected = Signal()
    system_metrics = Signal(dict)
    ai_token = Signal(str, str)     # token, session_id
    ai_done = Signal(str, int)      # session_id, token_count
    ai_error = Signal(str)
    log_entry = Signal(dict)
    notification = Signal(dict)
    error = Signal(str)
    raw_message = Signal(dict)


class WSWorker(QThread):
    """
    Manages the WebSocket connection to the JARVIS backend.
    
    Architecture:
    - Runs its own asyncio event loop in a dedicated QThread
    - Reconnects automatically on connection failure
    - Sends all signals to main thread via Qt signal/slot
    - Heartbeat every 30 seconds to keep connection alive
    """

    def __init__(self, ws_url: str = BACKEND_WS_URL, parent=None):
        super().__init__(parent)
        self.ws_url = ws_url
        self.signals = WSWorkerSignals()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._ws = None
        self._running = False
        self._reconnect_interval = 3.0
        self._max_reconnect_interval = 30.0
        self._send_queue: asyncio.Queue = None

    def run(self) -> None:
        """QThread entry point — creates and runs the asyncio loop."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._running = True
        try:
            self._loop.run_until_complete(self._connection_loop())
        finally:
            self._loop.close()
            logger.debug("[WSWorker] Event loop closed")

    async def _connection_loop(self) -> None:
        """Reconnection loop with exponential backoff."""
        import websockets

        interval = self._reconnect_interval

        while self._running:
            try:
                logger.info(f"[WSWorker] Connecting to {self.ws_url}")
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=30,
                    ping_timeout=10,
                    close_timeout=5,
                ) as ws:
                    self._ws = ws
                    self._send_queue = asyncio.Queue()
                    interval = self._reconnect_interval  # Reset on success
                    self.signals.connected.emit()
                    logger.success("[WSWorker] Connected to backend")

                    # Subscribe to channels
                    for channel in (WS_CHANNEL_SYSTEM, WS_CHANNEL_AI, WS_CHANNEL_LOGS):
                        await self._send_raw({"type": "subscribe", "channel": channel, "payload": {}})

                    # Run receiver and sender concurrently
                    await asyncio.gather(
                        self._receive_loop(ws),
                        self._send_loop(ws),
                        self._heartbeat_loop(ws),
                    )

            except Exception as e:
                logger.warning(f"[WSWorker] Connection error: {e}")
                self.signals.disconnected.emit()

                if self._running:
                    logger.info(f"[WSWorker] Reconnecting in {interval:.1f}s...")
                    await asyncio.sleep(interval)
                    interval = min(interval * 1.5, self._max_reconnect_interval)

    async def _receive_loop(self, ws) -> None:
        """Receive and route incoming messages."""
        async for raw in ws:
            if not self._running:
                break
            try:
                msg = json.loads(raw)
                self.signals.raw_message.emit(msg)
                await self._route_message(msg)
            except json.JSONDecodeError:
                logger.warning(f"[WSWorker] Invalid JSON received")
            except Exception as e:
                logger.error(f"[WSWorker] Error routing message: {e}")

    async def _route_message(self, msg: dict) -> None:
        """Route message to the appropriate signal."""
        msg_type = msg.get("type", "")
        payload = msg.get("payload", {})

        if msg_type == WSEventType.SYSTEM_METRICS:
            self.signals.system_metrics.emit(payload)

        elif msg_type == WSEventType.AI_TOKEN:
            token = payload.get("token", "")
            session_id = payload.get("session_id", "")
            self.signals.ai_token.emit(token, session_id)

        elif msg_type == WSEventType.AI_DONE:
            session_id = payload.get("session_id", "")
            count = payload.get("tokens_generated", 0)
            self.signals.ai_done.emit(session_id, count)

        elif msg_type == WSEventType.AI_ERROR:
            self.signals.ai_error.emit(payload.get("error", "Unknown AI error"))

        elif msg_type == WSEventType.LOG_ENTRY:
            self.signals.log_entry.emit(payload)

        elif msg_type == WSEventType.NOTIFICATION:
            self.signals.notification.emit(payload)

    async def _send_loop(self, ws) -> None:
        """Drain the send queue and send messages to backend."""
        while self._running:
            try:
                msg = await asyncio.wait_for(self._send_queue.get(), timeout=1.0)
                await ws.send(json.dumps(msg, default=str))
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"[WSWorker] Send error: {e}")
                break

    async def _heartbeat_loop(self, ws) -> None:
        """Send periodic heartbeat to keep connection alive."""
        while self._running:
            await asyncio.sleep(30)
            try:
                await ws.send(json.dumps({
                    "type": WSEventType.HEARTBEAT,
                    "channel": "system",
                    "payload": {},
                    "timestamp": datetime.utcnow().isoformat(),
                }))
            except Exception:
                break

    async def _send_raw(self, msg: dict) -> None:
        """Queue a message for sending (async-safe)."""
        if self._send_queue:
            await self._send_queue.put(msg)

    def send_message(self, msg: dict) -> None:
        """
        Thread-safe method to queue a message from the main thread.
        Call this from Qt main thread — it schedules on the worker loop.
        """
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send_raw(msg), self._loop)

    def stop(self) -> None:
        """Gracefully stop the worker thread."""
        self._running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        self.wait(3000)
