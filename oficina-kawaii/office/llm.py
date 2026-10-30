"""Cliente Mistral con reintentos, manejo de errores amigable y modo JSON validado.

La API key se lee solo de la variable de entorno MISTRAL_API_KEY (via .env con
python-dotenv); nunca se escribe en el código.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Sequence

from dotenv import load_dotenv
from mistralai.client import Mistral
from mistralai.client import errors as mistral_errors

DEFAULT_MODEL = "mistral-small-latest"
DEFAULT_TIMEOUT_S = 60
MAX_RETRIES = 3
RETRY_BACKOFF_S = 2.0


class LLMError(RuntimeError):
    """Error amigable de la oficina cuando la llamada a Mistral falla."""

    def __init__(self, mensaje: str, reintentar: bool = True) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.reintentar = reintentar


@dataclass(frozen=True)
class ChatMessage:
    """Mensaje de chat compatible con la API de Mistral."""

    role: str
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


def _load_api_key() -> str:
    load_dotenv()
    key = os.getenv("MISTRAL_API_KEY", "").strip()
    if not key:
        raise LLMError(
            "🐾 Falta la clave MISTRAL_API_KEY. Crea un archivo .env con MISTRAL_API_KEY=tu_clave "
            "(puedes copiar .env.example). Tu pedido quedó guardado para reintentar.",
            reintentar=False,
        )
    return key


class MistralClient:
    """Envoltorio simple sobre el SDK oficial de Mistral."""

    def __init__(self, api_key: str | None = None, timeout: int = DEFAULT_TIMEOUT_S) -> None:
        self._client = Mistral(api_key=api_key or _load_api_key(), timeout=timeout)

    def _complete_once(
        self,
        model: str,
        messages: Sequence[ChatMessage],
        temperature: float,
        json_mode: bool,
    ) -> str:
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": [m.to_dict() for m in messages],
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = self._client.chat.complete(**kwargs)
        content = response.choices[0].message.content
        if isinstance(content, list):
            content = "".join(str(part) for part in content)
        return str(content or "")

    def chat(
        self,
        messages: Sequence[ChatMessage],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> str:
        """Llama al chat con reintentos exponenciales ante errores transitorios.

        Lanza LLMError con mensaje amigable si la llamada falla definitivamente.
        """
        ultimo_error: Exception | None = None
        for intento in range(1, MAX_RETRIES + 1):
            try:
                return self._complete_once(model, messages, temperature, json_mode)
            except mistral_errors.SDKError as exc:
                ultimo_error = exc
                status = getattr(exc, "status_code", None)
                if status in (401, 403):
                    raise LLMError(
                        "🔑 La API de Mistral rechazó la clave (401/403). Revisa tu MISTRAL_API_KEY en .env. "
                        "Tu pedido quedó guardado para reintentar.",
                        reintentar=False,
                    ) from exc
                if status == 429 or (status is not None and 500 <= int(status) < 600):
                    if intento < MAX_RETRIES:
                        time.sleep(RETRY_BACKOFF_S * intento)
                        continue
            except Exception as exc:  # timeouts de red, etc.
                ultimo_error = exc
                if intento < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_S * intento)
                    continue
        raise LLMError(
            f"😿 No pude hablar con Mistral tras {MAX_RETRIES} intentos ({ultimo_error}). "
            "Tu pedido quedó guardado para reintentar con un clic."
        ) from ultimo_error

    def chat_json(
        self,
        messages: Sequence[ChatMessage],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.3,
        fallback: dict | None = None,
    ) -> dict:
        """Llama en modo JSON, valida el resultado y reintenta una vez.

        Si tras el reintento sigue sin ser JSON válido, devuelve `fallback`
        (o un dict vacío) para no perder el pedido del usuario.
        """
        texto = self.chat(messages, model=model, temperature=temperature, json_mode=True)
        try:
            return json.loads(texto)
        except (json.JSONDecodeError, TypeError):
            pass
        texto = self.chat(messages, model=model, temperature=0.0, json_mode=True)
        try:
            parsed = json.loads(texto)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        return fallback if fallback is not None else {}


def simple_chat(prompt: str, model: str = DEFAULT_MODEL, system: str | None = None) -> str:
    """Atajo de una sola llamada; útil para scripts de prueba."""
    messages: list[ChatMessage] = []
    if system:
        messages.append(ChatMessage(role="system", content=system))
    messages.append(ChatMessage(role="user", content=prompt))
    return MistralClient().chat(messages, model=model)
