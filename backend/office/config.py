"""Carga de configuración desde variables de entorno.

El backend es SIN ESTADO: no hay base de datos ni archivos escritos en disco.
Toda la configuración llega por variables de entorno (ver .env.example).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_MAX_AI_CALLS_PER_DAY = 200
DEFAULT_MAX_PROMPT_CHARS = 6000
DEFAULT_MAX_HISTORY_MESSAGES = 30


class MissingConfigError(RuntimeError):
    """Falta una variable de entorno obligatoria."""


@dataclass(frozen=True)
class Settings:
    """Configuración inmutable de la aplicación."""

    mistral_api_key: str
    app_password: str
    max_ai_calls_per_day: int
    max_prompt_chars: int = DEFAULT_MAX_PROMPT_CHARS
    max_history_messages: int = DEFAULT_MAX_HISTORY_MESSAGES


def _require(name: str) -> str:
    """Devuelve el valor de una variable obligatoria o lanza error claro.

    Nunca incluye el valor de la variable en el mensaje de error.
    """
    value = os.environ.get(name, "").strip()
    if not value:
        raise MissingConfigError(
            f"Falta la variable de entorno obligatoria: {name}. "
            "Cópiala desde .env.example y define su valor antes de arrancar."
        )
    return value


def load_settings() -> Settings:
    """Lee y valida la configuración actual del proceso."""
    raw_daily = os.environ.get("MAX_AI_CALLS_PER_DAY", "").strip()
    try:
        daily = int(raw_daily) if raw_daily else DEFAULT_MAX_AI_CALLS_PER_DAY
    except ValueError:
        daily = DEFAULT_MAX_AI_CALLS_PER_DAY
    if daily <= 0:
        daily = DEFAULT_MAX_AI_CALLS_PER_DAY
    return Settings(
        mistral_api_key=_require("MISTRAL_API_KEY"),
        app_password=_require("APP_PASSWORD"),
        max_ai_calls_per_day=daily,
    )
