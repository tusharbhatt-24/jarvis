"""
JARVIS Desktop — AI Console Page
=================================
Interactive AI console with chat bubbles and streaming response display.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit, QPushButton, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtMultimedia import QAudioInput, QMediaCaptureSession, QMediaRecorder, QMediaPlayer, QAudioOutput
from desktop.ui.components.widgets import SectionHeader, GlowSeparator, apply_glow
from desktop.state.app_state import AppState
from shared.constants import Colors, WSEventType

class AIConsolePage(QWidget):
    def __init__(self, ws_worker, parent=None):
        super().__init__(parent)
        self.ws_worker = ws_worker
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Header with Model Selector
        header_layout = QHBoxLayout()
        header = SectionHeader("AI CONSOLE", "Direct communication with JARVIS neural network.")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        # Model Selector
        from PySide6.QtWidgets import QComboBox
        self.model_selector = QComboBox()
        self.model_selector.addItems(["llama3.2-vision"])
        self.model_selector.setStyleSheet("padding: 5px 10px; background-color: rgba(0,0,0,0.5); color: #00f0ff; border: 1px solid rgba(0,212,255,0.3); border-radius: 4px; font-weight: bold;")
        header_layout.addWidget(self.model_selector)
        
        layout.addLayout(header_layout)
        layout.addWidget(GlowSeparator())
        
        # Chat History Area (Scrollable)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(0, 0, 10, 0)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch() # Push messages to bottom
        
        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area)
        
        # Input Area
        input_container = QFrame()
        input_container.setObjectName("glass-panel")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)
        
        self.attach_btn = QPushButton("+")
        self.attach_btn.setObjectName("secondary-btn")
        self.attach_btn.setFixedWidth(40)
        self.attach_btn.clicked.connect(self._attach_file)
        input_layout.addWidget(self.attach_btn)
        
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setObjectName("secondary-btn")
        self.mic_btn.setFixedWidth(40)
        self.mic_btn.clicked.connect(self._toggle_recording)
        input_layout.addWidget(self.mic_btn)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command or query...")
        self.input_field.returnPressed.connect(self._send_query)
        input_layout.addWidget(self.input_field)
        
        self.send_btn = QPushButton("TRANSMIT")
        self.send_btn.setObjectName("primary-btn")
        self.send_btn.clicked.connect(self._send_query)
        input_layout.addWidget(self.send_btn)
        
        layout.addWidget(input_container)
        
        apply_glow(input_container, color=Colors.ACCENT_CYAN, radius=10)
        
        self.selected_file = None
        self.is_recording = False
        
        # Audio Recording setup (sounddevice fallback)
        import os
        import tempfile
        self.temp_audio_path = os.path.join(tempfile.gettempdir(), "jarvis_speech.wav")
        self.recording_frames = []
        self.audio_stream = None
            
        # Connect to state
        self.state = AppState.instance()
        self.state.ai_token_received.connect(self._on_token_received)
        self.state.ai_response_complete.connect(self._on_response_complete)
        
        self.current_ai_bubble = None
        
        # Media Player for TTS
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Connect to raw messages for voice
        self.ws_worker.signals.raw_message.connect(self._on_raw_message)
        
    def _send_query(self):
        text = self.input_field.text().strip()
        if not text and not self.selected_file:
            return
            
        images = []
        file_name = None
        payload_text = text
        
        # Handle attachment
        if self.selected_file:
            import os
            file_name = os.path.basename(self.selected_file)
            
            if self.selected_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                import base64
                try:
                    with open(self.selected_file, "rb") as f:
                        images.append(base64.b64encode(f.read()).decode('utf-8'))
                except Exception as e:
                    print(f"Error reading image: {e}")
            else:
                # Treat as text file
                try:
                    with open(self.selected_file, "r") as f:
                        payload_text = f"Content of {file_name}:\n\n" + f.read() + "\n\n" + text
                except Exception as e:
                    print(f"Error reading file: {e}")
                    
        # Add user message to UI
        self._add_chat_bubble(text or "[Sent a file]", is_user=True, file_name=file_name)
        self.input_field.clear()
        
        # Reset attachment
        self.selected_file = None
        self.attach_btn.setText("+")
        
        # Update state
        self.state.set_ai_processing(True)
        
        # Create a new bubble for AI response
        self.current_ai_bubble = self._add_chat_bubble("", is_user=False)
        
        # Send via WS
        msg = {
            "type": WSEventType.AI_QUERY,
            "channel": "ai",
            "payload": {
                "text": payload_text,
                "context_turns": 10,
                "images": images if images else None,
                "model": self.model_selector.currentText()
            }
        }
        self.ws_worker.send_message(msg)
        
    def _attach_file(self):
        from PySide6.QtWidgets import QFileDialog
        import os
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Attach File to JARVIS", 
            "", 
            "All Files (*);;Images (*.png *.jpg *.jpeg);;Text Files (*.txt *.md *.py *.js *.json)"
        )
        if file_path:
            self.selected_file = file_path
            self.attach_btn.setText(f"📎 {os.path.basename(file_path)[:5]}...")
        
    def _toggle_recording(self):
        import sounddevice as sd
        import soundfile as sf
        from PySide6.QtCore import QTimer
        
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.mic_btn.setText("🛑")
            self.mic_btn.setStyleSheet("background-color: #ff4444;")
            
            self.recording_frames = []
            
            def callback(indata, frames, time, status):
                if status:
                    print(f"[SoundDevice] {status}")
                self.recording_frames.append(indata.copy())
                
            try:
                self.audio_stream = sd.InputStream(samplerate=44100, channels=1, callback=callback)

                self.audio_stream.start()
                self._add_chat_bubble("🎙️ Listening...", is_user=False)
            except Exception as e:
                self._add_chat_bubble(f"[Error] Failed to start microphone: {e}", is_user=False)
                self.is_recording = False
                self.mic_btn.setText("🎤")
                self.mic_btn.setStyleSheet("")
        else:
            # Stop recording
            self.is_recording = False
            self.mic_btn.setText("🎤")
            self.mic_btn.setStyleSheet("")
            
            if self.audio_stream:
                self.audio_stream.stop()
                self.audio_stream.close()
                self.audio_stream = None
                
            # Save to file
            if self.recording_frames:
                import numpy as np
                data = np.concatenate(self.recording_frames, axis=0)
                sf.write(self.temp_audio_path, data, 44100)

                
                # Wait a moment for file to save (not strictly needed now but safe)
                QTimer.singleShot(100, self._send_audio_file)
            else:
                self._add_chat_bubble("[Error] No audio recorded.", is_user=False)
            
    def _send_audio_file(self):
        import os
        import base64
        
        if os.path.exists(self.temp_audio_path):
            try:
                with open(self.temp_audio_path, "rb") as f:
                    audio_base64 = base64.b64encode(f.read()).decode('utf-8')
                    
                # Send via WS
                msg = {
                    "type": "voice_audio",
                    "channel": "ai",
                    "payload": {
                        "audio_base64": audio_base64,
                        "auto_trigger_ai": False
                    }
                }
                self.ws_worker.send_message(msg)
                
                # Remove file
                os.unlink(self.temp_audio_path)
            except Exception as e:
                self._add_chat_bubble(f"[Error reading audio: {e}]", is_user=False)
        else:
            self._add_chat_bubble("[Error] Audio file not found", is_user=False)
            
    def _on_raw_message(self, msg):
        msg_type = msg.get("type")
        payload = msg.get("payload", {})
        
        if msg_type == "voice_transcription":
            text = payload.get("text")
            if text:
                current = self.input_field.text()
                self.input_field.setText(current + " " + text if current else text)
                
        elif msg_type == "voice_audio_response":
            audio_base64 = payload.get("audio_base64")
            if audio_base64:
                self._play_audio(audio_base64)
                
    def _play_audio(self, base64_data):
        import base64
        import tempfile
        import os
        
        try:
            audio_data = base64.b64decode(base64_data)
            play_path = os.path.join(tempfile.gettempdir(), "jarvis_tts_response.mp3")
            with open(play_path, "wb") as f:
                f.write(audio_data)
                
            # Try playing with sounddevice first (pure Python, no GUI)
            import sounddevice as sd
            import soundfile as sf
            try:
                data, fs = sf.read(play_path)
                sd.play(data, fs)
            except Exception as e:
                print(f"sounddevice playback failed: {e}. Trying afplay.")
                # Fallback to afplay
                import subprocess
                try:
                    subprocess.Popen(["afplay", play_path])
                except Exception as e2:
                    print(f"afplay failed: {e2}. Trying QMediaPlayer.")
                    self.player.setSource(QUrl.fromLocalFile(play_path))
                    self.player.play()



        except Exception as e:
            print(f"Failed to play audio: {e}")
        
    def _add_chat_bubble(self, text, is_user=True, file_name=None):
        bubble = QFrame()
        bubble.setObjectName("chat-bubble-user" if is_user else "chat-bubble-ai")
        
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(15, 12, 15, 12)
        
        if file_name:
            file_frame = QFrame()
            file_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); border-radius: 4px; padding: 4px;")
            file_layout = QHBoxLayout(file_frame)
            file_layout.setContentsMargins(5, 5, 5, 5)
            
            icon_label = QLabel("📎")
            icon_label.setStyleSheet("font-size: 12px;")
            file_layout.addWidget(icon_label)
            
            name_label = QLabel(file_name)
            name_label.setStyleSheet("font-size: 11px; color: #00f0ff; font-weight: bold;")
            file_layout.addWidget(name_label)
            
            file_layout.addStretch()
            bubble_layout.addWidget(file_frame)
            
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        bubble_layout.addWidget(label)
        
        # Add timestamp
        from datetime import datetime
        time_str = datetime.now().strftime("%I:%M %p")
        time_label = QLabel(time_str)
        time_label.setStyleSheet("font-size: 10px; color: rgba(255, 255, 255, 0.5);")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        bubble_layout.addWidget(time_label)
        
        # Alignment container
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        if is_user:
            container_layout.addStretch()
            container_layout.addWidget(bubble)
        else:
            container_layout.addWidget(bubble)
            container_layout.addStretch()
            
        # Insert before the stretch at the bottom
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)
        
        # Auto scroll to bottom
        QTimer.singleShot(50, self._scroll_to_bottom)
        
        return label
        
    def _on_token_received(self, token, session_id):
        if self.current_ai_bubble:
            current_text = self.current_ai_bubble.text()
            self.current_ai_bubble.setText(current_text + token)
            self._scroll_to_bottom()
            
    def _on_response_complete(self, full_text):
        # We can do post-processing here if needed
        self.current_ai_bubble = None
        
    def _scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
