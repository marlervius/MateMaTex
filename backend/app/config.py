"""
Application configuration via environment variables.
Uses pydantic-settings for validation and typing.
Supports both local development (.env) and production (Render/Supabase).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Unified application settings."""

    # ---- Database (Supabase) ----
    database_url: str = Field(
        default="",
        description="Supabase PostgreSQL connection string",
    )
    supabase_url: str = Field(
        default="",
        description="Supabase project URL (for auth)",
    )
    supabase_anon_key: str = Field(
        default="",
        description="Supabase anon (public) key",
    )
    supabase_service_role_key: str = Field(
        default="",
        description="Supabase service role key (server-side only)",
    )
    supabase_jwt_secret: str = Field(
        default="",
        description="Supabase JWT secret for token verification",
    )

    # ---- LLM API keys ----
    google_api_key: str = Field(default="", description="Google Gemini API key")
    anthropic_api_key: str = Field(default="", description="Anthropic Claude API key")
    openai_api_key: str = Field(default="", description="OpenAI API key")
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL (local dev only)",
    )

    # ---- LLM defaults ----
    default_model: str = Field(default="gemini-2.0-flash")
    primary_provider: str = Field(default="google")
    primary_model: str = Field(default="gemini-2.0-flash")
    fallback_provider: str = Field(default="google")
    fallback_model: str = Field(default="gemini-2.0-flash")
    temperature: float = Field(default=0.15, ge=0.0, le=2.0)
    max_retries: int = Field(default=3, ge=1, le=10)

    # ---- App ----
    environment: str = Field(
        default="development",
        description="'development' or 'production'",
    )
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    pdflatex_path: str = Field(default="pdflatex")
    output_dir: str = Field(default="output")
    max_verification_retries: int = Field(default=3)

    # ---- CORS ----
    frontend_url: str = Field(
        default="http://localhost:3000",
        description="Frontend URL (overridden in production)",
    )

    # ---- Render ----
    port: int = Field(default=10000)

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()


# Backward-compatible aliases used by existing code
class LLMProviderConfig:
    """Thin wrapper that delegates to Settings for backward compat."""

    def __init__(self) -> None:
        s = get_settings()
        self.primary_provider = s.primary_provider
        self.primary_model = s.primary_model
        self.fallback_provider = s.fallback_provider
        self.fallback_model = s.fallback_model
        self.google_api_key = s.google_api_key
        self.anthropic_api_key = s.anthropic_api_key
        self.openai_api_key = s.openai_api_key
        self.ollama_base_url = s.ollama_base_url
        self.temperature = s.temperature
        self.max_retries = s.max_retries


class AppConfig:
    """Thin wrapper that delegates to Settings for backward compat."""

    def __init__(self) -> None:
        s = get_settings()
        self.debug = s.debug
        self.log_level = s.log_level
        self.pdflatex_path = s.pdflatex_path
        self.output_dir = s.output_dir
        self.max_verification_retries = s.max_verification_retries
        self.llm = LLMProviderConfig()


def get_config() -> AppConfig:
    """Backward-compatible config getter used by existing modules."""
    return AppConfig()
