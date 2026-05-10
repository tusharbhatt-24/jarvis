"""
JARVIS Shared Constants
=======================
Central source of truth for all constant values used across
backend, desktop, and utility modules.
"""

from __future__ import annotations

# ── Application Identity ──────────────────────────────────────────────────────
APP_NAME = "JARVIS"
APP_VERSION = "1.0.0"
APP_CODENAME = "Genesis"
APP_DESCRIPTION = "Futuristic Offline AI Assistant"

# ── Server Configuration ──────────────────────────────────────────────────────
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8766
BACKEND_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
BACKEND_WS_URL = f"ws://{BACKEND_HOST}:{BACKEND_PORT}/ws"
API_PREFIX = "/api/v1"

# ── WebSocket Channels ────────────────────────────────────────────────────────
WS_CHANNEL_AI = "ai"
WS_CHANNEL_VOICE = "voice"
WS_CHANNEL_SYSTEM = "system"
WS_CHANNEL_LOGS = "logs"
WS_CHANNEL_NOTIFICATIONS = "notifications"

WS_CHANNELS = {
    WS_CHANNEL_AI,
    WS_CHANNEL_VOICE,
    WS_CHANNEL_SYSTEM,
    WS_CHANNEL_LOGS,
    WS_CHANNEL_NOTIFICATIONS,
}

# ── WebSocket Event Types ─────────────────────────────────────────────────────
class WSEventType:
    # Connection lifecycle
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    HEARTBEAT = "heartbeat"
    HEARTBEAT_ACK = "heartbeat_ack"
    ERROR = "error"

    # AI events
    AI_QUERY = "ai_query"
    AI_TOKEN = "ai_token"
    AI_DONE = "ai_done"
    AI_ERROR = "ai_error"

    # System events
    SYSTEM_METRICS = "system_metrics"
    SYSTEM_ALERT = "system_alert"

    # Voice events
    VOICE_START = "voice_start"
    VOICE_CHUNK = "voice_chunk"
    VOICE_RESULT = "voice_result"
    VOICE_STOP = "voice_stop"

    # Log events
    LOG_ENTRY = "log_entry"

    # Notification events
    NOTIFICATION = "notification"

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = "database/jarvis.db"
DB_ECHO_SQL = False
CONVERSATION_MAX_MEMORY = 50  # Max turns in memory cache

# ── System Monitoring ─────────────────────────────────────────────────────────
METRICS_POLL_INTERVAL_SEC = 1.0   # Backend polling interval
METRICS_BROADCAST_INTERVAL_SEC = 1.0

# ── UI Colors (shared for QSS generation and docs) ────────────────────────────
class Colors:
    BG_PRIMARY   = "#0a0a0f"
    BG_SECONDARY = "#0d0d1a"
    BG_CARD      = "#111128"
    BG_GLASS     = "rgba(17, 17, 40, 0.6)"

    ACCENT_CYAN  = "#00d4ff"
    ACCENT_BLUE  = "#0080ff"
    ACCENT_PURPLE= "#7b2fff"
    ACCENT_GREEN = "#00ff88"
    ACCENT_RED   = "#ff3366"
    ACCENT_AMBER = "#ffaa00"

    TEXT_PRIMARY   = "#e8eaf6"
    TEXT_SECONDARY = "#9094b4"
    TEXT_MUTED     = "#454970"

    BORDER_SUBTLE = "rgba(0, 212, 255, 0.15)"
    BORDER_ACTIVE = "rgba(0, 212, 255, 0.6)"

    GLOW_CYAN  = "rgba(0, 212, 255, 0.3)"
    GLOW_BLUE  = "rgba(0, 128, 255, 0.3)"

# ── Fonts ─────────────────────────────────────────────────────────────────────
class Fonts:
    PRIMARY   = "Inter"
    MONO      = "JetBrains Mono"
    FALLBACK  = "Segoe UI"

# ── Animation Durations (ms) ──────────────────────────────────────────────────
class Animations:
    FAST    = 150
    NORMAL  = 300
    SLOW    = 600
    SPLASH  = 2500
    ORB_PULSE = 3000

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}"
LOG_DIR = "logs"
LOG_MAX_SIZE = "50 MB"
LOG_RETENTION = "7 days"

# ── Notification Types ────────────────────────────────────────────────────────
class NotificationType:
    INFO    = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR   = "error"
    AI      = "ai"
