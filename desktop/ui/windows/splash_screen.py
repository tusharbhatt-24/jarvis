"""
JARVIS Desktop — Splash Screen
==============================
Futuristic loading sequence with animated AI orb and cinematic transitions.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QTimer, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor
from desktop.assets.styles.theme import get_splash_stylesheet
from desktop.ui.components.widgets import AIOrb, apply_glow
from shared.constants import Colors

class SplashScreen(QWidget):
    def __init__(self, on_complete_callback):
        super().__init__()
        self.on_complete_callback = on_complete_callback
        
        # Frameless and translucent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setStyleSheet(get_splash_stylesheet())
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Orb Container to allow glow
        self.orb_container = QWidget()
        orb_layout = QVBoxLayout(self.orb_container)
        orb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.orb = AIOrb(size=120)
        orb_layout.addWidget(self.orb)
        layout.addWidget(self.orb_container)
        
        apply_glow(self.orb_container, color=Colors.ACCENT_CYAN, radius=30)
        
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.title_lbl = QLabel("JARVIS")
        self.title_lbl.setObjectName("splash-title")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_lbl)
        
        self.sub_lbl = QLabel("SYSTEM INITIALIZATION")
        self.sub_lbl.setObjectName("splash-sub")
        self.sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_lbl)
        
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        
        self.status_lbl = QLabel("Loading core modules...")
        self.status_lbl.setObjectName("splash-status")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_lbl)
        
        # Simulate loading
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(30)
        
        self._progress_val = 0
        
        # Opacity animation for fade in/out
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(1000)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.opacity_anim.start()
        
    def _update_progress(self):
        self._progress_val += 1
        self.progress.setValue(self._progress_val)
        
        if self._progress_val == 20:
            self.status_lbl.setText("Establishing neural links...")
            self.orb.set_active(True)
        elif self._progress_val == 50:
            self.status_lbl.setText("Accessing local database...")
        elif self._progress_val == 80:
            self.status_lbl.setText("Activating interface protocols...")
            
        if self._progress_val >= 100:
            self.timer.stop()
            self.status_lbl.setText("Online")
            QTimer.singleShot(500, self._fade_out)
            
    def _fade_out(self):
        self.opacity_anim.setDirection(QPropertyAnimation.Direction.Backward)
        self.opacity_anim.finished.connect(self._on_fade_out_finished)
        self.opacity_anim.start()
        
    def _on_fade_out_finished(self):
        self.hide()
        self.on_complete_callback()
        self.deleteLater()
