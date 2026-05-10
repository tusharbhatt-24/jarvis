"""
JARVIS Desktop Theme Manager
============================
Centralized QSS stylesheet generation with full glassmorphism,
neon cyan palette, animations, and dark premium design.
"""

from __future__ import annotations

from shared.constants import Colors, Fonts


MAIN_STYLESHEET = f"""
/* ═══════════════════════════════════════════════════════════════════════════
   JARVIS Desktop — Global QSS Theme
   Dark Premium Glassmorphism + Neon Cyan
   ═══════════════════════════════════════════════════════════════════════════ */

/* ── Global Reset ─────────────────────────────────────────────────────────── */
* {{
    font-family: "{Fonts.PRIMARY}", "{Fonts.FALLBACK}", sans-serif;
    font-size: 13px;
    color: {Colors.TEXT_PRIMARY};
    outline: none;
    border: none;
    background: transparent;
    selection-background-color: {Colors.ACCENT_CYAN};
    selection-color: {Colors.BG_PRIMARY};
}}

QMainWindow, QDialog {{
    background-color: {Colors.BG_PRIMARY};
}}

QWidget {{
    background-color: transparent;
}}

/* ── Scrollbar ────────────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {Colors.BG_SECONDARY};
    width: 6px;
    border-radius: 3px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {Colors.ACCENT_CYAN};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {Colors.ACCENT_BLUE};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {Colors.BG_SECONDARY};
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {Colors.ACCENT_CYAN};
    border-radius: 3px;
    min-width: 30px;
}}

/* ── Glass Panel ──────────────────────────────────────────────────────────── */
QFrame#glass-panel {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(17, 17, 40, 0.85),
        stop:1 rgba(13, 13, 26, 0.75));
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 16px;
}}
QFrame#glass-panel-bright {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 20, 50, 0.90),
        stop:1 rgba(15, 15, 35, 0.80));
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 16px;
}}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
QFrame#sidebar {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(10, 10, 20, 0.98),
        stop:1 rgba(13, 13, 26, 0.95));
    border-right: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 0;
}}

/* ── Sidebar Buttons ─────────────────────────────────────────────────────── */
QPushButton#sidebar-btn {{
    background: transparent;
    color: {Colors.TEXT_SECONDARY};
    text-align: left;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 500;
    border: 1px solid transparent;
}}
QPushButton#sidebar-btn:hover {{
    background: rgba(0, 212, 255, 0.08);
    color: {Colors.ACCENT_CYAN};
    border: 1px solid rgba(0, 212, 255, 0.2);
}}
QPushButton#sidebar-btn:checked {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(0, 212, 255, 0.18),
        stop:1 rgba(0, 128, 255, 0.10));
    color: {Colors.ACCENT_CYAN};
    border: 1px solid rgba(0, 212, 255, 0.4);
    border-left: 3px solid {Colors.ACCENT_CYAN};
}}

/* ── Primary Button ───────────────────────────────────────────────────────── */
QPushButton#primary-btn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {Colors.ACCENT_CYAN},
        stop:1 {Colors.ACCENT_BLUE});
    color: {Colors.BG_PRIMARY};
    font-weight: 700;
    font-size: 13px;
    padding: 10px 24px;
    border-radius: 10px;
    border: none;
}}
QPushButton#primary-btn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #33ddff,
        stop:1 #3399ff);
}}
QPushButton#primary-btn:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #00aacc,
        stop:1 #0066cc);
}}
QPushButton#primary-btn:disabled {{
    background: rgba(0, 212, 255, 0.2);
    color: {Colors.TEXT_MUTED};
}}

/* ── Ghost Button ─────────────────────────────────────────────────────────── */
QPushButton#ghost-btn {{
    background: transparent;
    color: {Colors.ACCENT_CYAN};
    font-weight: 600;
    padding: 8px 18px;
    border-radius: 8px;
    border: 1px solid rgba(0, 212, 255, 0.4);
}}
QPushButton#ghost-btn:hover {{
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid rgba(0, 212, 255, 0.7);
}}

/* ── Icon Button ─────────────────────────────────────────────────────────── */
QPushButton#icon-btn {{
    background: transparent;
    color: {Colors.TEXT_SECONDARY};
    padding: 8px;
    border-radius: 8px;
    border: 1px solid transparent;
}}
QPushButton#icon-btn:hover {{
    background: rgba(0, 212, 255, 0.1);
    color: {Colors.ACCENT_CYAN};
    border: 1px solid rgba(0, 212, 255, 0.2);
}}

/* ── Input Fields ─────────────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: rgba(17, 17, 40, 0.8);
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 10px;
    padding: 10px 14px;
    color: {Colors.TEXT_PRIMARY};
    font-size: 13px;
    selection-background-color: {Colors.ACCENT_CYAN};
    selection-color: {Colors.BG_PRIMARY};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid rgba(0, 212, 255, 0.6);
    background: rgba(20, 20, 50, 0.9);
}}
QLineEdit::placeholder {{
    color: {Colors.TEXT_MUTED};
}}

/* ── Labels ───────────────────────────────────────────────────────────────── */
QLabel#title-xl {{
    font-size: 28px;
    font-weight: 800;
    color: {Colors.TEXT_PRIMARY};
    letter-spacing: -0.5px;
}}
QLabel#title-lg {{
    font-size: 20px;
    font-weight: 700;
    color: {Colors.TEXT_PRIMARY};
}}
QLabel#title-md {{
    font-size: 16px;
    font-weight: 600;
    color: {Colors.TEXT_PRIMARY};
}}
QLabel#subtitle {{
    font-size: 12px;
    color: {Colors.TEXT_SECONDARY};
    letter-spacing: 0.5px;
}}
QLabel#accent-text {{
    font-size: 13px;
    font-weight: 600;
    color: {Colors.ACCENT_CYAN};
}}
QLabel#mono {{
    font-family: "{Fonts.MONO}", "Consolas", monospace;
    font-size: 12px;
    color: {Colors.ACCENT_GREEN};
}}
QLabel#status-online {{
    color: {Colors.ACCENT_GREEN};
    font-size: 11px;
    font-weight: 600;
}}
QLabel#status-offline {{
    color: {Colors.ACCENT_RED};
    font-size: 11px;
    font-weight: 600;
}}

/* ── Progress Bars ────────────────────────────────────────────────────────── */
QProgressBar {{
    background: rgba(255,255,255,0.06);
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar#cpu-bar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {Colors.ACCENT_CYAN}, stop:1 {Colors.ACCENT_BLUE});
    border-radius: 4px;
}}
QProgressBar#ram-bar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {Colors.ACCENT_PURPLE}, stop:1 {Colors.ACCENT_BLUE});
    border-radius: 4px;
}}
QProgressBar#gpu-bar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {Colors.ACCENT_GREEN}, stop:1 {Colors.ACCENT_CYAN});
    border-radius: 4px;
}}

/* ── Tab Widget ───────────────────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 12px;
    background: transparent;
}}
QTabBar::tab {{
    background: transparent;
    color: {Colors.TEXT_SECONDARY};
    padding: 8px 20px;
    border-radius: 8px;
    margin-right: 4px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background: rgba(0, 212, 255, 0.15);
    color: {Colors.ACCENT_CYAN};
    border-bottom: 2px solid {Colors.ACCENT_CYAN};
}}
QTabBar::tab:hover {{
    background: rgba(0, 212, 255, 0.08);
    color: {Colors.TEXT_PRIMARY};
}}

/* ── ComboBox ─────────────────────────────────────────────────────────────── */
QComboBox {{
    background: rgba(17, 17, 40, 0.8);
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 8px;
    padding: 8px 14px;
    color: {Colors.TEXT_PRIMARY};
}}
QComboBox:focus {{
    border: 1px solid rgba(0, 212, 255, 0.6);
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background: {Colors.BG_CARD};
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 8px;
    selection-background-color: rgba(0, 212, 255, 0.2);
    padding: 4px;
}}

/* ── Separator ────────────────────────────────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {Colors.BORDER_SUBTLE};
    background: {Colors.BORDER_SUBTLE};
    border: none;
    max-height: 1px;
}}

/* ── Tooltip ──────────────────────────────────────────────────────────────── */
QToolTip {{
    background: {Colors.BG_CARD};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ── Chat Messages ────────────────────────────────────────────────────────── */
QFrame#chat-bubble-user {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(0, 128, 255, 0.2),
        stop:1 rgba(0, 212, 255, 0.12));
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 16px;
    border-bottom-right-radius: 4px;
}}
QFrame#chat-bubble-ai {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(17, 17, 40, 0.9),
        stop:1 rgba(20, 20, 55, 0.85));
    border: 1px solid rgba(123, 47, 255, 0.3);
    border-radius: 16px;
    border-bottom-left-radius: 4px;
}}

/* ── Status Badge ────────────────────────────────────────────────────────── */
QLabel#badge-online {{
    background: rgba(0, 255, 136, 0.15);
    color: {Colors.ACCENT_GREEN};
    border: 1px solid rgba(0, 255, 136, 0.4);
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 600;
}}
QLabel#badge-offline {{
    background: rgba(255, 51, 102, 0.15);
    color: {Colors.ACCENT_RED};
    border: 1px solid rgba(255, 51, 102, 0.4);
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 600;
}}

/* ── Activity Log List ────────────────────────────────────────────────────── */
QListWidget {{
    background: transparent;
    border: none;
    outline: none;
}}
QListWidget::item {{
    background: rgba(17, 17, 40, 0.5);
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 4px;
}}
QListWidget::item:hover {{
    background: rgba(0, 212, 255, 0.05);
    border: 1px solid rgba(0, 212, 255, 0.2);
}}
QListWidget::item:selected {{
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid rgba(0, 212, 255, 0.4);
    color: {Colors.TEXT_PRIMARY};
}}
"""


def get_stylesheet() -> str:
    """Return the full application stylesheet."""
    return MAIN_STYLESHEET


def get_splash_stylesheet() -> str:
    """Return stylesheet specific to the splash screen."""
    return f"""
    QWidget {{
        background-color: {Colors.BG_PRIMARY};
        font-family: "{Fonts.PRIMARY}", "{Fonts.FALLBACK}";
    }}
    QLabel#splash-title {{
        font-size: 52px;
        font-weight: 900;
        color: {Colors.ACCENT_CYAN};
        letter-spacing: 12px;
    }}
    QLabel#splash-sub {{
        font-size: 14px;
        font-weight: 400;
        color: {Colors.TEXT_SECONDARY};
        letter-spacing: 4px;
    }}
    QLabel#splash-status {{
        font-size: 12px;
        color: {Colors.TEXT_MUTED};
        letter-spacing: 2px;
    }}
    QProgressBar {{
        background: rgba(255,255,255,0.05);
        border: none;
        border-radius: 3px;
        height: 3px;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {Colors.ACCENT_CYAN},
            stop:0.5 {Colors.ACCENT_BLUE},
            stop:1 {Colors.ACCENT_PURPLE});
        border-radius: 3px;
    }}
    """
