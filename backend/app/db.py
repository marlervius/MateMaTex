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

    Handles passwords that contain unescaped @ signs by splitting manually
    on the LAST @ before the host, rather than relying on urlparse which
    splits on the FIRST @.
    """
    import re

    url = url.strip().strip("'\"")

    # Normalise scheme
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("jdbc:"):
        url = url[5:]

    # Remove scheme prefix for manual parsing
    # Format: postgresql://user:password@host:port/database?params
    without_scheme = url.split("://", 1)[1] if "://" in url else url

    # Split on the LAST @ to separate credentials from host
    # This handles passwords containing @ signs
    at_idx = without_scheme.rfind("@")
    if at_idx == -1:
        # No credentials in URL
        credentials = ""
        host_part = without_scheme
    else:
        credentials = without_scheme[:at_idx]
        host_part = without_scheme[at_idx + 1:]

    # Parse credentials (user:password)
    if ":" in credentials:
        user, password = credentials.split(":", 1)
    else:
        user = credentials
        password = ""

    # URL-decode user and password
    user = unquote(user) if user else "postgres"
    password = unquote(password) if password else ""

    # Parse host_part: host:port/database?params
    # Remove query params
    host_part = re.split(r"[?#]", host_part)[0]

    # Split database from host
    if "/" in host_part:
        host_port, database = host_part.split("/", 1)
    else:
        host_port = host_part
        database = "postgres"

    # Split host and port
    # Handle IPv6: [::1]:5432
    if host_port.startswith("["):
        bracket_end = host_port.index("]")
        host = host_port[1:bracket_end]
        port_str = host_port[bracket_end + 2:] if bracket_end + 1 < len(host_port) else ""
    elif ":" in host_port:
        host, port_str = host_port.rsplit(":", 1)
    else:
        host = host_port
        port_str = ""

    port = int(port_str) if port_str else 5432
    database = database or "postgres"

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

        raw_url = settings.database_url
        # Log masked URL for debugging (show scheme, user, host — hide password)
        _masked = raw_url
        if ":" in raw_url and "@" in raw_url:
            # Mask password between first : after :// and last @
            scheme_end = raw_url.find("://")
            if scheme_end != -1:
                after_scheme = raw_url[scheme_end + 3:]
                last_at = after_scheme.rfind("@")
                first_colon = after_scheme.find(":")
                if first_colon != -1 and last_at != -1 and first_colon < last_at:
                    _masked = raw_url[:scheme_end + 3 + first_colon + 1] + "***" + after_scheme[last_at:]
        logger.info("database_raw_url_masked", url=_masked)

        conn_kwargs = _parse_database_url(raw_url)
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
