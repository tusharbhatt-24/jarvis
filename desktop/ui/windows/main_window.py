"""
JARVIS Desktop — Main Window
============================
The primary container window featuring the sidebar navigation and stacked pages.
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QFrame, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent
from desktop.ui.windows.dashboard_page import DashboardPage
from desktop.ui.windows.ai_console_page import AIConsolePage
from desktop.ui.windows.gestures_page import GesturesPage
from desktop.ui.windows.knowledge_page import KnowledgePage
from desktop.ui.windows.voice_page import VoicePage
from desktop.ui.windows.settings_page import SettingsPage
from desktop.ui.components.widgets import AIOrb, StatusIndicator, apply_glow
from desktop.assets.styles.theme import get_stylesheet
from desktop.state.app_state import AppState
from shared.constants import Colors

class MainWindow(QMainWindow):
    def __init__(self, ws_worker):
        super().__init__()
        self.ws_worker = ws_worker
        self.state = AppState.instance()
        
        self.setWindowTitle("JARVIS")
        self.resize(1100, 700)
        
        # Apply global stylesheet
        self.setStyleSheet(get_stylesheet())
        
        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout = QHBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ── Sidebar ───────────────────────────────────────────────────────────
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(10)
        
        # App Title / Logo Area
        logo_layout = QHBoxLayout()
        self.small_orb = AIOrb(size=40)
        logo_layout.addWidget(self.small_orb)
        
        title_vbox = QVBoxLayout()
        title_lbl = QLabel("JARVIS")
        title_lbl.setObjectName("title-md")
        sub_lbl = QLabel("v1.0.0")
        sub_lbl.setObjectName("subtitle")
        title_vbox.addWidget(title_lbl)
        title_vbox.addWidget(sub_lbl)
        logo_layout.addLayout(title_vbox)
        logo_layout.addStretch()
        
        sidebar_layout.addLayout(logo_layout)
        sidebar_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # Navigation Buttons
        self.nav_buttons = {}
        self._create_nav_btn("dashboard", "DASHBOARD", sidebar_layout)
        self._create_nav_btn("ai_console", "AI CONSOLE", sidebar_layout)
        self._create_nav_btn("voice", "VOICE", sidebar_layout)
        self._create_nav_btn("vision", "VISION", sidebar_layout)
        self._create_nav_btn("knowledge", "KNOWLEDGE", sidebar_layout)
        self._create_nav_btn("settings", "SETTINGS", sidebar_layout)
        
        sidebar_layout.addStretch()
        
        # Status Indicator at bottom of sidebar
        self.status_ind = StatusIndicator("Connecting...")
        sidebar_layout.addWidget(self.status_ind)
        
        main_layout.addWidget(self.sidebar, 1)
        
        # ── Content Area (Stacked Widget) ────────────────────────────────────
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 4)
        
        # Initialize Pages
        self.pages = {}
        self.pages["dashboard"] = DashboardPage()
        self.pages["ai_console"] = AIConsolePage(self.ws_worker)
        self.pages["vision"] = GesturesPage()
        self.pages["knowledge"] = KnowledgePage(self.ws_worker)
        
        # Pages
        self.pages["voice"] = VoicePage(self.ws_worker)
        self.pages["settings"] = SettingsPage(self.ws_worker)
        
        for key, page in self.pages.items():
            self.stacked_widget.addWidget(page)
            
        # Connect state
        self.state.active_page_changed.connect(self._on_page_changed)
        self.state.connection_changed.connect(self._on_connection_changed)
        
        # Set initial connection state if already connected
        if self.state.connection.is_connected:
            self._on_connection_changed(True)
            
        # Set initial page
        self._set_active_nav_button("dashboard")
        
        # Make window draggable despite being frameless (if requested, but here we just have a standard window or custom top bar)
        # For this design, let's keep it a standard window but with premium QSS styling.
        
    def _create_nav_btn(self, page_id, label, layout):
        btn = QPushButton(label)
        btn.setObjectName("sidebar-btn")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.state.navigate_to(page_id))
        layout.addWidget(btn)
        self.nav_buttons[page_id] = btn
        
    def _set_active_nav_button(self, page_id):
        for pid, btn in self.nav_buttons.items():
            btn.setChecked(pid == page_id)
            
    def _on_page_changed(self, page_id):
        self._set_active_nav_button(page_id)
        if page_id in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[page_id])
            
    def _on_connection_changed(self, connected):
        if connected:
            self.status_ind.set_online(True, "Online")
            self.small_orb.set_active(True)
        else:
            self.status_ind.set_online(False, "Offline")
            self.small_orb.set_active(False)
            
    def _create_placeholder_page(self, title, description):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("title-lg")
        layout.addWidget(lbl_title)
        
        lbl_desc = QLabel(description)
        lbl_desc.setObjectName("subtitle")
        layout.addWidget(lbl_desc)
        
        layout.addStretch()
        return widget
