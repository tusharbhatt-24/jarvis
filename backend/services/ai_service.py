"""
JARVIS AI Service (Phase 2 - Ollama Integration)
================================================
Connects to local Ollama instance for real-time AI inference.
Streams tokens back to clients via WebSocket.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

import httpx
from loguru import logger

from shared.constants import WS_CHANNEL_AI, WSEventType
from shared.schemas import AIQueryPayload
from backend.core.config import get_settings


class AIService:
    """
    AI orchestration service connected to Ollama.
    
    Handles:
    - Conversation history management
    - Async HTTP streaming from Ollama API
    - Token-by-token WebSocket broadcasting to specific clients
    """

    def __init__(self, ws_hub):
        self._hub = ws_hub
        self._ai_ready = False
        self._sessions: dict[str, list[dict]] = {}  # session_id → conversation turns
        self.settings = get_settings()
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # Phase 5: Knowledge Service for RAG
        from backend.services.knowledge_service import KnowledgeService
        self.knowledge_service = KnowledgeService()

    async def initialize(self) -> None:
        """Verify connection to Ollama server."""
        logger.info(f"[AIService] Initializing | Host={self.settings.ollama_host}")
        
        try:
            # Check if Ollama is running
            response = await self.client.get(f"{self.settings.ollama_host}/api/tags")
            if response.status_code == 200:
                logger.success("[AIService] Successfully connected to Ollama server")
                self._ai_ready = True
                
                # Check if default model is pulled
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                
                # Check for llama3.2 or equivalent
                target = self.settings.ollama_default_model
                if not any(target in name for name in model_names):
                    logger.warning(f"[AIService] Default model '{target}' not found in Ollama. Available: {model_names}")
                    logger.warning(f"[AIService] Please run `ollama pull {target}` in your terminal.")
                else:
                    logger.info(f"[AIService] Default model '{target}' is available.")
            else:
                logger.error(f"[AIService] Ollama server returned status {response.status_code}")
        except Exception as e:
            logger.error(f"[AIService] Failed to connect to Ollama: {e}")
            logger.error("[AIService] Please ensure Ollama is running on your system.")
            # We still keep it "ready" or handle it gracefully so the app doesn't crash,
            # but queries will fail until Ollama is started.
            self._ai_ready = True # Keep true so we can try to connect on query, or false to block?
            # Let's keep it False if it failed, but allow trying queries. 
            # Actually, let's keep it True to allow the UI to attempt connection later or show errors on query.

    async def process_query(
        self,
        payload: AIQueryPayload,
        client_id: str,
        model: str = None,
    ) -> None:
        """
        Process an AI query using Ollama or ChatGPT and stream tokens back.
        """
        session_id = payload.session_id or str(uuid.uuid4())
        model = model or payload.model or self.settings.ollama_default_model
        
        # Fallback to vision model if images are present and model is text-only
        if payload.images and (model == "llama3.2" or model == "llama3.2:latest"):
            model = "llama3.2-vision"
            
        logger.info(f"[AIService] Query from {client_id} | session={session_id} | model={model}")
        
        # Maintain conversation history
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        # Phase 5: Query Knowledge Base (RAG)
        context_text = ""
        try:
            results = self.knowledge_service.query(payload.text, n_results=2)
            if results and results.get("documents"):
                docs = results["documents"][0]
                if docs:
                    context_text = "\n\n[System: The following context was retrieved from your knowledge base.]\n" + "\n".join(docs)
                    logger.info(f"[AIService] Found {len(docs)} relevant docs in KB")
        except Exception as e:
            logger.error(f"[AIService] KB query failed: {e}")

        user_message = {
            "role": "user",
            "content": payload.text + context_text,
        }
        if payload.images:
            user_message["images"] = payload.images

        self._sessions[session_id].append(user_message)

        # Prepare context (limited by context_turns)
        history = self._sessions[session_id]
        if len(history) > payload.context_turns * 2:
            history = history[-(payload.context_turns * 2):]

        # Prepare Ollama request
        ollama_payload = {
            "model": model,
            "messages": history,
            "stream": True
        }

        assistant_response = ""
        token_count = 0

        try:
            # Connect to Ollama streaming endpoint
            async with self.client.stream(
                "POST", 
                f"{self.settings.ollama_host}/api/chat",
                json=ollama_payload
            ) as response:
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"Ollama error ({response.status_code}): {error_text.decode()}")

                async for line in response.aiter_lines():
                    if not line:
                        continue
                        
                    data = json.loads(line)
                    
                    # Check for completion
                    if data.get("done", False):
                        break
                        
                    # Extract token
                    message = data.get("message", {})
                    token = message.get("content", "")
                    
                    if token:
                        assistant_response += token
                        token_count += 1
                        
                        # Stream to client via WebSocket
                        await self._hub.unicast(client_id, {
                            "type": WSEventType.AI_TOKEN,
                            "channel": WS_CHANNEL_AI,
                            "payload": {
                                "token": token,
                                "session_id": session_id,
                                "done": False,
                            },
                            "timestamp": datetime.utcnow().isoformat(),
                        })

            # Send completion signal
            await self._hub.unicast(client_id, {
                "type": WSEventType.AI_DONE,
                "channel": WS_CHANNEL_AI,
                "payload": {
                    "session_id": session_id,
                    "done": True,
                    "tokens_generated": token_count,
                },
                "timestamp": datetime.utcnow().isoformat(),
            })

            # Store assistant response in history
            self._sessions[session_id].append({
                "role": "assistant",
                "content": assistant_response,
            })
            
            logger.info(f"[AIService] Response complete | session={session_id} | tokens={token_count}")
            return assistant_response

        except Exception as e:
            logger.error(f"[AIService] Error during Ollama generation: {e}")
            
            # Send error to client
            await self._hub.unicast(client_id, {
                "type": WSEventType.AI_ERROR,
                "channel": WS_CHANNEL_AI,
                "payload": {"error": f"Ollama Error: {str(e)}"},
                "timestamp": datetime.utcnow().isoformat(),
            })


    def is_ready(self) -> bool:
        return self._ai_ready

    def get_session_history(self, session_id: str) -> list[dict]:
        return self._sessions.get(session_id, [])

    def clear_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
