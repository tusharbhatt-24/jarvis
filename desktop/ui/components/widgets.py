"""
JARVIS Desktop — Reusable Widget Components
============================================
All reusable UI primitives used across windows and panels.
Build complex UIs by composing these atomic components.
"""

from __future__ import annotations

import math
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QFrame, QHBoxLayout,
    QVBoxLayout, QProgressBar, QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    QRect, Property, QPoint, QSize, Signal,
)
from PySide6.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont,
    QLinearGradient, QPainterPath, QRadialGradient,
)

from shared.constants import Colors, Animations


# ── Utility: Apply glow drop shadow ──────────────────────────────────────────

def apply_glow(widget: QWidget, color: str = Colors.ACCENT_CYAN, radius: int = 20, strength: int = 40) -> None:
    """Apply a neon glow drop shadow to a widget."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(radius)
    shadow.setColor(QColor(color))
    shadow.setOffset(0, 0)
    widget.setGraphicsEffect(shadow)


# ── AI Orb Widget ─────────────────────────────────────────────────────────────

class AIOrb(QWidget):
    """
    Animated AI core orb with pulsing rings, rotating arcs, and glow effect.
    Pure QPainter rendering — no external assets needed.
    """

    def __init__(self, size: int = 160, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._size = size
        self._pulse = 0.0
        self._rotation = 0.0
        self._is_active = False
        self._is_listening = False

        self.setFixedSize(size + 60, size + 60)

        # Pulse animation
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_timer.start(16)  # ~60fps

        # Rotation animation
        self._rot_timer = QTimer(self)
        self._rot_timer.timeout.connect(self._update_rotation)
        self._rot_timer.start(20)

    def set_active(self, active: bool) -> None:
        """Set whether the AI is currently processing."""
        self._is_active = active
        self.update()

    def set_listening(self, listening: bool) -> None:
        """Set voice listening state."""
        self._is_listening = listening
        self.update()

    def _update_pulse(self) -> None:
        import time
        self._pulse = math.sin(time.time() * 2.0) * 0.5 + 0.5
        self.update()

    def _update_rotation(self) -> None:
        speed = 2.0 if self._is_active else 0.5
        self._rotation = (self._rotation + speed) % 360
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        r = self._size // 2

        # ── Background glow ───────────────────────────────────────────────────
        glow_grad = QRadialGradient(cx, cy, r + 30)
        glow_alpha = int(60 + self._pulse * 40)
        glow_grad.setColorAt(0, QColor(0, 212, 255, glow_alpha))
        glow_grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), QBrush(glow_grad))

        # ── Outer pulse rings ─────────────────────────────────────────────────
        for i in range(3):
            ring_alpha = int((1 - i * 0.3) * (0.3 + self._pulse * 0.3) * 255)
            ring_r = r + 15 + i * 12 + self._pulse * 8
            pen = QPen(QColor(0, 212, 255, ring_alpha))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(int(cx - ring_r), int(cy - ring_r),
                                int(ring_r * 2), int(ring_r * 2))

        # ── Rotating arcs ─────────────────────────────────────────────────────
        arc_colors = [
            QColor(0, 212, 255, 200),
            QColor(0, 128, 255, 160),
            QColor(123, 47, 255, 140),
        ]
        for i, color in enumerate(arc_colors):
            pen = QPen(color)
            pen.setWidth(2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            arc_r = r + 4 - i * 2
            rect = QRect(int(cx - arc_r), int(cy - arc_r), int(arc_r * 2), int(arc_r * 2))
            angle_start = int((self._rotation + i * 120) * 16)
            angle_span = int((120 + self._pulse * 40) * 16)
            painter.drawArc(rect, angle_start, angle_span)

        # ── Core sphere ───────────────────────────────────────────────────────
        core_grad = QRadialGradient(cx - r * 0.2, cy - r * 0.2, r)
        if self._is_listening:
            core_grad.setColorAt(0, QColor(0, 255, 136, 240))
            core_grad.setColorAt(0.4, QColor(0, 212, 255, 200))
        elif self._is_active:
            core_grad.setColorAt(0, QColor(0, 200, 255, 250))
            core_grad.setColorAt(0.4, QColor(0, 128, 255, 220))
        else:
            core_grad.setColorAt(0, QColor(30, 40, 80, 240))
            core_grad.setColorAt(0.4, QColor(15, 20, 50, 220))
        core_grad.setColorAt(0.7, QColor(10, 15, 40, 200))
        core_grad.setColorAt(1.0, QColor(5, 10, 30, 180))
        painter.setBrush(QBrush(core_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(cx - r), int(cy - r), r * 2, r * 2)

        # ── Core highlight ────────────────────────────────────────────────────
        highlight_grad = QRadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.5)
        highlight_alpha = int(80 + self._pulse * 60)
        highlight_grad.setColorAt(0, QColor(255, 255, 255, highlight_alpha))
        highlight_grad.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(highlight_grad))
        painter.drawEllipse(int(cx - r), int(cy - r), r * 2, r * 2)

        # ── Core text ─────────────────────────────────────────────────────────
        font = QFont("Inter", 9, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(0, 212, 255, 200))
        text = "LISTENING" if self._is_listening else ("ACTIVE" if self._is_active else "JARVIS")
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)

        painter.end()


# ── Metric Card ──────────────────────────────────────────────────────────────

class MetricCard(QFrame):
    """System metric display card with label, value, and progress bar."""

    def __init__(self, title: str, bar_object_name: str = "cpu-bar", parent=None):
        super().__init__(parent)
        self.setObjectName("glass-panel")
        self.setFixedHeight(90)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # Header row
        header = QHBoxLayout()
        self._title_lbl = QLabel(title)
        self._title_lbl.setObjectName("subtitle")
        self._value_lbl = QLabel("0%")
        self._value_lbl.setObjectName("accent-text")
        self._value_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        header.addWidget(self._title_lbl)
        header.addWidget(self._value_lbl)
        layout.addLayout(header)

        # Sub-value
        self._sub_lbl = QLabel("")
        self._sub_lbl.setObjectName("subtitle")
        layout.addWidget(self._sub_lbl)

        # Progress bar
        self._bar = QProgressBar()
        self._bar.setObjectName(bar_object_name)
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedHeight(6)
        self._bar.setTextVisible(False)
        layout.addWidget(self._bar)

    def update_value(self, percent: float, sub: str = "") -> None:
        self._value_lbl.setText(f"{percent:.1f}%")
        self._bar.setValue(int(percent))
        if sub:
            self._sub_lbl.setText(sub)


# ── Status Indicator ──────────────────────────────────────────────────────────

class StatusIndicator(QWidget):
    """Animated dot + text status indicator."""

    def __init__(self, text: str = "Offline", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._dot = QLabel("●")
        self._dot.setObjectName("status-offline")
        self._text = QLabel(text)
        self._text.setObjectName("subtitle")

        layout.addWidget(self._dot)
        layout.addWidget(self._text)
        layout.addStretch()

        # Blink animation
        self._blink = True
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._toggle_blink)
        self._online = False

    def set_online(self, online: bool, text: str = "") -> None:
        self._online = online
        if text:
            self._text.setText(text)
        if online:
            self._dot.setObjectName("status-online")
            self._timer.start(1200)
        else:
            self._dot.setObjectName("status-offline")
            self._timer.stop()
            self._dot.setText("●")
        self._dot.style().unpolish(self._dot)
        self._dot.style().polish(self._dot)

    def _toggle_blink(self) -> None:
        self._blink = not self._blink
        self._dot.setText("●" if self._blink else "○")


# ── Notification Toast ────────────────────────────────────────────────────────

class NotificationToast(QFrame):
    """Animated slide-in notification toast."""

    def __init__(self, title: str, message: str, notif_type: str = "info", parent=None):
        super().__init__(parent)
        self.setObjectName("glass-panel-bright")
        self.setFixedWidth(320)
        self.setMinimumHeight(70)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        # Icon
        icon_map = {"info": "ℹ", "success": "✓", "warning": "⚠", "error": "✗", "ai": "◈"}
        color_map = {
            "info": Colors.ACCENT_CYAN, "success": Colors.ACCENT_GREEN,
            "warning": Colors.ACCENT_AMBER, "error": Colors.ACCENT_RED,
            "ai": Colors.ACCENT_PURPLE,
        }
        icon_lbl = QLabel(icon_map.get(notif_type, "ℹ"))
        icon_lbl.setStyleSheet(f"color: {color_map.get(notif_type, Colors.ACCENT_CYAN)}; font-size: 18px;")
        icon_lbl.setFixedWidth(24)
        layout.addWidget(icon_lbl)

        # Text
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("title-md")
        title_lbl.setStyleSheet("font-size: 13px; font-weight: 700;")
        msg_lbl = QLabel(message)
        msg_lbl.setObjectName("subtitle")
        msg_lbl.setWordWrap(True)
        text_col.addWidget(title_lbl)
        text_col.addWidget(msg_lbl)
        layout.addLayout(text_col)

        apply_glow(self, color_map.get(notif_type, Colors.ACCENT_CYAN), radius=15)


# ── Separator ─────────────────────────────────────────────────────────────────

class GlowSeparator(QFrame):
    """Thin glowing horizontal separator."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setStyleSheet(f"background: {Colors.BORDER_SUBTLE}; max-height: 1px;")


# ── Section Header ────────────────────────────────────────────────────────────

class SectionHeader(QWidget):
    """Section title with optional accent line."""

    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("title-lg")
        layout.addWidget(title_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setObjectName("subtitle")
            layout.addWidget(sub_lbl)


# ── Animated Counter Label ────────────────────────────────────────────────────

class AnimatedCounter(QLabel):
    """Label that animates number changes with smooth counting effect."""

    def __init__(self, initial: float = 0, suffix: str = "", parent=None):
        super().__init__(parent)
        self._current = initial
        self._target = initial
        self._suffix = suffix
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._step)
        self.setText(f"{initial:.1f}{suffix}")

    def set_value(self, value: float) -> None:
        self._target = value
        if not self._timer.isActive():
            self._timer.start(16)

    def _step(self) -> None:
        diff = self._target - self._current
        if abs(diff) < 0.1:
            self._current = self._target
            self._timer.stop()
        else:
            self._current += diff * 0.15
        self.setText(f"{self._current:.1f}{self._suffix}")
