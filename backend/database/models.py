"""
JARVIS Backend Database Layer
==============================
SQLAlchemy async models + CRUD operations using aiosqlite.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    Float, Boolean, JSON, select, delete
)
from sqlalchemy.ext.asyncio import (
    AsyncSession, AsyncEngine,
    async_sessionmaker, create_async_engine
)
from sqlalchemy.orm import DeclarativeBase
from loguru import logger

from backend.core.config import get_settings


# ── ORM Base ──────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ── Models ────────────────────────────────────────────────────────────────────

class ConversationSessionModel(Base):
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), unique=True, nullable=False, index=True)
    title = Column(String(255), default="New Conversation")
    model = Column(String(100), default="llama3.2")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConversationTurnModel(Base):
    __tablename__ = "conversation_turns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), nullable=False, index=True)
    role = Column(String(20), nullable=False)   # "user" | "assistant"
    content = Column(Text, nullable=False)
    model = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ActivityLogModel(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class SettingModel(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), unique=True, nullable=False)
    value_json = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Engine & Session ──────────────────────────────────────────────────────────

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker] = None


async def init_database() -> None:
    """Initialize the database engine and create all tables."""
    global _engine, _session_factory
    settings = get_settings()

    _engine = create_async_engine(
        settings.database_url,
        echo=settings.db_echo,
        connect_args={"check_same_thread": False},
    )
    _session_factory = async_sessionmaker(
        _engine, expire_on_commit=False, class_=AsyncSession
    )

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info(f"[Database] Initialized | url={settings.database_url}")


async def get_session() -> AsyncSession:
    """Get a new async database session."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _session_factory()


async def close_database() -> None:
    """Dispose database engine on shutdown."""
    global _engine
    if _engine:
        await _engine.dispose()
        logger.info("[Database] Connection disposed")


# ── CRUD Operations ───────────────────────────────────────────────────────────

class ConversationCRUD:

    @staticmethod
    async def create_session(session_id: str, title: str = "New Conversation", model: str = "llama3.2") -> ConversationSessionModel:
        async with await get_session() as db:
            obj = ConversationSessionModel(session_id=session_id, title=title, model=model)
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            return obj

    @staticmethod
    async def get_sessions(limit: int = 50) -> List[ConversationSessionModel]:
        async with await get_session() as db:
            result = await db.execute(
                select(ConversationSessionModel)
                .order_by(ConversationSessionModel.updated_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    @staticmethod
    async def add_turn(session_id: str, role: str, content: str, model: Optional[str] = None) -> ConversationTurnModel:
        async with await get_session() as db:
            turn = ConversationTurnModel(
                session_id=session_id, role=role,
                content=content, model=model,
            )
            db.add(turn)
            await db.commit()
            await db.refresh(turn)
            return turn

    @staticmethod
    async def get_turns(session_id: str, limit: int = 50) -> List[ConversationTurnModel]:
        async with await get_session() as db:
            result = await db.execute(
                select(ConversationTurnModel)
                .where(ConversationTurnModel.session_id == session_id)
                .order_by(ConversationTurnModel.created_at.asc())
                .limit(limit)
            )
            return list(result.scalars().all())


class ActivityCRUD:

    @staticmethod
    async def log(event_type: str, description: str, metadata: dict | None = None) -> ActivityLogModel:
        async with await get_session() as db:
            entry = ActivityLogModel(
                event_type=event_type,
                description=description,
                metadata_json=json.dumps(metadata or {}),
            )
            db.add(entry)
            await db.commit()
            return entry

    @staticmethod
    async def get_recent(limit: int = 100) -> List[ActivityLogModel]:
        async with await get_session() as db:
            result = await db.execute(
                select(ActivityLogModel)
                .order_by(ActivityLogModel.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())


class SettingsCRUD:

    @staticmethod
    async def get(key: str, default=None):
        async with await get_session() as db:
            result = await db.execute(select(SettingModel).where(SettingModel.key == key))
            row = result.scalar_one_or_none()
            if row:
                return json.loads(row.value_json)
            return default

    @staticmethod
    async def set(key: str, value) -> None:
        async with await get_session() as db:
            result = await db.execute(select(SettingModel).where(SettingModel.key == key))
            existing = result.scalar_one_or_none()
            if existing:
                existing.value_json = json.dumps(value)
                existing.updated_at = datetime.utcnow()
            else:
                db.add(SettingModel(key=key, value_json=json.dumps(value)))
            await db.commit()
