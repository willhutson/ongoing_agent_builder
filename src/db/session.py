"""
Database session management for SpokeStack.
Handles connection pooling and async sessions.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator, Optional
import logging
import os

from ..config import get_settings

logger = logging.getLogger(__name__)

# Lazy engine — created on first use, not at import time
_engine = None
_session_factory = None


def get_database_url() -> str:
    """
    Build database URL from settings or environment.
    Supports both sync and async drivers.
    """
    settings = get_settings()

    # Check for explicit database URL first
    db_url = getattr(settings, 'database_url', None) or os.getenv('DATABASE_URL')

    if db_url:
        # Convert postgres:// to postgresql+asyncpg:// for async
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql+asyncpg://', 1)
        elif db_url.startswith('postgresql://') and '+asyncpg' not in db_url:
            db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        return db_url

    # Build from components
    db_host = getattr(settings, 'db_host', None) or os.getenv('DB_HOST', 'localhost')
    db_port = getattr(settings, 'db_port', None) or os.getenv('DB_PORT', '5432')
    db_name = getattr(settings, 'db_name', None) or os.getenv('DB_NAME', 'spokestack')
    db_user = getattr(settings, 'db_user', None) or os.getenv('DB_USER', 'spokestack')
    db_password = getattr(settings, 'db_password', None) or os.getenv('DB_PASSWORD', 'spokestack')

    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_engine():
    """Get or create the async engine (lazy initialization)."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            get_database_url(),
            echo=os.getenv('DB_ECHO', 'false').lower() == 'true',
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
            connect_args={"timeout": 5},
        )
    return _engine


def get_session_factory():
    """Get or create the session factory (lazy initialization)."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes.
    Provides a database session and handles cleanup.

    Usage:
        @router.get("/instances")
        async def list_instances(db: AsyncSession = Depends(get_db)):
            ...
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables.
    Called on application startup.
    """
    from .models import Base

    eng = get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections.
    Called on application shutdown.
    """
    if _engine is not None:
        await _engine.dispose()
