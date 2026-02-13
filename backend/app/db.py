"""
Async database connection pool for Supabase PostgreSQL.

Usage in routers:
    from app.db import get_db

    @router.get("/items")
    async def list_items(db = Depends(get_db)):
        rows = await db.fetch("SELECT * FROM items WHERE user_id = $1", user_id)
"""

from __future__ import annotations

import asyncpg
import structlog

from app.config import get_settings

logger = structlog.get_logger()

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the connection pool."""
    global _pool
    if _pool is None:
        settings = get_settings()
        if not settings.database_url:
            raise RuntimeError(
                "DATABASE_URL is not set. "
                "Set it to your Supabase connection string."
            )
        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
        logger.info("database_pool_created")
    return _pool


async def get_db():
    """FastAPI dependency — yields a single connection from the pool."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn


async def close_pool() -> None:
    """Close the pool on shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("database_pool_closed")
