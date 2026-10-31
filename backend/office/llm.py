"""Cliente mínimo de la API de chat de Mistral.

El token NUNCA se imprime, se loguea ni se devuelve: solo se lee de la variable
de entorno MISTRAL_API_KEY y se envía como cabecera Authorization.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import httpx

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
DEFAULT_MODEL = "mistral-small-latest"


class LLMError(RuntimeError):
    """Fallo al llamar al modelo (sin red, token inválido, cuota, etc.)."""


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class MistralClient:
    """Cliente async de chat completions. Sin token -> modo None (fallback)."""

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float = 60.0):
        self._api_key = (api_key if api_key is not None else os.environ.get("MISTRAL_API_KEY", "")).strip()
        self.model = (model or os.environ.get("MISTRAL_MODEL", "") or DEFAULT_MODEL).strip()
        self._timeout = timeout

    @property
    def available(self) -> bool:
        return bool(self._api_key)

    async def chat(self, messages: list[ChatMessage]) -> str:
        if not self.available:
            raise LLMError("MISTRAL_API_KEY no configurada")
        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(MISTRAL_API_URL, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise LLMError(f"Error de red llamando a Mistral: {type(exc).__name__}") from exc
        if resp.status_code != 200:
            raise LLMError(f"Mistral devolvió HTTP {resp.status_code}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Respuesta de Mistral con formato inesperado") from exc
