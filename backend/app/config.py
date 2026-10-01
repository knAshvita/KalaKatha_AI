"""
KalaKatha AI – Application Configuration
Reads all settings from environment variables (via .env file).
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Gemini / ADK ──────────────────────────────────────────────────────────
    gemini_api_key: str = ""
    # Optional pool of multiple keys for automatic quota fallback rotation
    gemini_api_keys: str = ""
    # Model for Google ADK agents (default: gemini-3-flash-preview)
    gemini_model: str = "gemini-3-flash-preview"
    kalakatha_model: str = ""  # alias for backwards compatibility

    # ── API settings ──────────────────────────────────────────────────────────
    app_name: str = "KalaKatha AI"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins for the React frontend
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:5174"

    # ── Upload limits ─────────────────────────────────────────────────────────
    max_upload_size_bytes: int = 10 * 1024 * 1024  # 10 MB

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def model_or_default(self) -> str:
        """Return the configured model, default gemini-3-flash-preview."""
        return self.gemini_model or self.kalakatha_model or "gemini-3-flash-preview"


_CURRENT_KEY_INDEX: int = 0


@lru_cache
def get_settings() -> Settings:
    """Cached singleton – import and call this everywhere you need settings."""
    settings = Settings()

    if settings.gemini_api_key:
        os.environ.setdefault("GOOGLE_API_KEY", settings.gemini_api_key)
        os.environ.setdefault("GEMINI_API_KEY", settings.gemini_api_key)

    return settings


def get_all_api_keys() -> list[str]:
    """Return all available API keys from the configuration pool."""
    settings = get_settings()
    keys: list[str] = []
    if settings.gemini_api_keys:
        for k in settings.gemini_api_keys.split(","):
            cleaned = k.strip()
            if cleaned and cleaned not in keys:
                keys.append(cleaned)
    if settings.gemini_api_key:
        for k in settings.gemini_api_key.split(","):
            cleaned = k.strip()
            if cleaned and cleaned not in keys:
                keys.append(cleaned)
    return keys


def rotate_api_key() -> str | None:
    """Rotate os.environ to the next configured API key if a quota limit is reached."""
    global _CURRENT_KEY_INDEX
    keys = get_all_api_keys()
    if len(keys) <= 1:
        return None
    _CURRENT_KEY_INDEX = (_CURRENT_KEY_INDEX + 1) % len(keys)
    next_key = keys[_CURRENT_KEY_INDEX]
    os.environ["GOOGLE_API_KEY"] = next_key
    os.environ["GEMINI_API_KEY"] = next_key
    return next_key
