"""
JARVIS Desktop — Gesture Worker
================================
Captures video from webcam, detects hand gestures using MediaPipe,
and controls the system or app.
"""

from __future__ import annotations

import time
import cv2
import mediapipe as mp
import pyautogui
from PySide6.QtCore import QThread, Signal
from loguru import logger


class GestureWorker(QThread):
    """
    Worker thread that runs OpenCV and MediaPipe to detect gestures.
    Emits signals for detected gestures and camera frames.
    """
    gesture_detected = Signal(str)
    frame_ready = Signal(object)  # Emits numpy array (frame)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def run(self) -> None:
        """Main loop for camera capture and processing."""
        self._running = True
        logger.info("[GestureWorker] Starting camera capture...")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            logger.error("[GestureWorker] Failed to open webcam")
            self.gesture_detected.emit("Camera Error")
            self._running = False
            return
            
        while self._running:
            success, frame = cap.read()
            if not success:
                logger.warning("[GestureWorker] Failed to read frame")
                time.sleep(0.1)
                continue
                
            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)
            
            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            gesture = "None"
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks on the frame (optional, for UI)
                    self.mp_draw.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Simple gesture detection logic
                    landmarks = hand_landmarks.landmark
                    
                    # Tips vs Pips
                    index_up = landmarks[8].y < landmarks[6].y
                    middle_up = landmarks[12].y < landmarks[10].y
                    ring_up = landmarks[16].y < landmarks[14].y
                    pinky_up = landmarks[20].y < landmarks[18].y
                    
                    # Thumb
                    thumb_up = landmarks[4].y < landmarks[2].y
                    thumb_down = landmarks[4].y > landmarks[2].y
                    
                    if index_up and not middle_up and not ring_up and not pinky_up:
                        gesture = "Index Up"
                    elif index_up and middle_up and not ring_up and not pinky_up:
                        gesture = "Peace"
                    elif not index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
                        gesture = "Fist"
                    elif index_up and middle_up and ring_up and pinky_up:
                        gesture = "Open Palm"
                    elif thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
                        gesture = "Thumb Up"
                    elif thumb_down and not index_up and not middle_up and not ring_up and not pinky_up:
                        gesture = "Thumb Down"
                        
                if gesture != "None":
                    logger.debug(f"[GestureWorker] Detected gesture: {gesture}")
                    self.gesture_detected.emit(gesture)
                    
            # Emit the processed frame
            self.frame_ready.emit(frame)
            
            # Control frame rate (~30 FPS)
            time.sleep(0.03)
            
        cap.release()
        logger.info("[GestureWorker] Camera capture stopped")
        
    def stop(self) -> None:
        """Stop the worker thread."""
        self._running = False
        self.wait(2000)
