"""
config/llm_client.py
─────────────────────
Centralised factory for Groq LLM client.
Reads credentials from settings (which loads from .env).

Usage:
    from config.llm_client import get_chat_llm
"""
from __future__ import annotations

from langchain_groq import ChatGroq
from config.settings import settings


def get_chat_llm(temperature: float | None = None, max_tokens: int | None = None) -> ChatGroq:
    """
    Return a ChatGroq instance using GROQ_API_KEY and GROQ_MODEL from .env.
    Defaults to llama-3.3-70b-versatile (free, fast, best for reasoning).
    """
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=temperature if temperature is not None else settings.groq_temperature,
        max_tokens=max_tokens if max_tokens is not None else settings.groq_max_tokens,
    )
