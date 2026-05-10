"""
JARVIS Backend — Knowledge Service (RAG)
=========================================
Manages document storage and retrieval using ChromaDB.
"""

from __future__ import annotations

import os
import chromadb
from loguru import logger


class KnowledgeService:
    """
    Handles Retrieval-Augmented Generation (RAG) using ChromaDB.
    Allows JARVIS to remember things and read local documents.
    """
    def __init__(self, data_dir: str = "data/chroma"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=self.data_dir)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="jarvis_knowledge"
        )
        logger.info(f"[KnowledgeService] Initialized at {data_dir}")
        
    def add_document(self, doc_id: str, text: str, metadata: dict | None = None) -> bool:
        """Add a document to the vector database."""
        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
            logger.info(f"[KnowledgeService] Added document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"[KnowledgeService] Failed to add document: {e}")
            return False
            
    def query(self, query_text: str, n_results: int = 3) -> dict:
        """Query the database for relevant documents."""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"[KnowledgeService] Query failed: {e}")
            return {}
            
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"[KnowledgeService] Deleted document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"[KnowledgeService] Failed to delete document: {e}")
            return False
