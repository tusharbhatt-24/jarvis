"""
JARVIS Backend API Routes — WebSocket Endpoint
==============================================
Handles WebSocket connection lifecycle, channel subscriptions,
and message routing to appropriate services.
"""

from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from backend.websocket.hub import ws_hub
from backend.services.ai_service import AIService
from backend.services.voice_service import VoiceService
from shared.constants import WS_CHANNEL_SYSTEM, WS_CHANNEL_AI, WS_CHANNEL_LOGS, WSEventType
from shared.schemas import AIQueryPayload

router = APIRouter(tags=["websocket"])

# Services are injected at startup
_ai_service: AIService | None = None
_voice_service: VoiceService | None = None


def set_services(ai_svc: AIService, voice_svc: VoiceService) -> None:
    """Inject service dependencies (called from main.py on startup)."""
    global _ai_service, _voice_service
    _ai_service = ai_svc
    _voice_service = voice_svc


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint.
    
    Message Protocol:
        Client → Server: { type, channel, payload, ... }
        Server → Client: { type, channel, payload, timestamp, ... }
    
    Supported client message types:
        - subscribe: { channel: "system"|"ai"|"logs"|... }
        - unsubscribe: { channel: "..." }
        - ai_query: { text, model?, session_id? }
        - heartbeat: {} → responds with heartbeat_ack
    """
    client = await ws_hub.connect(websocket)
    client_id = client.client_id

    # Auto-subscribe to system channel
    await ws_hub.subscribe(client_id, WS_CHANNEL_SYSTEM)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning(f"[WS] Invalid JSON from {client_id}")
                continue

            msg_type = msg.get("type", "")
            channel = msg.get("channel", "")
            payload = msg.get("payload", {})

            logger.debug(f"[WS] {client_id} | type={msg_type} | channel={channel}")

            # ── Route message to handler ──────────────────────────────────────
            if msg_type == "subscribe":
                await ws_hub.subscribe(client_id, channel)
                await ws_hub.unicast(client_id, {
                    "type": "subscribed",
                    "channel": channel,
                    "payload": {"status": "ok"},
                    "timestamp": datetime.utcnow().isoformat(),
                })

            elif msg_type == "unsubscribe":
                await ws_hub.unsubscribe(client_id, channel)

            elif msg_type == WSEventType.HEARTBEAT:
                await ws_hub.unicast(client_id, {
                    "type": WSEventType.HEARTBEAT_ACK,
                    "channel": "system",
                    "payload": {"server_time": datetime.utcnow().isoformat()},
                    "timestamp": datetime.utcnow().isoformat(),
                })

            elif msg_type == WSEventType.AI_QUERY:
                if _ai_service and _ai_service.is_ready():
                    query = AIQueryPayload(**payload)
                    selected_model = payload.get("model")
                    # Fire and forget — runs concurrently
                    import asyncio
                    asyncio.create_task(_ai_service.process_query(query, client_id, model=selected_model))
                else:
                    await ws_hub.unicast(client_id, {
                        "type": WSEventType.AI_ERROR,
                        "channel": WS_CHANNEL_AI,
                        "payload": {"error": "AI service not ready"},
                        "timestamp": datetime.utcnow().isoformat(),
                    })

            elif msg_type == "voice_audio":
                if _voice_service and _voice_service.is_stt_ready():
                    audio_base64 = payload.get("audio_base64")
                    if audio_base64:
                        import base64
                        import tempfile
                        import os
                        import asyncio
                        
                        try:
                            audio_data = base64.b64decode(audio_base64)
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                                tmp.write(audio_data)
                                tmp_path = tmp.name
                                
                            text = await _voice_service.transcribe_audio(tmp_path)
                            os.unlink(tmp_path)
                            
                            await ws_hub.unicast(client_id, {
                                "type": "voice_transcription",
                                "channel": "ai",
                                "payload": {"text": text},
                                "timestamp": datetime.utcnow().isoformat(),
                            })
                            
                            if payload.get("auto_trigger_ai", True):
                                if _ai_service and _ai_service.is_ready():
                                    query = AIQueryPayload(text=text, context_turns=10)
                                    selected_model = payload.get("model")
                                    
                                    # Create task to run AI and then generate TTS response
                                    async def run_ai_and_tts():
                                        try:
                                            ai_response = await _ai_service.process_query(query, client_id, model=selected_model)
                                            if ai_response and _voice_service:
                                                import tempfile
                                                import base64
                                                import os
                                                
                                                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                                                    tmp_path = tmp.name
                                                    
                                                success = await _voice_service.generate_speech(ai_response, tmp_path)
                                                
                                                if success:
                                                    with open(tmp_path, "rb") as f:
                                                        audio_base64 = base64.b64encode(f.read()).decode('utf-8')
                                                    os.unlink(tmp_path)
                                                    
                                                    await ws_hub.unicast(client_id, {
                                                        "type": "voice_audio_response",
                                                        "channel": "ai",
                                                        "payload": {"audio_base64": audio_base64},
                                                        "timestamp": datetime.utcnow().isoformat(),
                                                    })
                                        except Exception as e:
                                            logger.error(f"[WS] Error in voice AI/TTS flow: {e}")
                                            
                                    asyncio.create_task(run_ai_and_tts())
                                    
                        except Exception as e:
                            logger.error(f"[WS] Failed to process voice audio: {e}")
                            await ws_hub.unicast(client_id, {
                                "type": "voice_error",
                                "channel": "ai",
                                "payload": {"error": f"Voice processing error: {str(e)}"},
                                "timestamp": datetime.utcnow().isoformat(),
                            })
                else:
                    await ws_hub.unicast(client_id, {
                        "type": "voice_error",
                        "channel": "ai",
                        "payload": {"error": "Voice service not ready"},
                        "timestamp": datetime.utcnow().isoformat(),
                    })

            elif msg_type == "voice_tts":
                if _voice_service:
                    text = payload.get("text")
                    if text:
                        import tempfile
                        import base64
                        import os
                        
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                                tmp_path = tmp.name
                                
                            success = await _voice_service.generate_speech(text, tmp_path)
                            
                            if success:
                                with open(tmp_path, "rb") as f:
                                    audio_base64 = base64.b64encode(f.read()).decode('utf-8')
                                os.unlink(tmp_path)
                                
                                await ws_hub.unicast(client_id, {
                                    "type": "voice_audio_response",
                                    "channel": "ai",
                                    "payload": {"audio_base64": audio_base64},
                                    "timestamp": datetime.utcnow().isoformat(),
                                })
                            else:
                                raise Exception("Failed to generate speech")
                        except Exception as e:
                            logger.error(f"[WS] Failed to generate TTS: {e}")
                            await ws_hub.unicast(client_id, {
                                "type": "voice_error",
                                "channel": "ai",
                                "payload": {"error": f"TTS error: {str(e)}"},
                                "timestamp": datetime.utcnow().isoformat(),
                            })
                else:
                    await ws_hub.unicast(client_id, {
                        "type": "voice_error",
                        "channel": "ai",
                        "payload": {"error": "Voice service not ready"},
                        "timestamp": datetime.utcnow().isoformat(),
                    })

            elif msg_type == "knowledge_add":
                if _ai_service and _ai_service.knowledge_service:
                    text = payload.get("text")
                    import uuid
                    doc_id = payload.get("id") or str(uuid.uuid4())
                    metadata = payload.get("metadata") or {}
                    
                    if text:
                        success = _ai_service.knowledge_service.add_document(doc_id, text, metadata)
                        
                        await ws_hub.unicast(client_id, {
                            "type": "knowledge_added",
                            "channel": "ai",
                            "payload": {"success": success, "id": doc_id},
                            "timestamp": datetime.utcnow().isoformat(),
                        })
                else:
                    await ws_hub.unicast(client_id, {
                        "type": "knowledge_error",
                        "channel": "ai",
                        "payload": {"error": "Knowledge service not ready"},
                        "timestamp": datetime.utcnow().isoformat(),
                    })

            else:
                logger.debug(f"[WS] Unhandled message type: {msg_type}")

    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected cleanly: {client_id}")
    except Exception as e:
        logger.error(f"[WS] Unexpected error for {client_id}: {e}")
    finally:
        await ws_hub.disconnect(client_id)
