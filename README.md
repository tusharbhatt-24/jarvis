# JARVIS - Offline AI Assistant

JARVIS is a powerful, local-first AI assistant designed to run entirely on your machine. It combines a high-performance **FastAPI** backend with a beautiful **PySide6 (Qt)** desktop interface and a **Flutter** mobile companion app, offering real-time interaction, system monitoring, and extensible AI capabilities across devices.

## 🚀 Features

### Core Features
- **Desktop GUI**: A premium user interface built with PySide6, featuring a splash screen, main window, and real-time state management.
- **Mobile Companion App**: A Flutter-based mobile application for interaction on the go, communicating in real-time with the backend.
- **FastAPI Backend**: A robust, asynchronous API server handling service orchestration and WebSocket communication.
- **Real-time Communication**: Bi-directional communication between clients (Desktop & Mobile) and the backend using WebSockets.
- **System Monitoring**: Live tracking of CPU and GPU metrics (via `psutil` and `GPUtil`).
- **Asynchronous Architecture**: Built from the ground up to be non-blocking and highly responsive.

### AI & Voice Services (In Development/Active)
- **AI Service**: Handles local LLM interactions (ready for streaming responses).
- **Voice Service**: Foundation for Text-to-Speech and Speech-to-Text capabilities.
- **Knowledge Service**: Manages local knowledge base.

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn (with standard workers)
- **WebSockets**: websockets
- **Database**: SQLAlchemy with `aiosqlite` (Async SQLite) and Alembic for migrations.
- **Data Validation**: Pydantic v2
- **Logging**: Loguru
- **Monitoring**: `psutil`, `GPUtil`

### Desktop Client
- **Framework**: PySide6 (Qt for Python)
- **Styling**: Custom themes

### Mobile Client
- **Framework**: Flutter (Dart)
- **State Management**: Provider
- **Communication**: `web_socket_channel`

## 📁 Project Structure

```text
jarvis/
├── backend/            # FastAPI Backend
│   ├── api/            # API Routes (REST & WebSocket)
│   ├── core/           # Configuration and core logic
│   ├── database/       # Models and database initialization
│   ├── services/       # Core services (AI, Voice, System, Knowledge)
│   └── main.py         # Backend entry point
├── desktop/            # PySide6 Desktop Application
│   ├── assets/         # UI Styles and assets
│   ├── state/          # Application state management
│   ├── ui/             # Windows and widgets
│   ├── workers/        # Background workers (WebSocket client)
│   └── main.py         # Desktop app entry point
├── mobile/             # Flutter Mobile Application
│   ├── lib/            # Dart source code
│   │   ├── services/   # Services (WebSocket, etc.)
│   │   └── main.dart   # Mobile app entry point
│   └── pubspec.yaml    # Flutter dependencies
├── shared/             # Shared constants and schemas (Pydantic)
└── utils/              # Common utilities (Logger, etc.)
```

## 🏁 Getting Started

### Prerequisites
- Python 3.11+
- Flutter SDK (for mobile app)

### Installation (Backend & Desktop)
1. Clone the repository (or navigate to the project directory).
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### 1. Backend
```bash
python -m backend.main
```

#### 2. Desktop Client
```bash
python -m desktop.main
```

#### 3. Mobile Client
Navigate to the `mobile` directory and run:
```bash
cd mobile
flutter run
```

## 🗺️ Roadmap (Phase 2+)
The following features are planned for future integration (dependencies listed in `requirements.txt`):
- **Local LLM Integration**: Ollama
- **Speech to Text**: Faster-Whisper
- **Text to Speech**: Edge-TTS
- **Gesture Control**: Mediapipe
- **Automation**: PyAutoGUI
- **Vector Database (RAG)**: ChromaDB
