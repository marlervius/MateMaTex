"""
Async database connection pool for Supabase PostgreSQL.

Usage in routers:
    from app.db import get_db

    @router.get("/items")
    async def list_items(db = Depends(get_db)):
        rows = await db.fetch("SELECT * FROM items WHERE user_id = $1", user_id)
"""

from __future__ import annotations

import re

import asyncpg
import structlog

from app.config import get_settings

logger = structlog.get_logger()

_pool: asyncpg.Pool | None = None


def _fix_database_url(url: str) -> str:
    """
    Normalise a Supabase / PostgreSQL connection string so asyncpg can parse it.

    Common issues:
    - Supabase gives ``postgresql://…@db.<ref>.supabase.co:5432/postgres``
      but sometimes with ``[IPv6]`` brackets that asyncpg rejects.
    - ``?sslmode=require`` is not understood by asyncpg (it uses ``ssl=True``).
    - Supabase "connection pooler" URLs use port 6543 and may include
      ``?pgbouncer=true`` which asyncpg does not understand.
    """
    # Strip surrounding whitespace / quotes
    url = url.strip().strip("'\"")

    # Replace jdbc: prefix if someone copy-pasted the JDBC URL
    url = re.sub(r"^jdbc:", "", url)

    # Remove IPv6 brackets around the host (asyncpg chokes on them)
    url = re.sub(r"@\[([^\]]+)\]:", r"@\1:", url)

    # asyncpg does not understand sslmode=… — convert to ssl=true
    url = re.sub(r"[?&]sslmode=[^&]*", "", url)

    # Remove pgbouncer param
    url = re.sub(r"[?&]pgbouncer=[^&]*", "", url)

    # Ensure we use postgresql:// (not postgres://)
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    # Clean up dangling ? at the end
    url = url.rstrip("?&")

    return url


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
        dsn = _fix_database_url(settings.database_url)
        logger.info("database_connecting", dsn_host=dsn.split("@")[-1].split("/")[0] if "@" in dsn else "***")
        _pool = await asyncpg.create_pool(
            dsn,
            min_size=2,
            max_size=10,
            command_timeout=30,
            ssl="require",
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
