"""
JARVIS Desktop — Knowledge Page
================================
Interface to add and manage facts in the knowledge base.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from desktop.ui.components.widgets import GlowSeparator, SectionHeader, apply_glow
from shared.constants import Colors


class KnowledgePage(QWidget):
    def __init__(self, ws_worker, parent=None):
        super().__init__(parent)
        self.ws_worker = ws_worker
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Header
        layout.addWidget(SectionHeader("KNOWLEDGE BASE", "Teach JARVIS new facts and information"))
        layout.addWidget(GlowSeparator())
        
        # Add Knowledge Area
        container = QFrame()
        container.setObjectName("glass-panel")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.setSpacing(15)
        
        title_lbl = QLabel("Add New Information")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f0ff;")
        vbox.addWidget(title_lbl)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter information here that you want JARVIS to remember and use as context...")
        self.text_input.setStyleSheet("background-color: #0b1528; border: 1px solid #1a2942; border-radius: 5px; padding: 10px; color: #fff;")
        vbox.addWidget(self.text_input)
        
        hbox = QHBoxLayout()
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Tags (comma separated, optional)")
        self.tags_input.setStyleSheet("background-color: #0b1528; border: 1px solid #1a2942; border-radius: 5px; padding: 8px; color: #fff;")
        hbox.addWidget(self.tags_input)
        
        self.save_btn = QPushButton("MEMORIZE")
        self.save_btn.setObjectName("primary-btn")
        self.save_btn.setFixedWidth(120)
        self.save_btn.clicked.connect(self._save_knowledge)
        hbox.addWidget(self.save_btn)
        
        vbox.addLayout(hbox)
        layout.addWidget(container)
        
        apply_glow(container, color=Colors.ACCENT_CYAN, radius=10)
        
        # Status
        self.status_label = QLabel("Ready to memorize.")
        self.status_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Connect to raw messages to hear back from backend
        self.ws_worker.signals.raw_message.connect(self._on_raw_message)
        
    def _save_knowledge(self):
        text = self.text_input.toPlainText().strip()
        tags = self.tags_input.text().strip()
        
        if not text:
            self.status_label.setText("Please enter some text.")
            self.status_label.setStyleSheet("color: #ff4444;")
            return
            
        # Send via WS
        msg = {
            "type": "knowledge_add",
            "channel": "ai",
            "payload": {
                "text": text,
                "metadata": {"tags": tags} if tags else {}
            }
        }
        self.ws_worker.send_message(msg)
        self.status_label.setText("Sending to memory...")
        self.status_label.setStyleSheet("color: #00f0ff;")
        
    def _on_raw_message(self, msg: dict):
        msg_type = msg.get("type")
        payload = msg.get("payload", {})
        
        if msg_type == "knowledge_added":
            success = payload.get("success")
            if success:
                self.status_label.setText("Successfully memorized and indexed!")
                self.status_label.setStyleSheet("color: #00ff00;")
                self.text_input.clear()
                self.tags_input.clear()
            else:
                self.status_label.setText("Failed to memorize. Check backend logs.")
                self.status_label.setStyleSheet("color: #ff4444;")
