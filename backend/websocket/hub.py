"""
JARVIS WebSocket Hub
====================
Manages all active WebSocket connections.
Supports per-channel broadcasting, unicast, and client subscriptions.
Thread-safe via asyncio primitives.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Optional

from fastapi import WebSocket
from loguru import logger

from shared.constants import WS_CHANNELS, WSEventType
from shared.schemas import WSMessage


class WSClient:
    """Represents a single connected WebSocket client."""

    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.subscriptions: set[str] = set()
        self.connected_at = datetime.utcnow()
        self.last_heartbeat = datetime.utcnow()
        self._send_lock = asyncio.Lock()

    async def send_message(self, message: WSMessage | dict) -> bool:
        """
        Send a message to this client. Returns False if disconnected.
        Uses a per-client lock to prevent concurrent write corruption.
        """
        async with self._send_lock:
            try:
                if isinstance(message, WSMessage):
                    data = message.model_dump_json()
                else:
                    data = json.dumps(message, default=str)
                await self.websocket.send_text(data)
                return True
            except Exception as e:
                logger.warning(f"Failed to send to client {self.client_id}: {e}")
                return False

    async def send_raw(self, data: bytes) -> bool:
        """Send binary data (e.g., audio chunks)."""
        async with self._send_lock:
            try:
                await self.websocket.send_bytes(data)
                return True
            except Exception:
                return False

    def subscribe(self, channel: str) -> None:
        if channel in WS_CHANNELS:
            self.subscriptions.add(channel)

    def unsubscribe(self, channel: str) -> None:
        self.subscriptions.discard(channel)

    def is_subscribed(self, channel: str) -> bool:
        return channel in self.subscriptions


class WSHub:
    """
    Central WebSocket connection manager.
    
    Responsibilities:
    - Track all active connections
    - Channel-based pub/sub broadcasting
    - Unicast messaging
    - Heartbeat tracking
    - Graceful disconnection handling
    """

    def __init__(self):
        self._clients: dict[str, WSClient] = {}
        self._channel_index: dict[str, set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> WSClient:
        """Accept a new WebSocket connection and register it."""
        await websocket.accept()
        client_id = client_id or str(uuid.uuid4())
        client = WSClient(websocket, client_id)

        async with self._lock:
            self._clients[client_id] = client

        logger.info(f"[WSHub] Client connected: {client_id} | Total: {len(self._clients)}")

        # Send welcome message
        await client.send_message({
            "type": WSEventType.CONNECTED,
            "channel": "system",
            "payload": {
                "client_id": client_id,
                "server_time": datetime.utcnow().isoformat(),
                "available_channels": list(WS_CHANNELS),
            },
            "timestamp": datetime.utcnow().isoformat(),
        })

        return client

    async def disconnect(self, client_id: str) -> None:
        """Remove a client from all channels and the hub."""
        async with self._lock:
            client = self._clients.pop(client_id, None)
            if client:
                # Remove from all channel indexes
                for channel in client.subscriptions:
                    self._channel_index[channel].discard(client_id)

        if client:
            logger.info(f"[WSHub] Client disconnected: {client_id} | Remaining: {len(self._clients)}")

    async def subscribe(self, client_id: str, channel: str) -> None:
        """Subscribe a client to a channel."""
        async with self._lock:
            client = self._clients.get(client_id)
            if client and channel in WS_CHANNELS:
                client.subscribe(channel)
                self._channel_index[channel].add(client_id)
                logger.debug(f"[WSHub] {client_id} subscribed to '{channel}'")

    async def unsubscribe(self, client_id: str, channel: str) -> None:
        """Unsubscribe a client from a channel."""
        async with self._lock:
            client = self._clients.get(client_id)
            if client:
                client.unsubscribe(channel)
                self._channel_index[channel].discard(client_id)

    async def broadcast(self, channel: str, message: WSMessage | dict) -> int:
        """
        Broadcast a message to all clients subscribed to a channel.
        Returns the number of successful deliveries.
        """
        subscriber_ids = set(self._channel_index.get(channel, set()))
        if not subscriber_ids:
            return 0

        tasks = []
        clients_to_check = []

        async with self._lock:
            for client_id in subscriber_ids:
                client = self._clients.get(client_id)
                if client:
                    clients_to_check.append(client)

        # Send outside the lock to avoid deadlock
        results = await asyncio.gather(
            *[c.send_message(message) for c in clients_to_check],
            return_exceptions=True,
        )

        # Disconnect failed clients
        failed = [
            clients_to_check[i].client_id
            for i, r in enumerate(results)
            if isinstance(r, Exception) or r is False
        ]
        for client_id in failed:
            await self.disconnect(client_id)

        successes = sum(1 for r in results if r is True)
        return successes

    async def unicast(self, client_id: str, message: WSMessage | dict) -> bool:
        """Send a message to a specific client."""
        client = self._clients.get(client_id)
        if not client:
            return False
        return await client.send_message(message)

    async def broadcast_all(self, message: WSMessage | dict) -> int:
        """Broadcast to ALL connected clients regardless of subscriptions."""
        async with self._lock:
            clients = list(self._clients.values())
        results = await asyncio.gather(
            *[c.send_message(message) for c in clients],
            return_exceptions=True,
        )
        return sum(1 for r in results if r is True)

    def get_client_count(self) -> int:
        return len(self._clients)

    def get_channel_subscriber_count(self, channel: str) -> int:
        return len(self._channel_index.get(channel, set()))

    def get_client(self, client_id: str) -> Optional[WSClient]:
        return self._clients.get(client_id)


# Singleton hub instance
ws_hub = WSHub()
