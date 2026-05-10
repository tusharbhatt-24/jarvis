"""
JARVIS Desktop — Voice Page
============================
Interface for the voice assistant with a pulsing AI Orb.
"""

from __future__ import annotations

import base64
import os
import subprocess
import tempfile
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget
from loguru import logger

from desktop.ui.components.widgets import AIOrb, GlowSeparator, SectionHeader
from shared.constants import Colors


class VoicePage(QWidget):
    def __init__(self, ws_worker, parent=None):
        super().__init__(parent)
        self.ws_worker = ws_worker
        self.is_recording = False
        self.recording_frames = []
        self.audio_stream = None
        self.playback_process = None
        
        # Initialize QMediaPlayer for robust playback
        from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Temp path to save audio
        self.temp_audio_path = os.path.join(tempfile.gettempdir(), "jarvis_voice_page.wav")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with Model Selector
        from PySide6.QtWidgets import QHBoxLayout, QComboBox
        header_layout = QHBoxLayout()
        header = SectionHeader("VOICE ASSISTANT", "Talk to JARVIS directly")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        self.model_selector = QComboBox()
        self.model_selector.addItems(["llama3.2-vision"])
        self.model_selector.setStyleSheet("padding: 5px 10px; background-color: rgba(0,0,0,0.5); color: #00f0ff; border: 1px solid rgba(0,212,255,0.3); border-radius: 4px; font-weight: bold;")
        header_layout.addWidget(self.model_selector)
        
        layout.addLayout(header_layout)
        layout.addWidget(GlowSeparator())
        
        # Center Area with Orb
        orb_container = QFrame()
        orb_container.setObjectName("glass-panel")
        orb_layout = QVBoxLayout(orb_container)
        orb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        orb_layout.setContentsMargins(20, 20, 20, 20)
        
        self.orb = AIOrb(size=200)
        orb_layout.addWidget(self.orb)
        
        self.status_label = QLabel("Click the button below to start speaking.")
        self.status_label.setStyleSheet("font-size: 16px; color: #888; margin-top: 15px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        orb_layout.addWidget(self.status_label)
        
        layout.addWidget(orb_container)
        
        # Conversation Display
        self.conversation_frame = QFrame()
        self.conversation_frame.setObjectName("glass-panel")
        conv_layout = QVBoxLayout(self.conversation_frame)
        conv_layout.setContentsMargins(20, 20, 20, 20)
        conv_layout.setSpacing(10)
        
        self.user_lbl = QLabel("You: ...")
        self.user_lbl.setWordWrap(True)
        self.user_lbl.setStyleSheet("color: #00f0ff; font-size: 14px;")
        conv_layout.addWidget(self.user_lbl)
        
        conv_layout.addWidget(GlowSeparator())
        
        self.ai_lbl = QLabel("JARVIS: ...")
        self.ai_lbl.setWordWrap(True)
        self.ai_lbl.setStyleSheet("color: #fff; font-size: 14px;")
        conv_layout.addWidget(self.ai_lbl)
        
        layout.addWidget(self.conversation_frame)
        
        # Control Button
        # Control Buttons
        from PySide6.QtWidgets import QHBoxLayout
        btn_layout = QHBoxLayout()
        
        self.listen_btn = QPushButton("START LISTENING")
        self.listen_btn.setObjectName("primary-btn")
        self.listen_btn.setFixedHeight(50)
        self.listen_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.listen_btn.clicked.connect(self._toggle_listening)
        btn_layout.addWidget(self.listen_btn, 3)
        
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setObjectName("secondary-btn")
        self.stop_btn.setFixedHeight(50)
        self.stop_btn.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #ff3366; color: white;")
        self.stop_btn.clicked.connect(self._stop_playback)
        btn_layout.addWidget(self.stop_btn, 1)
        
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        # Connect to raw messages to hear back from backend
        self.ws_worker.signals.raw_message.connect(self._on_raw_message)
        
    def _toggle_listening(self):
        import sounddevice as sd
        import soundfile as sf
        
        # Stop playback if playing (Barge-in)
        self._stop_playback()
        
        if not self.is_recording:
            self.is_recording = True
            self.listen_btn.setText("STOP LISTENING")
            self.listen_btn.setStyleSheet("background-color: #ff4444; font-size: 16px; font-weight: bold;")
            self.orb.set_listening(True)
            self.status_label.setText("Listening... Speak now.")
            self.status_label.setStyleSheet("color: #00ff00; font-size: 16px;")
            
            self.recording_frames = []
            
            def callback(indata, frames, time, status):
                self.recording_frames.append(indata.copy())
                
            try:
                self.audio_stream = sd.InputStream(samplerate=16000, channels=1, callback=callback)
                self.audio_stream.start()
            except Exception as e:
                self.status_label.setText(f"Error starting mic: {e}")
                self.status_label.setStyleSheet("color: #ff4444; font-size: 16px;")
                self.is_recording = False
                self.listen_btn.setText("START LISTENING")
                self.listen_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
                self.orb.set_listening(False)
        else:
            self.is_recording = False
            self.listen_btn.setText("START LISTENING")
            self.listen_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
            self.orb.set_listening(False)
            self.orb.set_active(True)  # Set processing state
            self.status_label.setText("Processing your speech...")
            self.status_label.setStyleSheet("color: #00f0ff; font-size: 16px;")
            
            if self.audio_stream:
                self.audio_stream.stop()
                self.audio_stream.close()
                self.audio_stream = None
                
            if self.recording_frames:
                import numpy as np
                data = np.concatenate(self.recording_frames, axis=0)
                sf.write(self.temp_audio_path, data, 16000)
                
                # Send to backend after a short delay
                QTimer.singleShot(100, self._send_audio)
                
    def _send_audio(self):
        if os.path.exists(self.temp_audio_path):
            try:
                with open(self.temp_audio_path, "rb") as f:
                    audio_base64 = base64.b64encode(f.read()).decode('utf-8')
                    
                msg = {
                    "type": "voice_audio",
                    "channel": "ai",
                    "payload": {
                        "audio_base64": audio_base64,
                        "auto_trigger_ai": True,
                        "model": self.model_selector.currentText()
                    }
                }
                self.ws_worker.send_message(msg)
                os.unlink(self.temp_audio_path)
            except Exception as e:
                self.status_label.setText(f"Error sending audio: {e}")
                self.status_label.setStyleSheet("color: #ff4444; font-size: 16px;")
                self.orb.set_active(False)
                
    def _stop_playback(self):
        if self.playback_process and self.playback_process.poll() is None:
            try:
                self.playback_process.terminate()
                self.playback_process.wait(timeout=1)
            except Exception as e:
                print(f"Failed to terminate playback: {e}")
            self.playback_process = None
            self.status_label.setText("Playback stopped.")
            self.status_label.setStyleSheet("color: #888; font-size: 16px;")
            self.orb.set_active(False)
            
    def _on_raw_message(self, msg: dict):
        msg_type = msg.get("type")
        payload = msg.get("payload", {})
        
        if msg_type == "voice_transcription":  # Whisper result
            text = payload.get("text")
            if text:
                self.user_lbl.setText(f"You: {text}")
            
        elif msg_type == "voice_audio_response":  # Audio response from edge-tts
            self.orb.set_active(False)
            self.status_label.setText("Speaking...")
            self.status_label.setStyleSheet("color: #00ff00; font-size: 16px;")
            
            audio_base64 = payload.get("audio_base64")
            if audio_base64:
                self._play_audio_mac(audio_base64)
                
        elif msg_type == "ai_token":  # Accumulate tokens if needed
            # For now we just wait for the final voice response
            pass
            
    def _play_audio_mac(self, base64_data: str):
        """Play audio on Mac using afplay fallback."""
        try:
            logger.info(f"[VoicePage] Playing audio, data length: {len(base64_data)}")
            audio_data = base64.b64decode(base64_data)
            play_path = os.path.join(tempfile.gettempdir(), "jarvis_voice_page_response.mp3")
            with open(play_path, "wb") as f:
                f.write(audio_data)
                
            logger.info(f"[VoicePage] Saved audio to {play_path}")
            
            # Use QMediaPlayer instead of afplay
            from PySide6.QtCore import QUrl
            self.player.setSource(QUrl.fromLocalFile(play_path))
            self.player.play()
            logger.info(f"[VoicePage] Started playback with QMediaPlayer")
            
            # Reset status after a few seconds
            QTimer.singleShot(3000, lambda: self.status_label.setText("Click the button below to start speaking."))
            QTimer.singleShot(3000, lambda: self.status_label.setStyleSheet("font-size: 16px; color: #888;"))
        except Exception as e:
            logger.error(f"[VoicePage] Failed to play audio: {e}")
            self.status_label.setText(f"Playback error: {e}")
            self.status_label.setStyleSheet("color: #ff4444; font-size: 16px;")
