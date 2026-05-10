"""
config/settings.py
──────────────────
Centralised application configuration using Pydantic-Settings.
Groq API edition — fast, free inference via llama/mixtral models.
Indian market edition — INR currency, NSE/BSE exchanges.

All values are loaded from the .env file. NEVER hardcode secrets here.
"""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Groq API (Free, Fast LLM) ─────────────────────────────────
    groq_api_key: str = Field(..., description="Groq API key from console.groq.com")
    groq_model: str = Field("llama-3.3-70b-versatile", description="Groq model name")
    groq_temperature: float = Field(0.1)
    groq_max_tokens: int = Field(4096)

    # ── Dhan (Free Broker — DhanHQ) ──────────────────────────────
    dhan_client_id: str = Field(default="", description="Dhan Client ID")
    dhan_access_token: str = Field(default="", description="Dhan Access Token")

    # ── Shoonya (Free Broker — Finvasia, optional) ────────────────
    shoonya_user_id: str = Field(default="", description="Shoonya User ID")
    shoonya_password: str = Field(default="", description="Shoonya Password")
    shoonya_vendor_code: str = Field(default="", description="Shoonya Vendor Code")
    shoonya_api_key: str = Field(default="", description="Shoonya API Key")
    shoonya_imei: str = Field(default="", description="Shoonya IMEI / MAC")

    # ── Infrastructure ────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379")
    chroma_persist_dir: str = Field(default="./memory/chroma_db")

    # ── Indian Market Risk Parameters ─────────────────────────────
    max_position_size_pct: float = Field(5.0)
    max_daily_drawdown_pct: float = Field(2.0)
    max_open_positions: int = Field(10)
    min_confidence_score: float = Field(0.65)
    max_volatility_indiavix: float = Field(20.0)
    min_avg_daily_volume: int = Field(500_000)

    # ── Indian Market Settings ────────────────────────────────────
    default_exchange: str = Field(default="NSE")
    default_currency: str = Field(default="INR")
    market_open_time: str = Field(default="09:15")
    market_close_time: str = Field(default="15:30")
    portfolio_value_inr: float = Field(default=1_000_000.0)

    # ── App ───────────────────────────────────────────────────────
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton)."""
    return Settings()


settings = get_settings()
