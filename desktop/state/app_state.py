"""
JARVIS Desktop — App State Manager
====================================
Centralized reactive state for the entire desktop application.
All UI components read from and subscribe to this singleton.
State mutations only happen via methods — no direct attribute writes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from PySide6.QtCore import QObject, Signal

from shared.schemas import SystemMetrics
from shared.constants import NotificationType


@dataclass
class ConnectionState:
    is_connected: bool = False
    backend_url: str = ""
    last_connected: Optional[datetime] = None
    reconnect_attempts: int = 0


@dataclass
class AIState:
    is_processing: bool = False
    current_session_id: Optional[str] = None
    current_response: str = ""
    total_queries: int = 0


@dataclass
class NotificationItem:
    title: str
    message: str
    type: str
    timestamp: datetime = field(default_factory=datetime.now)
    read: bool = False


class AppState(QObject):
    """
    Singleton application state with reactive Qt signals.
    
    Usage:
        state = AppState.instance()
        state.connection_changed.connect(my_handler)
        state.set_connected(True)
    """

    # ── Signals ───────────────────────────────────────────────────────────────
    connection_changed = Signal(bool)
    metrics_updated = Signal(object)         # SystemMetrics
    ai_state_changed = Signal(object)        # AIState
    ai_token_received = Signal(str, str)     # token, session_id
    ai_response_complete = Signal(str)       # full response text
    notification_added = Signal(object)      # NotificationItem
    active_page_changed = Signal(str)
    log_entry_added = Signal(dict)

    _instance: Optional["AppState"] = None

    def __init__(self):
        super().__init__()
        self.connection = ConnectionState()
        self.ai = AIState()
        self.metrics: Optional[SystemMetrics] = None
        self.active_page: str = "dashboard"
        self.notifications: list[NotificationItem] = []
        self.activity_log: list[dict] = []

    @classmethod
    def instance(cls) -> "AppState":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Connection ────────────────────────────────────────────────────────────

    def set_connected(self, connected: bool, url: str = "") -> None:
        self.connection.is_connected = connected
        if connected:
            self.connection.last_connected = datetime.now()
            self.connection.reconnect_attempts = 0
            if url:
                self.connection.backend_url = url
        self.connection_changed.emit(connected)

    # ── Metrics ───────────────────────────────────────────────────────────────

    def update_metrics(self, metrics_dict: dict) -> None:
        try:
            self.metrics = SystemMetrics(**metrics_dict)
            self.metrics_updated.emit(self.metrics)
        except Exception as e:
            pass  # Silently skip malformed metrics

    # ── AI State ──────────────────────────────────────────────────────────────

    def set_ai_processing(self, processing: bool, session_id: str = "") -> None:
        self.ai.is_processing = processing
        if session_id:
            self.ai.current_session_id = session_id
        if processing:
            self.ai.current_response = ""
        self.ai_state_changed.emit(self.ai)

    def append_ai_token(self, token: str, session_id: str) -> None:
        self.ai.current_response += token
        self.ai_token_received.emit(token, session_id)

    def complete_ai_response(self, session_id: str, token_count: int) -> None:
        full_response = self.ai.current_response
        self.ai.is_processing = False
        self.ai.total_queries += 1
        self.ai_state_changed.emit(self.ai)
        self.ai_response_complete.emit(full_response)

    # ── Notifications ─────────────────────────────────────────────────────────

    def add_notification(
        self,
        title: str,
        message: str,
        notif_type: str = NotificationType.INFO,
    ) -> NotificationItem:
        item = NotificationItem(title=title, message=message, type=notif_type)
        self.notifications.insert(0, item)
        if len(self.notifications) > 100:
            self.notifications = self.notifications[:100]
        self.notification_added.emit(item)
        return item

    def get_unread_count(self) -> int:
        return sum(1 for n in self.notifications if not n.read)

    def mark_all_read(self) -> None:
        for n in self.notifications:
            n.read = True

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate_to(self, page: str) -> None:
        if page != self.active_page:
            self.active_page = page
            self.active_page_changed.emit(page)

    # ── Activity Log ──────────────────────────────────────────────────────────

    def add_log_entry(self, entry: dict) -> None:
        self.activity_log.insert(0, entry)
        if len(self.activity_log) > 500:
            self.activity_log = self.activity_log[:500]
        self.log_entry_added.emit(entry)
