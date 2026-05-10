"""
JARVIS Desktop — Entry Point
============================
Run this file to start the desktop application.
"""

import sys
import os

# Add project root to python path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from desktop.app import JarvisApp

def main():
    try:
        app = JarvisApp()
        sys.exit(app.run())
    except Exception as e:
        print(f"Fatal error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
