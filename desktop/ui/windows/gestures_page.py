"""
JARVIS Desktop — Gestures Page
================================
Displays camera feed and detected gestures.
"""

from __future__ import annotations

import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from desktop.ui.components.widgets import GlowSeparator, SectionHeader
from desktop.workers.gesture_worker import GestureWorker
from shared.constants import Colors


class GesturesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Header
        layout.addWidget(SectionHeader("VISION & GESTURE CONTROL", "Control JARVIS with hand movements"))
        layout.addWidget(GlowSeparator())
        
        # Camera Feed Container
        self.video_label = QLabel("Camera Feed Stopped")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setObjectName("glass-panel")
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: #0b1528; border-radius: 10px; color: #666;")
        layout.addWidget(self.video_label)
        
        # Controls & Info
        info_container = QFrame()
        info_container.setObjectName("glass-panel")
        info_layout = QHBoxLayout(info_container)
        info_layout.setContentsMargins(15, 10, 15, 10)
        
        self.gesture_label = QLabel("Gesture: None")
        self.gesture_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00f0ff;")
        info_layout.addWidget(self.gesture_label)
        
        info_layout.addStretch()
        
        self.toggle_btn = QPushButton("START CAMERA")
        self.toggle_btn.setObjectName("primary-btn")
        self.toggle_btn.setFixedWidth(150)
        self.toggle_btn.clicked.connect(self._toggle_camera)
        info_layout.addWidget(self.toggle_btn)
        
        layout.addWidget(info_container)
        
        # Worker
        self.worker = GestureWorker()
        self.worker.gesture_detected.connect(self._on_gesture_detected)
        self.worker.frame_ready.connect(self._on_frame_ready)
        
    def _toggle_camera(self):
        if not self.worker.isRunning():
            self.worker.start()
            self.toggle_btn.setText("STOP CAMERA")
            self.video_label.setText("Initializing Camera...")
        else:
            self.worker.stop()
            self.toggle_btn.setText("START CAMERA")
            self.video_label.setText("Camera Feed Stopped")
            self.video_label.setPixmap(QPixmap()) # Clear pixmap
            self.gesture_label.setText("Gesture: None")
            
    def _on_gesture_detected(self, gesture: str):
        self.gesture_label.setText(f"Gesture: {gesture}")
        
        # Avoid spamming actions (add a cooldown)
        if not hasattr(self, "_last_action_time"):
            self._last_action_time = 0
            
        import time
        import pyautogui
        
        current_time = time.time()
        if current_time - self._last_action_time < 1.5: # 1.5 second cooldown
            return
            
        # Simple actions mapped to gestures
        if gesture == "Fist":
            try:
                pyautogui.press('volumemute')
                self._last_action_time = current_time
                self.gesture_label.setText(f"Gesture: {gesture} (MUTED)")
            except Exception as e:
                print(f"Action failed: {e}")
            
        elif gesture == "Peace":
            try:
                pyautogui.press('playpause')
                self._last_action_time = current_time
                self.gesture_label.setText(f"Gesture: {gesture} (PLAY/PAUSE)")
            except Exception as e:
                print(f"Action failed: {e}")
                
        elif gesture == "Index Up":
            try:
                pyautogui.press('volumeup')
                self._last_action_time = current_time
                self.gesture_label.setText(f"Gesture: {gesture} (VOL UP)")
            except Exception as e:
                print(f"Action failed: {e}")
        
    def _on_frame_ready(self, frame):
        # Convert OpenCV BGR to QImage RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = image.shape
        bytes_per_line = ch * w
        q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Scale to fit label
        pixmap = QPixmap.fromImage(q_image)
        self.video_label.setPixmap(pixmap.scaled(
            self.video_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        
    def closeEvent(self, event):
        self.worker.stop()
        event.accept()
