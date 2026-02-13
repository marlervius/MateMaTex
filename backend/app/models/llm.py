"""
Model-agnostic LLM interface.

Supports: Google Gemini, Anthropic Claude, OpenAI GPT, local Ollama models.
Implements automatic fallback: if primary model fails, tries secondary.
"""

from __future__ import annotations

import structlog
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import LLMProviderConfig, get_config

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------
def _create_google(model: str, api_key: str, temperature: float) -> BaseChatModel:
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
        convert_system_message_to_human=True,
    )


def _create_anthropic(model: str, api_key: str, temperature: float) -> BaseChatModel:
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model=model,
        anthropic_api_key=api_key,
        temperature=temperature,
        max_tokens=8192,
    )


def _create_openai(model: str, api_key: str, temperature: float) -> BaseChatModel:
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        temperature=temperature,
    )


def _create_ollama(model: str, base_url: str, temperature: float) -> BaseChatModel:
    from langchain_openai import ChatOpenAI

    # Ollama exposes an OpenAI-compatible API
    return ChatOpenAI(
        model=model,
        base_url=f"{base_url}/v1",
        api_key="ollama",  # Ollama doesn't need a real key
        temperature=temperature,
    )


_PROVIDER_FACTORIES = {
    "google": lambda m, cfg, t: _create_google(m, cfg.google_api_key, t),
    "anthropic": lambda m, cfg, t: _create_anthropic(m, cfg.anthropic_api_key, t),
    "openai": lambda m, cfg, t: _create_openai(m, cfg.openai_api_key, t),
    "ollama": lambda m, cfg, t: _create_ollama(m, cfg.ollama_base_url, t),
}


# ---------------------------------------------------------------------------
# Unified interface
# ---------------------------------------------------------------------------
class LLMInterface:
    """
    Unified LLM interface with automatic fallback.

    Usage:
        llm = LLMInterface(config)
        response = llm.invoke(system_prompt, user_prompt)
    """

    def __init__(
        self,
        config: LLMProviderConfig | None = None,
        *,
        provider: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
    ):
        cfg = config or get_config().llm
        self._config = cfg
        self._temperature = temperature if temperature is not None else cfg.temperature

        # Primary model
        primary_provider = provider or cfg.primary_provider
        primary_model = model or cfg.primary_model
        self._primary = self._build(primary_provider, primary_model)

        # Fallback model (only if different from primary)
        if (
            cfg.fallback_provider != primary_provider
            or cfg.fallback_model != primary_model
        ):
            try:
                self._fallback = self._build(cfg.fallback_provider, cfg.fallback_model)
            except Exception:
                self._fallback = None
        else:
            self._fallback = None

        self._provider_name = primary_provider
        self._model_name = primary_model

    def _build(self, provider: str, model: str) -> BaseChatModel:
        factory = _PROVIDER_FACTORIES.get(provider)
        if factory is None:
            raise ValueError(
                f"Unknown LLM provider: {provider!r}. "
                f"Supported: {', '.join(_PROVIDER_FACTORIES)}"
            )
        return factory(model, self._config, self._temperature)

    @property
    def provider(self) -> str:
        return self._provider_name

    @property
    def model(self) -> str:
        return self._model_name

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send a system+user prompt pair to the LLM. Returns the text response.
        Falls back to secondary model on failure.
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = self._primary.invoke(messages)
            return response.content
        except Exception as primary_err:
            logger.warning(
                "primary_llm_failed",
                provider=self._provider_name,
                model=self._model_name,
                error=str(primary_err),
            )

            if self._fallback is not None:
                try:
                    logger.info("attempting_fallback_llm")
                    response = self._fallback.invoke(messages)
                    return response.content
                except Exception as fallback_err:
                    logger.error(
                        "fallback_llm_failed",
                        error=str(fallback_err),
                    )
                    raise fallback_err from primary_err

            raise primary_err

    async def ainvoke(self, system_prompt: str, user_prompt: str) -> str:
        """Async version of invoke."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = await self._primary.ainvoke(messages)
            return response.content
        except Exception as primary_err:
            if self._fallback is not None:
                try:
                    response = await self._fallback.ainvoke(messages)
                    return response.content
                except Exception as fallback_err:
                    raise fallback_err from primary_err
            raise primary_err


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------
def get_llm(
    *,
    provider: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
) -> LLMInterface:
    """Create an LLM interface with optional overrides."""
    return LLMInterface(
        provider=provider,
        model=model,
        temperature=temperature,
    )
