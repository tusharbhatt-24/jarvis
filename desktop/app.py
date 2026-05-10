"""
JARVIS Desktop — Application Controller
=======================================
Handles the application lifecycle, workers initialization, and window management.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject
from desktop.ui.windows.main_window import MainWindow
from desktop.ui.windows.splash_screen import SplashScreen
from desktop.workers.ws_worker import WSWorker
from desktop.state.app_state import AppState
from utils.logger import setup_logger, get_logger

log = get_logger("desktop")

class JarvisApp(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        
        # Initialize Logger
        setup_logger("desktop")
        log.info("Starting JARVIS Desktop Application")
        
        # Initialize State
        self.state = AppState.instance()
        
        # Initialize Worker
        self.ws_worker = WSWorker(parent=self)
        self._connect_worker_signals()
        
        # Windows
        self.main_window = None
        self.splash = None
        
    def run(self):
        # Start Worker Thread
        self.ws_worker.start()
        
        # Show Splash Screen
        self.splash = SplashScreen(on_complete_callback=self._show_main_window)
        self.splash.show()
        
        # Execute Event Loop
        res = self.app.exec()
        self.cleanup()
        return res
        
    def _show_main_window(self):
        log.info("Splash complete. Showing main window.")
        self.main_window = MainWindow(self.ws_worker)
        self.main_window.show()
        
    def _connect_worker_signals(self):
        # Bridge worker signals to AppState
        self.ws_worker.signals.connected.connect(lambda: self.state.set_connected(True))
        self.ws_worker.signals.disconnected.connect(lambda: self.state.set_connected(False))
        self.ws_worker.signals.system_metrics.connect(self.state.update_metrics)
        self.ws_worker.signals.ai_token.connect(self.state.append_ai_token)
        self.ws_worker.signals.ai_done.connect(self.state.complete_ai_response)
        self.ws_worker.signals.ai_error.connect(lambda err: self.state.add_notification("AI Error", err, "error"))
        
        # Also log raw messages for debugging
        self.ws_worker.signals.raw_message.connect(lambda msg: log.debug(f"WS Recv: {msg.get('type')}"))
        
    def cleanup(self):
        log.info("Cleaning up resources...")
        self.ws_worker.stop()
