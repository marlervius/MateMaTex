"""
Async database connection pool for Supabase PostgreSQL.

Usage in routers:
    from app.db import get_db

    @router.get("/items")
    async def list_items(db = Depends(get_db)):
        rows = await db.fetch("SELECT * FROM items WHERE user_id = $1", user_id)
"""

from __future__ import annotations

import ssl as _ssl
from urllib.parse import urlparse, unquote

import asyncpg
import structlog

from app.config import get_settings

logger = structlog.get_logger()

_pool: asyncpg.Pool | None = None


def _parse_database_url(url: str) -> dict:
    """
    Parse a Supabase / PostgreSQL connection string into keyword arguments
    for asyncpg.create_pool().

    We parse manually to avoid issues with:
    - Passwords containing @ or other special characters
    - IPv6 brackets
    - asyncpg not understanding ?sslmode=require
    """
    url = url.strip().strip("'\"")

    # Normalise scheme
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    # Remove jdbc: prefix
    if url.startswith("jdbc:"):
        url = url[5:]

    parsed = urlparse(url)

    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    user = unquote(parsed.username or "postgres")
    password = unquote(parsed.password or "")
    database = (parsed.path or "/postgres").lstrip("/") or "postgres"

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
    }


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

        conn_kwargs = _parse_database_url(settings.database_url)
        logger.info(
            "database_connecting",
            host=conn_kwargs["host"],
            port=conn_kwargs["port"],
            database=conn_kwargs["database"],
            user=conn_kwargs["user"],
        )

        # Create an SSL context for Supabase (requires SSL)
        ssl_ctx = _ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = _ssl.CERT_NONE

        _pool = await asyncpg.create_pool(
            min_size=2,
            max_size=10,
            command_timeout=30,
            ssl=ssl_ctx,
            **conn_kwargs,
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
