"""
JARVIS Desktop — Settings Page
==============================
Interface for configuring AI models, voice preferences, and network settings.
"""

from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QComboBox, QFormLayout, QLineEdit, QSlider
from PySide6.QtCore import Qt, QTimer
from desktop.ui.components.widgets import SectionHeader, GlowSeparator
from desktop.state.app_state import AppState
from shared.constants import Colors

class SettingsPage(QWidget):
    def __init__(self, ws_worker, parent=None):
        super().__init__(parent)
        self.ws_worker = ws_worker
        self.state = AppState.instance()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        layout.addWidget(SectionHeader("SETTINGS", "Configure your JARVIS experience"))
        layout.addWidget(GlowSeparator())
        
        # Settings Container
        settings_container = QFrame()
        settings_container.setObjectName("glass-panel")
        form_layout = QFormLayout(settings_container)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # AI Settings Section
        ai_header = QLabel("AI Settings")
        ai_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f0ff; margin-top: 10px;")
        form_layout.addRow(ai_header)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["llama3.2-vision", "llama3", "mistral"])
        self.model_combo.setStyleSheet("padding: 8px; background-color: rgba(0,0,0,0.5); color: white; border: 1px solid rgba(0,212,255,0.3); border-radius: 4px;")
        form_layout.addRow("Default Model:", self.model_combo)
        
        # Voice Settings Section
        voice_header = QLabel("Voice Settings")
        voice_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f0ff; margin-top: 20px;")
        form_layout.addRow(voice_header)
        
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
        self.voice_combo.setStyleSheet("padding: 8px; background-color: rgba(0,0,0,0.5); color: white; border: 1px solid rgba(0,212,255,0.3); border-radius: 4px;")
        form_layout.addRow("Voice Persona:", self.voice_combo)
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 150)
        self.speed_slider.setValue(100)
        form_layout.addRow("Speech Speed (%):", self.speed_slider)
        
        # Network Settings Section
        net_header = QLabel("Network Settings")
        net_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f0ff; margin-top: 20px;")
        form_layout.addRow(net_header)
        
        self.host_input = QLineEdit("127.0.0.1")
        self.host_input.setStyleSheet("padding: 8px; background-color: rgba(0,0,0,0.5); color: white; border: 1px solid rgba(0,212,255,0.3); border-radius: 4px;")
        form_layout.addRow("Backend Host:", self.host_input)
        
        self.port_input = QLineEdit("8766")
        self.port_input.setStyleSheet("padding: 8px; background-color: rgba(0,0,0,0.5); color: white; border: 1px solid rgba(0,212,255,0.3); border-radius: 4px;")
        form_layout.addRow("Backend Port:", self.port_input)
        
        layout.addWidget(settings_container)
        
        # Save Button
        self.save_btn = QPushButton("SAVE SETTINGS")
        self.save_btn.setObjectName("primary-btn")
        self.save_btn.setFixedHeight(50)
        self.save_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.save_btn.clicked.connect(self._save_settings)
        layout.addWidget(self.save_btn)
        
        layout.addStretch()
        
    def _save_settings(self):
        # Visual confirmation
        self.save_btn.setText("SETTINGS SAVED!")
        self.save_btn.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #00ff00; color: black;")
        QTimer.singleShot(2000, self._reset_save_btn)
        
    def _reset_save_btn(self):
        self.save_btn.setText("SAVE SETTINGS")
        self.save_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
