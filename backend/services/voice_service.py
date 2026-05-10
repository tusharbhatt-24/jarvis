"""
JARVIS Voice Service (Phase 3 - Voice Assistant)
================================================
Handles Speech-to-Text (STT) using faster-whisper
and Text-to-Speech (TTS) using edge-tts.
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Optional

import edge_tts
from faster_whisper import WhisperModel
from loguru import logger

from shared.constants import WS_CHANNEL_AI, WSEventType


class VoiceService:
    """
    Voice service for audio transcription and vocalization.
    """

    def __init__(self, ws_hub):
        self._hub = ws_hub
        self._stt_model: Optional[WhisperModel] = None
        self._stt_ready = False
        self._tts_voice = "en-US-ChristopherNeural" # Premium male voice or "en-US-AriaNeural" for female
        
    async def initialize(self) -> None:
        """Initialize models in a background thread to avoid blocking."""
        logger.info("[VoiceService] Initializing models...")
        
        # Load Whisper model in a separate thread because it's CPU intensive
        try:
            loop = asyncio.get_running_loop()
            # "tiny" or "base" is good for fast local inference
            self._stt_model = await loop.run_in_executor(
                None, 
                lambda: WhisperModel("tiny", device="cpu", compute_type="int8")
            )
            self._stt_ready = True
            logger.success("[VoiceService] Faster-Whisper (tiny) loaded successfully")
        except Exception as e:
            logger.error(f"[VoiceService] Failed to load Whisper model: {e}")
            self._stt_ready = False

    async def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe an audio file to text."""
        if not self._stt_ready or self._stt_model is None:
            raise Exception("STT model is not ready")
            
        logger.info(f"[VoiceService] Transcribing {audio_path}...")
        
        loop = asyncio.get_running_loop()
        
        def _transcribe():
            segments, info = self._stt_model.transcribe(audio_path, beam_size=5)
            full_text = ""
            for segment in segments:
                full_text += segment.text + " "
            return full_text.strip()
            
        text = await loop.run_in_executor(None, _transcribe)
        logger.info(f"[VoiceService] Transcription complete: '{text}'")
        return text

    async def generate_speech(self, text: str, output_path: str) -> bool:
        """Generate speech from text and save to a file."""
        logger.info(f"[VoiceService] Generating speech for: '{text[:20]}...'")
        try:
            communicate = edge_tts.Communicate(text, self._tts_voice)
            await communicate.save(output_path)
            logger.info(f"[VoiceService] Speech saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"[VoiceService] Failed to generate speech: {e}")
            return False

    def is_stt_ready(self) -> bool:
        return self._stt_ready
